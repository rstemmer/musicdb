# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module organizes the import process of artwork the MusicDB Database.
"""

import logging
from pathlib            import Path
from PIL                import Image
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.fileprocessing import Fileprocessing
from musicdb.mdbapi.database    import MusicDBDatabase
from musicdb.mdbapi.artwork     import MusicDBArtwork
from musicdb.mdbapi.videoframes import VideoFrames
from musicdb.mdbapi.musicdirectory      import MusicDirectory
from musicdb.taskmanagement.taskmanager import TaskManager


class ArtworkManager(TaskManager):
    """
    This class manages importing artwork.
    The class is derived from :class:`musicdb.taskmanagement.taskmanager.TaskManager`.
    
    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: (optional) A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        TaskManager.__init__(self, config, database)

        self.musicdirectory   = MusicDirectory(self.cfg)
        self.artworkdirectory = Filesystem(self.cfg.directories.artwork)
        self.fileprocessing   = Fileprocessing(self.cfg.directories.uploads)
        self.databasemanager  = MusicDBDatabase(config, database)



    def InitiateImport(self, sourcepath, targetpath):
        """
        This method initiates importing an artwork for an album.

        The addresses file can be an image or a music file.
        This file is used to determine the ``"awsourcetype"``.
        The following source types are possible and determined in the described way:

            * ``"imagefile"``: A file that exists in the upload directory
            * ``"songfile"``: A file that exists in the music directory and can be analysed by :meth:`musicdb.mdbapi.musicdirectory.MusicDirectory.AnalysePath`.
            * ``"videofile"``: A file that exists in the music directory and can be analysed by :meth:`musicdb.mdbapi.musicdirectory.MusicDirectory.AnalysePath`.

        The ``sourcepath`` must be a path relative to the music directory or the upload directory.
        If the file does not exist in the music directory, it will then be checked in the upload directory.

        The ``targetpath`` must be a path to an album or a video that already exists in the database.
        It determines if the artwork will be imported for an album or a video.
        The target type is determined by using :meth:`musicdb.mdbapi.musicdirectory.MusicDirectory.AnalysePath`.

        Args:
            sourcepath (str): Path to the artwork that shall be imported.
            targetpath (str): Path relative to the music directory
        
        Returns:
            The task ID as string or ``None`` if something failed.

        Raises:
            TypeError: When one of the parameters are of a wrong data type
            ValueError: When one of the parameters has an unexpected value
        """
        # Check parameters
        if type(sourcepath) != str:
            raise TypeError("Source path must be a string!")

        if type(targetpath) != str:
            raise TypeError("Target path must be a string")

        # Determine source type
        sourcetype = None
        if self.uploaddirectory.IsFile(sourcepath):
            sourcetype = "imagefile"
        elif self.musicdirectory.IsFile(sourcepath):
            fileinfos = self.musicdirectory.AnalysePath(sourcepath)
            if fileinfos and fileinfos["song"]:
                sourcetype = "songfile"
            elif fileinfos and fileinfos["video"]:
                sourcetype = "videofile"

        if not sourcetype:
            raise ValueError("Source path \"%s\" does not address a valid image, song or video file", str(sourcepath))

        # Determine target type
        targettype = None
        fileinfos  = self.musicdirectory.AnalysePath(targetpath)
        if not fileinfos:
            raise ValueError("Invalid target path \"%s\".", str(targetpath))

        if fileinfos["video"] and self.musicdirectory.IsFile(targetpath):
            targettype = "video"
        elif fileinfos["album"] and self.musicdirectory.IsDirectory(targetpath):
            targettype = "album"

        if not targettype:
            raise ValueError("Target path \"%s\" does not address a valid video file or album directory", str(targetpath))


        task = self.CreateNewTask()
        # General Data
        task["state"       ] = "startartworkimport"
        task["contenttype" ] = "artwork"
        task["awsourcetype"] = sourcetype
        task["awsourcepath"] = sourcepath
        if targettype == "album":
            task["albumpath"] = targetpath
        elif targettype == "video":
            task["videopath"] = targetpath

        self.SaveTask(task)
        self.ScheduleTask(task)
        return task["id"]



    def ImportArtwork(self, task):
        """
        This method imports artwork from the upload directory or from an integrated or imported music file.
        Depending on the ``"awsourcetype"`` different import methods are called:

            * ``"videofile"``: :meth:`~ImportVideoArtwork` - Import from video file
            * ``"songfile"``:  :meth:`~ImportAlbumArtwork` - Import from a song file of an album
            * ``"imagefile"``: :meth:`~ImportArtworkFromUpload` - Import from upload directory

        The path to the artwork source must be given in ``"awsourcepath"``.

        If the artwork is being imported for an album or video is determined by the values of ``"videopath"`` or ``"albumpath"``.
        Only one of those values shall be set. The other one must the ``None``.

        The task must be in ``"startartworkimport"`` state, otherwise nothing happens but printing an error message.
        If post processing was successful, the task state gets updated to ``"importcomplete"``.
        When an error occurred, the state will become ``"invalidcontent"`` or ``"importfailed"``.

        Args:
            task (dict): the task object of an import-task

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if task["state"] != "startartworkimport":
            logging.error("The task %s must be in \"startartworkimport\" state for importing. Actual state was \"%s\". \033[1;30m(Such a mistake should not happen. Anyway, the task won\'t be further processed and nothing bad will happen.)", task["id"], task["state"])
            return False

        # Perform artwork import
        self.UpdateTaskState(task, "importingartwork")
        awsourcetype = task["awsourcetype"]
        success = False
        if awsourcetype == "videofile":
            logging.debug("Importing Artwork from Video File: %s", awsourcetype)
            success = self.ImportVideoArtwork(task)
        elif awsourcetype == "songfile":
            logging.debug("Importing Artwork from Song File: %s", awsourcetype)
            success = self.ImportAlbumArtwork(task)
        elif awsourcetype == "imagefile":
            logging.debug("Importing Artwork from Upload Directory: %s", awsourcetype)
            success = self.ImportArtworkFromUpload(task)
        else:
            logging.warning("Unsupported artwork source type: \"%s\" \033[1;30m(Content will be ignored)", str(awsourcetype))
            self.UpdateTaskState(task, "invalidcontent", "Unsupported content type")
            return False

        # Update task state
        if success == True:
            logging.debug("Artwork Import succeeded");
            newstate = "importcomplete"
        else:
            newstate = "importfailed"

        self.UpdateTaskState(task, newstate)
        return success



    def ImportVideoArtwork(self, task):
        """
        Returns:
            ``True`` on success
        """
        logging.error("The Import Video Process needs to be reviewed!") # FIXME
        # Check task state and type
        if task["state"] != "importvideoartwork":
            logging.warning("Cannot import artwork that is not in \"importvideoartwork\" state. Upload with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return False

        if task["contenttype"] != "video":
            logging.warning("Video expected. Actual type of upload: \"%s\" \033[1;30m(No video will be imported)", str(task["contenttype"]))
            return False

        # Start generating the artworks
        videopath    = task["videofile"]
        framemanager = VideoFrames(self.cfg, self.db)

        video = self.db.GetVideoByPath(videopath)
        if not video:
            logging.error("Getting video \"%s\" from database failed. \033[1;30m(Artwork import canceled)", str(videopath), str(e))
            self.NotifyClient("InternalError", task, "Video artwork import failed")
            return False

        retval = framemanager.UpdateVideoFrames(video)
        if retval == False:
            logging.error("Generating video frames and preview failed for video \"%s\". \033[1;30m(Artwork import canceled)", str(videopath))
            self.NotifyClient("InternalError", task, "Video artwork import failed")
            return False

        logging.info("Importing Video thumbnails and previews succeeded")
        return True



    def ImportAlbumArtwork(self, task):
        """
        This method imports an album artwork from one of the songs of the album.

        The following key/value setup must be provided by the ``task``:

            * ``"awsourcetype"``: *Not Used* (Will be determined automatically by :meth:`musicdb.mdbapi.artwork.MusicDBArtwork.UpdateAlbumArtwork`).
            * ``"awsourcepath"``: A path to a song inside the music directory (usually also inside the album directory)
            * ``"albumpath"``: A path relative to the music directory, addressing an album that already exists in the database.

        Returns:
            ``True`` on success
        """
        sourcepath = task["awsourcepath"]
        albumpath  = task["albumpath"]
        
        logging.debug("Importing artwork from \"%s\" for album \"%s\".", sourcepath, albumpath)

        # Get album information
        album = self.db.GetAlbumByPath(albumpath)
        if not album:
            logging.waring("Album with path \"%s\" does not exist in the database! \033[1;30m(Album Artwork Import canceled)")
            self.NotifyClient("InternalError", task, "Album does not exist in the database.")
            return False

        # Import Artwork
        awmanager   = MusicDBArtwork(self.cfg, self.db)
        success     = awmanager.UpdateAlbumArtwork(album)

        # Give feedback
        if not success:
            logging.error("Importing artwork \"%s\" failed. \033[1;30m(Artwork import canceled)", str(sourcepath))
            self.NotifyClient("InternalError", task, "Importing artwork failed")
            return False

        logging.info("Importing artwork for album \"%s\" succeeded", album["name"])
        return True



    def ImportArtworkFromUpload(self, task):
        """
        This method performs the artwork import from an uploaded file.
        It loads the files into the Upload Directory and updates the corresponding music entries.

        The following key/value setup must be provided by the ``task``:

            * ``"awsourcetype"``: Must be ``"imagefile"``
            * ``"awsourcepath"``: A path to a song inside the upload directory
            * ``"albumpath"``: A path relative to the music directory, addressing an album that already exists in the database.

        This method expects that the state of the task is ``"importingartwork"``.

        Args:
            task (dict): The task dictionary

        Returns:
            ``True`` on success.
        """
        sourcepath = task["awsourcepath"]
        albumpath  = task["albumpath"]

        logging.debug("Importing artwork from \"%s\" for album \"%s\".", sourcepath, albumpath)

        # Get album information
        album = self.db.GetAlbumByPath(albumpath)
        if not album:
            logging.waring("Album with path \"%s\" does not exist in the database! \033[1;30m(Album Artwork Import canceled)")
            self.NotifyClient("InternalError", task, "Album does not exist in the database.")
            return False
        artist = self.db.GetArtistById(album["artistid"])

        artistname = artist["name"]
        albumname  = album["name"]
        albumid    = album["id"]

        # Import artwork
        awmanager   = MusicDBArtwork(self.cfg, self.db)
        artworkname = awmanager.CreateArtworkName(artistname, albumname)
        success     = awmanager.SetArtwork(albumid, sourcepath, artworkname)

        if not success:
            logging.error("Importing artwork \"%s\" failed. \033[1;30m(Artwork import canceled)", str(sourcepath))
            self.NotifyClient("InternalError", task, "Importing artwork failed")
            return False

        logging.info("Importing Artwork succeeded")
        return True




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

