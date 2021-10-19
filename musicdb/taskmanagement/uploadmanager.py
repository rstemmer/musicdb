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
"""

import json
import time
import logging
import datetime
import threading
from pathlib            import Path
from PIL                import Image
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.fileprocessing import Fileprocessing
from musicdb.lib.metatags       import MetaTags
from musicdb.mdbapi.database    import MusicDBDatabase
from musicdb.mdbapi.artwork     import MusicDBArtwork
from musicdb.mdbapi.videoframes import VideoFrames
from musicdb.mdbapi.musicdirectory      import MusicDirectory
from musicdb.taskmanagement.taskmanager import TaskManager


class UploadManager(TaskManager):
    """
    This class manages uploading content to the server MusicDB runs on.
    All data is stored in the uploads-directory configured in the MusicDB configuration.
    The class is derived from :class:`musicdb.taskmanagement.taskmanager.TaskManager`.
    
    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: (optional) A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        TaskManager.__init__(self, config, database)

        self.musicfs    = MusicDirectory(self.cfg)
        self.artworkfs  = Filesystem(self.cfg.directories.artwork)
        # TODO: check write permission of all directories
        self.fileprocessing = Fileprocessing(self.cfg.directories.uploads)
        self.dbmanager  = MusicDBDatabase(config, database)



    #####################################################################
    # Management Functions                                              #
    #####################################################################



    def InitiateUpload(self, uploadid, mimetype, contenttype, filesize, checksum, sourcefilename):
        """
        Initiates an upload of a file into a MusicDB managed file space.
        After calling this method, a notification gets triggered to request the first chunk of data from the clients.
        In case uploads are deactivated in the MusicDB Configuration, an ``"InternalError"`` Notification gets sent to the clients.

        Args:
            uploadid (str): Unique ID to identify the upload task 
            mimetype (str): MIME-Type of the file (example: ``"image/png"``)
            contenttype (str): Type of the content: (``"video"``, ``"album"``, ``"artwork"``)
            filesize (int): Size of the complete file in bytes
            checksum (str): SHA-1 check sum of the source file
            sourcefilename (str): File name (example: ``"test.png"``)

        Raises:
            TypeError: When one of the arguments has not the expected type
            ValueError: When *contenttype* does not have the expected values
        """
        self.InitiateProcess(uploadid, mimetype, contenttype, filesize, checksum, sourcefilename, "waitforchunk")
        return



    def RequestRemoveUpload(self, uploadid):
        """
        This method triggers removing a specific upload.
        This includes the uploaded file as well as the upload task information and annotations.

        The upload task can be in any state.
        When the remove-operation is triggered, its state gets changed to ``"remove"``.

        Only the ``"remove"`` state gets set. Removing will be done by the Management Thread.

        Args:
            uploadid (str): ID of the upload-task

        Returns:
            ``True`` on success
        """
        try:
            task = self.GetTaskByID(uploadid)
        except Exception as e:
            logging.error("Internal error while requesting a new chunk of data: %s", str(e))
            return False

        self.UpdateTaskState(task, "remove")
        return True



    def NewChunk(self, uploadid, rawdata):
        """
        This method processes a new chunk received from the uploading client.

        Args:
            uploadid (str): Unique ID to identify the upload task
            rawdata (bytes): Raw data to append to the uploaded data

        Returns:
            ``False`` in case an error occurs. Otherwise ``True``.

        Raises:
            TypeError: When *rawdata* is not of type ``bytes``
        """
        if type(rawdata) != bytes:
            raise TypeError("raw data must be of type bytes. Type was \"%s\""%(str(type(rawdata))))

        try:
            task = self.GetTaskByID(uploadid)
        except Exception as e:
            logging.error("Internal error while requesting a new chunk of data: %s", str(e))
            return False

        chunksize = len(rawdata)
        filepath  = task["uploadpath"]

        try:
            with open(filepath, "ab") as fd:
                fd.write(rawdata)
        except Exception as e:
            logging.warning("Writing chunk of uploaded data into \"%s\" failed: %s \033[1;30m(Upload canceled)", filepath, str(e))
            self.UpdateTaskState(task, "uploadfailed", "Writing data failed with error: \"%s\""%(str(e)))
            return False

        task["offset"] += chunksize
        self.SaveTask(task)

        if task["offset"] >= task["filesize"]:
            # Upload complete
            self.UploadCompleted(task)
        else:
            # Get next chunk of data
            self.NotifyClient("ChunkRequest", task)
        return True



    def UploadCompleted(self, task):
        """
        This method continues the file management after an upload was completed.
        The following tasks were performed:

            * Checking the checksum of the destination file (SHA1) and compares it with the ``"sourcechecksum"`` from the *task*-dict.

        When the upload was successful, it notifies the clients with a ``"UploadComplete"`` notification.
        Otherwise with a ``"UploadFailed"`` one.

        Args:
            task (dict): The task that upload was completed

        Returns:
            ``True`` When the upload was successfully complete, otherwise ``False``
        """
        # Check checksum
        destchecksum = self.fileprocessing.Checksum(task["uploadpath"], "sha1")
        if destchecksum != task["sourcechecksum"]:
            logging.error("Upload Failed: \033[0;36m%s \e[1;30m(Checksum mismatch)", task["uploadpath"]);
            self.UpdateTaskState(task, "uploadfailed", "Checksum mismatch")
            return False

        logging.info("Upload Complete: \033[0;36m%s", task["uploadpath"]);
        self.UpdateTaskState(task, "uploadcomplete")
        # Now, the Management Thread takes care about post processing or removing no longer needed content
        return True



    def PreProcessUploadedFile(self, task):
        """
        This method initiates pre-processing of an uploaded file.
        Depending on the *contenttype* different post processing methods are called:

            * ``"video"``: :meth:`~PreProcessVideo`
            * ``"artwork"``: :meth:`~PreProcessArtwork`

        The task must be in ``"uploadcomplete"`` state, otherwise nothing happens but printing an error message.
        If post processing was successful, the task state gets updated to ``"preprocessed"``.
        When an error occurred, the state will become ``"invalidcontent"``.

        Args:
            task (dict): the task object of an upload-task

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if task["state"] != "uploadcomplete":
            logging.error("task must be in \"uploadcomplete\" state for post processing. Actual state was \"%s\". \033[1;30m(Such a mistake should not happen. Anyway, the task won\'t be post process and nothing bad will happen.)", task["state"])
            return False

        # Perform post processing
        logging.debug("Preprocessing upload %s -> %s", str(task["sourcefilename"]), str(task["uploadpath"]))
        success = False
        if task["contenttype"] == "video":
            success = self.PreProcessVideo(task)
        elif task["contenttype"] == "artwork":
            success = self.PreProcessArtwork(task)
        else:
            logging.warning("Unsupported content type of upload: \"%s\" \033[1;30m(Upload will be ignored)", str(task["contenttype"]))
            self.UpdateTaskState(task, "invalidcontent", "Unsupported content type")
            return False

        # Update task state
        if success == True:
            newstate = "preprocessed"
        else:
            newstate = "invalidcontent"

        self.UpdateTaskState(task, newstate)
        return success



    def PreProcessVideo(self, task):
        """

        Args:
            task (dict): the task object of an upload-task
        """
        meta = MetaTags()
        try:
            meta.Load(task["uploadpath"])
        except ValueError:
            logging.error("The file \"%s\" uploaded as video to %s is not a valid video or the file format is not supported. \033[1;30m(File will be not further processed.)", task["sourcefilename"], task["uploadpath"])
            return False

        # Get all meta infos (for videos, this does not include any interesting information.
        # Maybe the only useful part is the Load-method to check if the file is supported by MusicDB
        #tags = meta.GetAllMetadata()
        #logging.debug(tags)
        return True



    def PreProcessArtwork(self, task):
        """

        Args:
            task (dict): the task object of an upload-task
        """
        origfile = task["uploadpath"]
        extension= self.uploaddirectory.GetFileExtension(origfile)
        jpegfile = origfile[:-len(extension)] + "jpg"
        if extension != "jpg":
            logging.debug("Transcoding artwork file form %s (\"%s\") to JPEG (\"%s\")", extension, origfile, jpegfile);
            im = Image.open(origfile)
            im = im.convert("RGB")
            im.save(jpegfile, "JPEG", optimize=True, progressive=True)

        task["preprocessedpath"] = jpegfile
        return True



    def AnnotateUpload(self, uploadid, annotations):
        """
        This method can be used to add additional information to an upload.
        This can be done during or after the upload process.

        Args:
            uploadid (str): ID to identify the upload

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            TypeError: When *uploadid* is not of type ``str``
            ValueError: When *uploadid* is not included in the Task Queue
        """
        try:
            task = self.GetTaskByID(uploadid)
        except Exception as e:
            logging.error("Internal error while requesting a new chunk of data: %s", str(e))
            return False

        for key, item in annotations.items():
            task["annotations"][key] = item

        self.SaveTask(task)
        self.NotifyClient("StateUpdate", task)
        return True



    def IntegrateUploadedFile(self, uploadid, triggerimport):
        """
        This method integrated the uploaded files into the music directory.
        The whole file tree will be created following the MusicDB naming scheme.

        The upload task must be in ``preprocesses`` state. If not, nothing happens.

        When *triggerimport* is ``true``, the upload manager start importing the music.
        This happens asynchronously inside the Upload Manager Thread.

        Args:
            uploadid (str): ID to identify the upload

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            TypeError: When *uploadid* is not of type ``str``
            ValueError: When *uploadid* is not included in the Task Queue
        """
        try:
            task = self.GetTaskByID(uploadid)
        except Exception as e:
            logging.error("Internal error while requesting a new chunk of data: %s", str(e))
            return False

        if task["state"] != "preprocessed":
            logging.warning("Cannot integrate an upload that is not in \"preprocessed\" state. Upload with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return

        # Perform post processing
        success = False
        if task["contenttype"] == "video":
            success = self.IntegrateVideo(task)
        elif task["contenttype"] == "artwork":
            success = True # Importing artwork does not require the file at any specific place
        else:
            logging.warning("Unsupported content type of upload: \"%s\" \033[1;30m(Upload will be ignored)", str(task["contenttype"]))
            self.UpdateTaskState(task, "integrationfailed", "Unsupported content type")
            return

        # Update task state
        if success == True:
            newstate = "integrated"
        else:
            newstate = "integrationfailed"
        self.UpdateTaskState(task, newstate)

        # Trigger import
        if success == False or triggerimport == False:
            return  # … but only if wanted, and previous step was successful

        self.UpdateTaskState(task, "startimport") # The upload management thread will do the rest
        return



    def IntegrateVideo(self, task):
        """
        When an annotation needed for creating the video file path in the music directory is missing, ``False`` gets returned and an error message written into the log
        """
        uploadedfile  = task["uploadpath"]    # uploaded file
        try:
            artistname    = task["annotations"]["artistname"]
            releasedate   = task["annotations"]["release"]
            videoname     = task["annotations"]["name"]
        except KeyError as e:
            logging.error("Collection video information for creating its path name failed with key-error for: %s \033[1;30m(Make sure all important annotations are given to that upload: name, artistname, release)", str(e))
            return False

        fileextension = self.uploaddirectory.GetFileExtension(uploadedfile)
        videofile     = artistname + "/" + releasedate + " - " + videoname + "." + fileextension

        task["videofile"] = videofile
        logging.debug("Integrating upload %s -> %s", str(uploadedfile), str(videofile))

        # Check if video file already exists
        if self.musicfs.Exists(videofile):
            logging.warning("File \"%s\" already exists in the music directory! \033[1;30m(It will NOT be overwritten)", str(videofile))
            self.NotifyClient("InternalError", task, "File already exists in the music directory")
            return False

        # Check if artist directory exists
        if not self.musicfs.IsDirectory(artistname):
            logging.info("Artist directory for \"%s\" does not exist and will be created.", str(artistname))
            try:
                self.musicfs.CreateSubdirectory(artistname)
            except PermissionError:
                logging.error("Creating artist sub-directory \"%s\" failed! - Permission denied! \033[1;30m(MusicDB requires write permission to the music file tree)", str(artistname))
                self.NotifyClient("InternalError", task, "Creating artist directory failed - Permission denied")
                return False

        # Copy file, create Artist directory if not existing
        try:
            success = self.musicfs.CopyFile(uploadedfile, videofile)
        except PermissionError:
            logging.error("Copying video file to \"%s\" failed! - Permission denied! \033[1;30m(MusicDB requires write permission to the music file tree)", str(videofile))
            self.NotifyClient("InternalError", task, "Copying failed - Permission denied")
            return False

        if(success):
            logging.info("New video file at %s", str(videofile))
        else:
            logging.warning("Copying video file to \"%s\" failed!", str(videofile))
        return success



    def ImportVideo(self, task):
        """
        Task state must be ``"startimport"`` and content type must be ``"video"``

        Returns:
            ``True`` on success.
        """
        # Check task state and type
        if task["state"] != "startimport":
            logging.warning("Cannot import an upload that is not in \"startimport\" state. Upload with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return False

        success = False
        if task["contenttype"] != "video":
            logging.warning("Video expected. Actual type of upload: \"%s\" \033[1;30m(No video will be imported)", str(task["contenttype"]))
            return False

        # Get important information
        try:
            artistname = task["annotations"]["artistname"]
            videopath  = task["videofile"]
        except KeyError as e:
            logging.error("Collecting video information for importing failed with key-error for: %s \033[1;30m(Make sure the artist name is annotated to the upload)", str(e))
            return False

        # Check if the artist already exists in the database - if not, add it
        artist = self.db.GetArtistByPath(artistname)
        if artist == None:
            logging.info("Importing new artist: \"%s\"", artistname)
            try:
                self.dbmanager.AddArtist(artistname)
            except Exception as e:
                logging.error("Importing artist \"%s\" failed with error: %s \033[1;30m(Video upload canceled)", str(artistname), str(e))
                self.NotifyClient("InternalError", task, "Importing artist failed")
                return False
            artist = self.db.GetArtistByPath(artistname)

        # Import video
        try:
            success = self.dbmanager.AddVideo(videopath, artist["id"])
        except Exception as e:
            logging.error("Importing video \"%s\" failed with error: %s \033[1;30m(Video upload canceled)", str(videopath), str(e))
            self.NotifyClient("InternalError", task, "Importing video failed")
            return False

        if not success:
            logging.error("Importing video \"%s\" failed. \033[1;30m(Video upload canceled)", str(videopath), str(e))
            self.NotifyClient("InternalError", task, "Importing video failed")
            return False

        # Add origin information to database if annotated
        try:
            origin = task["annotations"]["origin"]
        except KeyError as e:
            pass
        else:
            video = self.db.GetVideoByPath(videopath)
            video["origin"] = origin
            self.db.WriteVideo(video)

        logging.info("Importing Video succeeded")
        return True



    def ImportVideoArtwork(self, task):
        """
        Returns:
            ``True`` on success
        """
        # Check task state and type
        if task["state"] != "importartwork":
            logging.warning("Cannot import artwork that is not in \"importartwork\" state. Upload with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
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



    def ImportArtwork(self, task):
        """
        Task state must be ``"startimport"`` and content type must be ``"artwork"``

        Returns:
            ``True`` on success.
        """
        # Check task state and type
        if task["state"] != "startimport":
            logging.warning("Cannot import an upload that is not in \"startimport\" state. Upload with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return False

        success = False
        if task["contenttype"] != "artwork":
            logging.warning("Album artwork expected. Actual type of upload: \"%s\" \033[1;30m(No artwork will be imported)", str(task["contenttype"]))
            return False

        # Get important information
        try:
            artistname = task["annotations"]["artistname"]
            albumname  = task["annotations"]["albumname"]
            albumid    = task["annotations"]["albumid"]
            sourcepath = task["preprocessedpath"]
        except KeyError as e:
            logging.error("Collecting artwork information for importing failed with key-error for: %s \033[1;30m(Make sure the artist and album name is annotated as well as the album ID.)", str(e))
            return False

        # Import artwork
        awmanager   = MusicDBArtwork(self.cfg, self.db)
        artworkname = awmanager.CreateArtworkName(artistname, albumname)
        success     = awmanager.SetArtwork(albumid, sourcepath, artworkname)

        if not success:
            logging.error("Importing artwork \"%s\" failed. \033[1;30m(Artwork upload canceled)", str(sourcepath))
            self.NotifyClient("InternalError", task, "Importing artwork failed")
            return False

        # Add origin information to database if annotated
        try:
            origin = task["annotations"]["origin"]
        except KeyError as e:
            pass
        else:
            video = self.db.GetVideoByPath(videopath)
            video["origin"] = origin
            self.db.WriteVideo(video)

        logging.info("Importing Artwork succeeded")
        return True




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

