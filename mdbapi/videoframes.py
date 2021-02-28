# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
This module handles the thumbnails (frames) and previews (git-animation) of videos.
Its main task is to cache, scale and provide them to the GUI.

.. attention::

    Frame and preview scaling has not been implemented yet.

Definitions
-----------

frame:
    One frame extracted from a music video stored as a picture.

thumbnail:
    One video frame that is used as image to represent the video in the UI.
    File format is JPEG, the file names begin with the prefix ``frame-``.
    In context of HTML ``video``-tags, this thumbnail is used as *poster*

preview:
    A short WebP-animation consisting of several frames of the video.
    This animation will can be played when the cursor hovers above the video.
    The file names begin with the prefix ``preview``.


Database
--------

The thumbnail and preview data is part of the video entry in the MusicDB Database.
The thumbnail and preview part consists of the following entries:

    +-----------------+---------------+-------------+
    | framesdirectory | thumbnailfile | previewfile |
    +-----------------+---------------+-------------+

framesdirectory:
    The path to a frame relative to the thumbnails and previews root directory set in the MusicDB Configuration.
    To access a scaled version of the artwork, the scale as suffix can be used.


Path structure
--------------

The video frames root directory can be configured in the MusicDB Configuration file.
Everything related to video frames takes place in this directory.
To use the artwork inside a web frontend, the HTTPS server needs access to this directory.

Relative to the frames root directory are the frames paths stored in the database.
For each video a sub directory exists.
Source-frames and all scaled frames as well as WebP animations are stored in this sub directory.

The name of the frames directory for a video, consists of the artist name and video name:
``$Artistname/$Videoname``.
This guarantees unique file names that are human readable at the same time.

Inside this sub directory the following files exists:

frame-$i.jpg:
    The source video frames.
    ``$i`` is a continuing number with two digits starting by 1.
    For one video, multiple frames will be extracted.
    The exact number of frames can be defined in the configuration file.
    The file format is JPEG.
    The samples are collected uniform distributed over the video length.

frame-$i ($s×$s).jpg:
    A scaled version of *frame-$i*.
    ``$s`` represents the scaled size that can be configured in the configuration file.
    The separator is a multiplication sign × (U+00D7) to make the name more human readable.
    Multiple scales are possible.
    For example, the name of the 5th frame scaled down to a size of max 100px would be ``frame-5 (100×100).jpg``

preview.webp:
    A preview of the video as animation.
    All source frames available as JPEG are combined to the GIF animation.
    The amount of frames can be configured, as well as the animation length.
    The frames are uniform distributed over the animation length.

preview ($s×$s).webp:
    A scaled version of the preview animation.

The sub directory name for each video gets created by
the method :meth:`~mdbapi.videoframes.VideoFrames.CreateFramesDirectoryName`.
This method replaces "/" by an Unicode division slash (U+2215) to avoid problems with the filesystem.

All new creates files and directories were set to the ownership ``[music]->owner:[music]->group``
and gets the permission ``rw-rw-r--`` (``+x`` for directories)

.. attention::

    Existing frames and previews will not be overwritten.
    In case the settings change, video frames and previews need to be removed manually before recreating them.

HTTPS Server
------------

Web browsers has to prefix the path with ``videoframes/``.
So, the server must be configured.
The resulting path will then be for example ``"videoframes/$framesdirectory/$previewfile"``.


Scaling
--------

Scales that shall be provides are set in the MusicDB Configuration as list of edge-lengths.
For example, to generate 50×27 and 150×83 versions of a frame,
the configuration would look like this: ``scales=50x27, 150x83``
The scaled frames get stored as progressive JPEGs to get a better responsiveness for the WebUI.

Usually videos do not have a ration of 1:1.
If the aspect ration of a frame differs from the desired thumbnail, the borders will be cropped.


Configuration
-------------

An example configuration can look like the following one:

.. code-block:: ini

    [videoframes]
    path=/data/musicdb/videoframes  ; Path to the sub directories for videos
    frames=5                        ; Grab 5 frames from the video
    scales=50x27, 150x83            ; Provide scales of 50px and 150px width with aspect ration of 16/9
    previewlength=3                 ; Create GIF-Animations with 3 second loop length

Under these conditions, a 150×83 pixels preview animation of a video "Sonne" from "Rammstein"
would have the following absolute path:
``/data/musicdb/videoframes/Rammstein/Sonne/preview (150×83).webp``.
Inside the database, this path is stored as ``Rammstein - Sonne``.
Inside the HTML code of the WebUI the following path would be used: ``Rammstein/Sonne/preview (150×83).webp``.


Algorithm
---------

To update the frames cache the following steps are done:

    #. Create a sun directory for the frames via :meth:`~mdbapi.videoframes.VideoFrames.CreateFramesDirectory`
    #. Generate the frames from a video with :meth:`~mdbapi.videoframes.VideoFrames.GenerateFrames`
    #. Generate the previews from the frames with :meth:`~mdbapi.videoframes.VideoFrames.GeneratePreviews`
    #. Update database entry with the directory name in the database via :meth:`~mdbapi.videoframes.VideoFrames.SetVideoFrames`
"""

import os
import stat
from lib.filesystem     import Filesystem
from lib.metatags       import MetaTags
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import *
from PIL                import Image

class VideoFrames(object):
    """
    This class implements the concept described above.
    The most important method is :meth:`~UpdateVideoFrames` that generates all frames and previews for a given video.

    Args:
        config: MusicDB configuration object
        database: MusicDB database

    Raises:
        TypeError: if config or database are not of the correct type
        ValueError: If one of the working-paths set in the config file does not exist
    """
    def __init__(self, config, database):

        if type(config) != MusicDBConfig:
            raise TypeError("Config-class of unknown type")
        if type(database) != MusicDatabase:
            raise TypeError("Database-class of unknown type")

        self.db     = database
        self.cfg    = config
        self.fs     = Filesystem()
        self.musicroot  = Filesystem(self.cfg.music.path)
        self.framesroot = Filesystem(self.cfg.videoframes.path)
        self.metadata   = MetaTags(self.cfg.music.path)
        self.maxframes  = self.cfg.videoframes.frames
        self.previewlength = self.cfg.videoframes.previewlength
        self.scales     = self.cfg.videoframes.scales

        # Check if all paths exist that have to exist
        pathlist = []
        pathlist.append(self.cfg.music.path)
        pathlist.append(self.cfg.videoframes.path)

        for path in pathlist:
            if not self.fs.Exists(path):
                raise ValueError("Path \""+ path +"\" does not exist.")



    def CreateFramesDirectoryName(self, artistname, videoname):
        """
        This method creates the name for a frames directory regarding the following schema:
        ``$Artistname/$Videoname``.
        If there is a ``/`` in the name, it gets replaced by ``∕`` (U+2215, DIVISION SLASH)

        Args:
            artistname (str): Name of an artist
            videoname (str): Name of a video

        Returns:
            valid frames sub directory name for a video
        """
        artistname = artistname.replace("/", "∕")
        videoname  = videoname.replace( "/", "∕")
        dirname    = artistname + "/" + videoname
        return dirname



    def CreateFramesDirectory(self, artistname, videoname):
        """
        This method creates the directory that contains all frames and previews for a video.
        The ownership of the created directory will be the music user and music group set in the configuration file.
        The permissions will be set to ``rwxrwxr-x``.
        If the directory already exists, only the attributes will be updated.

        Args:
            artistname (str): Name of an artist
            videoname (str): Name of a video

        Returns:
            The name of the directory.
        """
        # Determine directory name
        dirname = self.CreateFramesDirectoryName(artistname, videoname)

        # Create directory if it does not yet exist
        if self.framesroot.IsDirectory(dirname):
            logging.debug("Frame directory \"%s\" already exists.", dirname)
        else:
            self.framesroot.CreateSubdirectory(dirname)

        # Set permissions to -rwxrwxr-x
        try:
            self.framesroot.SetAttributes(dirname,
                    self.cfg.music.owner, self.cfg.music.group,
                    stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                    stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
                    stat.S_IROTH |                stat.S_IXOTH )
        except Exception as e:
            logging.warning("Setting frames sub directory attributes failed with error %s. \033[1;30m(Leaving them as they are)", str(e))

        return dirname



    def GenerateFrames(self, dirname, videopath):
        """
        This method creates all frame files, including scaled frames, from a video.
        After generating the frames, animations can be generated via :meth:`~GeneratePreviews`.

        To generate the frames, ``ffmpeg`` is used in the following way:

        .. code-block:: bash

            ffmpeg -ss $time -i $videopath -vf scale=iw*sar:ih -vframes 1 $videoframes/$dirname/frame-xx.jpg

        ``videopath`` and ``dirname`` are the parameters of this method.
        ``videoframes`` is the root directory for the video frames as configured in the MusicDB Configuration file.
        ``time`` is a moment in time in the video at which the frame gets selected.
        This value gets calculated depending of the videos length and amount of frames that shall be generated.
        The file name of the frames will be ``frame-xx.jpg`` where ``xx`` represents the frame number.
        The number is decimal, has two digits and starts with 01.

        The scale solves the differences between the Display Aspect Ratio (DAR) and the Sample Aspect Ratio (SAR).
        By using a scale of image width multiplied by the SAR, the resulting frame has the same ratio as the video in the video player.

        The total length of the video gets determined by :meth:`~lib.metatags.MetaTags.GetPlaytime`

        When there are already frames existing, nothing will be done.
        This implies that it is mandatory to remove existing frames manually when there are changes in the configuration.
        For example when increasing or decreasing the amount of frames to consider for the animation.
        The method will return ``True`` in this case, because there are frames existing.

        Args:
            dirname (str): Name/Path of the directory to store the generated frames
            videopath (str): Path to the video that gets processed

        Returns:
            ``True`` on success, otherwise ``False``
        """
        # Determine length of the video in seconds
        try:
            self.metadata.Load(videopath)
            videolength = self.metadata.GetPlaytime()
        except Exception as e:
            logging.exception("Generating frames for video \"%s\" failed with error: %s", videopath, str(e))
            return False

        slicelength = videolength / (self.maxframes+1)
        sliceoffset = slicelength / 2

        for framenumber in range(self.maxframes):
            # Calculate time point of the frame in seconds
            #moment = (videolength / self.maxframes) * framenumber
            moment = sliceoffset + slicelength * framenumber

            # Define destination path
            framename = "frame-%02d.jpg"%(framenumber+1)
            framepath = dirname + "/" + framename

            # Only create frame if it does not yet exist
            if not self.framesroot.Exists(framepath):
                # create absolute paths for FFMPEG
                absframepath = self.framesroot.AbsolutePath(framepath)
                absvideopath = self.musicroot.AbsolutePath(videopath)

                # Run FFMPEG - use absolute paths
                process = ["ffmpeg",
                        "-ss",      str(moment),
                        "-i",       absvideopath,
                        "-vf",      "scale=iw*sar:ih",   # Make sure the aspect ration is correct
                        "-vframes", "1",
                        absframepath]
                logging.debug("Getting frame via %s", str(process))
                try:
                    self.fs.Execute(process)
                except Exception as e:
                    logging.exception("Generating frame for video \"%s\" failed with error: %s", videopath, str(e))
                    return False

            # Scale down the frame
            self.ScaleFrame(dirname, framenumber+1)

        return True



    def ScaleFrame(self, dirname, framenumber):
        """
        This method creates a scaled version of the existing frames for a video.
        The aspect ration of the frame will be maintained.
        In case the resulting aspect ratio differs from the source file,
        the borders of the source frame will be cropped in the scaled version.

        If a scaled version exist, it will be skipped.

        The scaled JPEG will be stored with optimized and progressive settings.

        Args:
            dirname (str): Name of the directory where the frames are stored at (relative)
            framenumber (int): Number of the frame that will be scaled

        Returns:
            *Nothing*
        """
        sourcename    = "frame-%02d.jpg"%(framenumber)
        sourcepath    = dirname + "/" + sourcename 
        abssourcepath = self.framesroot.AbsolutePath(sourcepath)

        for scale in self.scales:
            width, height   = map(int, scale.split("x"))
            scaledframename = "frame-%02d (%d×%d).jpg"%(framenumber, width, height)
            scaledframepath = dirname + "/" + scaledframename
            
            # In case the scaled version already exists, nothing will be done
            if self.framesroot.Exists(scaledframepath):
                continue

            absscaledframepath = self.framesroot.AbsolutePath(scaledframepath)

            size  = (width, height)
            frame = Image.open(abssourcepath)
            frame.thumbnail(size, Image.BICUBIC)
            frame.save(absscaledframepath, "JPEG", optimize=True, progressive=True)
        return



    def GeneratePreviews(self, dirname):
        """
        This method creates all preview animations (.webp), including scaled versions, from frames.
        The frames can be generated via :meth:`~GenerateFrames`.

        In case there is already a preview file, the method returns ``True`` without doing anything.

        Args:
            dirname (str): Name/Path of the directory to store the generated frames

        Returns:
            ``True`` on success, otherwise ``False``
        """
        # Create original sized preview
        framepaths = []
        for framenumber in range(self.maxframes):
            framename = "frame-%02d.jpg"%(framenumber+1)
            framepath = dirname + "/" + framename
            framepaths.append(framepath)
        previewpath = dirname + "/preview.webp"

        success  = True
        success &= self.CreateAnimation(framepaths, previewpath)

        # Create scaled down previews
        for scale in self.scales:
            framepaths    = []
            width, height = map(int, scale.split("x"))

            for framenumber in range(self.maxframes):
                scaledframename = "frame-%02d (%d×%d).jpg"%(framenumber+1, width, height)
                scaledframepath = dirname + "/" + scaledframename
                framepaths.append(scaledframepath)

            previewpath = dirname + "/preview (%d×%d).webp"%(width, height)
            success    &= self.CreateAnimation(framepaths, previewpath)

        return success



    def CreateAnimation(self, framepaths, animationpath):
        """
        This method creates a WebP animation from frames that are addresses by a sorted list of paths.
        Frame paths that do not exists or cannot be opened will be ignored.
        If there already exists an animation addressed by animation path, nothing will be done.

        The list of frame paths must at least contain 2 entries.

        Args:
            framepaths (list(str)): A list of relative frame paths that will be used to create an animation
            animationpath (str): A relative path where the animation shall be stored at.

        Returns:
            ``True`` when an animation has been created or exists, otherwise ``False``
        """
        if self.framesroot.IsFile(animationpath):
            logging.debug("There is already an animation \"%s\" (Skipping frame generation process)", animationpath)
            return True

        # Load all frames
        frames = []
        for framepath in framepaths:
            absframepath = self.framesroot.AbsolutePath(framepath)

            try:
                frame = Image.open(absframepath)
            except FileNotFoundError as e:
                logging.warning("Unable to load frame \"$s\": %s \033[1;30m(Frame will be ignored)", absframepath, str(e))
                continue

            frames.append(frame)

        # Check if enough frames for a preview have been loaded
        if len(frames) < 2:
            logging.error("Not enough frames were loaded. Cannot create a preview animation. \033[1;30m(%d < 2)", len(frames))
            return False

        # Create absolute animation file path
        absanimationpath = self.framesroot.AbsolutePath(animationpath)

        # Calculate time for each frame in ms being visible
        duration = int((self.previewlength * 1000) / self.maxframes)

        # Store as WebP animation
        preview = frames[0]                 # Start with frame 0
        preview.save(absanimationpath, 
                save_all=True,              # Save all frames
                append_images=frames[1:],   # Save these frames
                duration=duration,          # Display time for each frame
                loop=0,                     # Show in infinite loop
                method=6)                   # Slower but better method [1]

        # [1] https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp

        return True



    def SetVideoFrames(self, videoid, framesdir, thumbnailfile=None, previewfile=None):
        """
        Set Database entry for the video with video ID ``videoid``.
        Using this method defines the frames directory to which all further paths are relative to.
        The thumbnail file addresses a static source frame (like ``frame-01.jpg``),
        the preview file addresses the preview animation (usually ``preview.webp``).

        If ``thumbnailfile`` or ``previewfile`` is ``None``, it will not be changed in the database.

        This method checks if the files exists.
        If not, ``False`` gets returned an *no* changes will be done in the database.

        Example:

            .. code-block:: python

                retval = vf.SetVideoFrames(1000, "Fleshgod Apocalypse/Monnalisa", "frame-02.jpg", "preview.webp")
                if retval == False:
                    print("Updating video entry failed.")

        Args:
            videoid (int): ID of the video that database entry shall be updated
            framesdir (str): Path of the video specific sub directory containing all frames/preview files. Relative to the video frames root directory
            thumbnailfile (str, NoneType): File name of the frame that shall be used as thumbnail, relative to ``framesdir``
            previewfile (str, NoneType): File name of the preview animation, relative to ``framesdir``

        Returns:
            ``True`` on success, otherwise ``False``
        """
        # Check if all files are valid
        if not self.framesroot.IsDirectory(framesdir):
            logging.error("The frames directory \"%s\" does not exist in the video frames root directory.", framesdir)
            return False

        if thumbnailfile and not self.framesroot.IsFile(framesdir + "/" + thumbnailfile):
            logging.error("The thumbnail file \"%s\" does not exits in the frames directory \"%s\".", thumbnailfile, framesdir)
            return False

        if previewfile and not self.framesroot.IsFile(framesdir + "/" + previewfile):
            logging.error("The preview file \"%s\" does not exits in the frames directory \"%s\".", previewfile, framesdir)
            return False

        # Change paths in the database
        retval = self.db.SetVideoFrames(videoid, framesdir, thumbnailfile, previewfile)

        return retval



    def UpdateVideoFrames(self, video):
        """
        #. Create frames directory (:meth:`~CreateFramesDirectory`)
        #. Generate frames (:meth:`~GenerateFrames`)
        #. Generate previews (:meth:`~GeneratePreviews`)

        Args:
            video: Database entry for the video for that the frames and preview animation shall be updated

        Returns:
            ``True`` on success, otherwise ``False``
        """
        logging.info("Updating frames and previews for %s", video["path"])

        artist     = self.db.GetArtistById(video["artistid"])
        artistname = artist["name"]
        videopath  = video["path"]
        videoname  = video["name"]
        videoid    = video["id"]

        # Prepare everything to start generating frames and previews
        framesdir  = self.CreateFramesDirectory(artistname, videoname)

        # Generate Frames
        retval = self.GenerateFrames(framesdir, videopath)
        if retval == False:
            return False

        # Generate Preview
        retval = self.GeneratePreviews(framesdir)
        if retval == False:
            return False

        # Update database
        retval = self.SetVideoFrames(videoid, framesdir, "frame-01.jpg", "preview.webp")
        return retval



    def ChangeThumbnail(self, video, timestamp):
        """
        This method creates a thumbnail image files, including scaled a version, from a video.
        The image will be generated from a frame addressed by the ``timestamp`` argument.

        To generate the thumbnail, ``ffmpeg`` is used in the following way:

        .. code-block:: bash

            ffmpeg -y -ss $timestamp -i $video["path"] -vf scale=iw*sar:ih -vframes 1 $videoframes/$video["framesdirectory"]/thumbnail.jpg

        ``video`` and ``timestamp`` are the parameters of this method.
        ``videoframes`` is the root directory for the video frames as configured in the MusicDB Configuration file.

        The scale solves the differences between the Display Aspect Ratio (DAR) and the Sample Aspect Ratio (SAR).
        By using a scale of image width multiplied by the SAR, the resulting frame has the same ratio as the video in the video player.

        The total length of the video gets determined by :meth:`~lib.metatags.MetaTags.GetPlaytime`
        If the time stamp is not between 0 and the total length, the method returns ``False`` and does nothing.

        When there is already a thumbnail existing it will be overwritten.

        Args:
            video: A video entry that shall be updated
            timestamp (int): Time stamp of the frame to select in seconds

        Returns:
            ``True`` on success, otherwise ``False``
        """

        dirname   = video["framesdirectory"]
        videopath = video["path"]
        videoid   = video["id"]

        # Determine length of the video in seconds
        try:
            self.metadata.Load(videopath)
            videolength = self.metadata.GetPlaytime()
        except Exception as e:
            logging.exception("Generating a thumbnail for video \"%s\" failed with error: %s", videopath, str(e))
            return False

        if timestamp < 0:
            logging.warning("Generating a thumbnail for video \"%s\" requires a time stamp > 0. Given was: %s", videopath, str(timestamp))
            return False

        if timestamp > videolength:
            logging.warning("Generating a thumbnail for video \"%s\" requires a time stamp smaller than the video play time (%s). Given was: %s", videopath, str(videolength), str(timestamp))
            return False


        # Define destination path
        framename = "thumbnail.jpg"
        framepath = dirname + "/" + framename

        # create absolute paths for FFMPEG
        absframepath = self.framesroot.AbsolutePath(framepath)
        absvideopath = self.musicroot.AbsolutePath(videopath)

        # Run FFMPEG - use absolute paths
        process = ["ffmpeg",
                "-y",                           # Yes, overwrite existing frame
                "-ss",      str(timestamp),
                "-i",       absvideopath,
                "-vf",      "scale=iw*sar:ih",  # Make sure the aspect ration is correct
                "-vframes", "1",
                absframepath]
        logging.debug("Getting thumbnail via %s", str(process))
        try:
            self.fs.Execute(process)
        except Exception as e:
            logging.exception("Generating a thumbnail for video \"%s\" failed with error: %s", videopath, str(e))
            return False

        # Scale down the frame
        self.ScaleThumbnail(dirname)

        # Set new Thumbnail
        retval = self.SetVideoFrames(videoid, dirname, thumbnailfile="thumbnail.jpg", previewfile=None)
        if not retval:
            return False

        return True



    def ScaleThumbnail(self, dirname):
        """
        This method creates a scaled version of the existing thumbnail for a video.
        The aspect ration of the frame will be maintained.
        In case the resulting aspect ratio differs from the source file,
        the borders of the source frame will be cropped in the scaled version.

        If a scaled version exist, it will be overwritten.

        The scaled JPEG will be stored with optimized and progressive settings.

        Args:
            dirname (str): Name of the directory where the frames are stored at (relative)

        Returns:
            *Nothing*
        """
        sourcename    = "thumbnail.jpg"
        sourcepath    = dirname + "/" + sourcename 
        abssourcepath = self.framesroot.AbsolutePath(sourcepath)

        for scale in self.scales:
            width, height   = map(int, scale.split("x"))
            scaledframename = "thumbnail (%d×%d).jpg"%(width, height)
            scaledframepath = dirname + "/" + scaledframename
            
            absscaledframepath = self.framesroot.AbsolutePath(scaledframepath)

            size  = (width, height)
            frame = Image.open(abssourcepath)
            frame.thumbnail(size, Image.BICUBIC)
            frame.save(absscaledframepath, "JPEG", optimize=True, progressive=True)
        return

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

