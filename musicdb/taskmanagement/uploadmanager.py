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
This module organizes the uploading process to data from the WebUI into the MusicDB Upload directory
where it can then be further processed.
"""

import logging
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



    def InitiateUpload(self, taskid, mimetype, contenttype, filesize, checksum, sourcefilename):
        """
        Initiates an upload of a file into a MusicDB managed file space.
        After calling this method, a notification gets triggered to request the first chunk of data from the clients.
        In case uploads are deactivated in the MusicDB Configuration, an ``"InternalError"`` Notification gets sent to the clients.

        Args:
            taskid (str): Unique ID to identify the upload task 
            mimetype (str): MIME-Type of the file (example: ``"image/png"``)
            contenttype (str): Type of the content: (``"video"``, ``"album"``, ``"artwork"``)
            filesize (int): Size of the complete file in bytes
            checksum (str): SHA-1 check sum of the source file
            sourcefilename (str): File name (example: ``"test.png"``)

        Raises:
            TypeError: When one of the arguments has not the expected type
            ValueError: When *contenttype* does not have the expected values
        """
        self.InitiateProcess(taskid, mimetype, contenttype, filesize, checksum, sourcefilename, "waitforchunk")
        return



    def RequestRemoveUpload(self, taskid):
        """
        This method triggers removing a specific upload.
        This includes the uploaded file as well as the upload task information and annotations.

        The upload task can be in any state.
        When the remove-operation is triggered, its state gets changed to ``"remove"``.

        Only the ``"remove"`` state gets set. Removing will be done by the Management Thread.

        Args:
            taskid (str): ID of the upload-task

        Returns:
            ``True`` on success
        """
        try:
            task = self.GetTaskByID(taskid)
        except Exception as e:
            logging.error("Removing of uploaded file failed because of the following error: %s", str(e))
            return False

        self.UpdateTaskState(task, "remove")
        return True



    def NewChunk(self, taskid, rawdata):
        """
        This method processes a new chunk received from the uploading client.

        Args:
            taskid (str): Unique ID to identify the upload task
            rawdata (bytes): Raw data to append to the uploaded data

        Returns:
            ``False`` in case an error occurs. Otherwise ``True``.

        Raises:
            TypeError: When *rawdata* is not of type ``bytes``
        """
        if type(rawdata) != bytes:
            raise TypeError("raw data must be of type bytes. Type was \"%s\""%(str(type(rawdata))))

        try:
            task = self.GetTaskByID(taskid)
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



    def AnnotateUpload(self, taskid, annotations):
        """
        This method can be used to add additional information to an upload.
        This can be done during or after the upload process.

        Args:
            taskid (str): ID to identify the upload
            annotations (dict): A dictionary with annotations that will be added to the upload task data structure

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            TypeError: When *taskid* is not of type ``str``
            ValueError: When *taskid* is not included in the Task Queue
        """
        try:
            task = self.GetTaskByID(taskid)
        except Exception as e:
            logging.error("Internal error while annotating an upload: %s", str(e))
            return False

        for key, item in annotations.items():
            task["annotations"][key] = item

        self.SaveTask(task)
        self.NotifyClient("StateUpdate", task)
        return True



    def PreProcessUploadedFile(self, task):
        """
        This method initiates pre-processing of an uploaded file.
        Depending on the *contenttype* different post processing methods are called:

            * ``"video"``: :meth:`~PreProcessVideo`
            * ``"artwork"``: :meth:`~PreProcessArtwork`

        The task must be in ``"uploadcomplete"`` state, otherwise nothing happens but printing an error message.
        If post processing was successful, the task state gets updated to ``"readyforintegration"``.
        When an error occurred, the state will become ``"invalidcontent"``.

        Args:
            task (dict): the task object of an upload-task

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if task["state"] != "uploadcomplete":
            logging.error("The task %s must be in \"uploadcomplete\" state for post processing. Actual state was \"%s\". \033[1;30m(Such a mistake should not happen. Anyway, the task won\'t be post process and nothing bad will happen.)", task["id"], task["state"])
            return False

        # Perform preprocessing
        logging.debug("Preprocessing upload %s -> %s", str(task["sourcefilename"]), str(task["uploadpath"]))
        self.UpdateTaskState(task, "preprocessing")
        success = False
        if task["contenttype"] == "video":
            success = self.PreProcessVideo(task)
        elif task["contenttype"] == "artwork":
            success = self.PreProcessArtwork(task)
        elif task["contenttype"] == "albumfile":
            success = self.PreProcessAlbumFile(task)
        else:
            logging.warning("Unsupported content type of upload: \"%s\" \033[1;30m(Upload will be ignored)", str(task["contenttype"]))
            self.UpdateTaskState(task, "invalidcontent", "Unsupported content type")
            return False

        # Update task state
        if success == True:
            logging.debug("Preprocessed %s -> %s", str(task["uploadpath"]), str(task["preprocessedpath"]))
            newstate = "readyforintegration"
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


    def PreProcessAlbumFile(self, task):
        """
        An album file in general can be anything. It can be a song (normal case) but also a booklet,
        a music video or anything else.
        This method identifies music files and reads its meta data using the :class:`~musicdb.lib.metatags.MetaTags` class.

        All tags returned by :meth:`~musicdb.lib.metatags.MetaTags.GetAllMetadata` will be annotated to the task, if the file is a music file.
        To annotate those information, the :meth:`~AnnotateUpload` method will be used.

        Args:
            task (dict): the task object of an upload-task

        Returns:
            ``True`` on success, otherwise ``False``.
        """
        taskid     = task["id"]
        uploadpath = task["uploadpath"]
        # TODO: Determine the task["minetype"] can be very interesting/important because of the variety of file types processed within this method

        # Read out some meta data and annotate them to the task
        meta = MetaTags()
        try:
            meta.Load(uploadpath)
        except ValueError:
            logging.debug("The file \"%s\" uploaded as part of an album to %s is not a song file.", task["sourcefilename"], task["uploadpath"])
        else:
            tags = meta.GetAllMetadata()
            self.AnnotateUpload(taskid, tags)

        task["preprocessedpath"] = uploadpath # path does not change. Set it anyway to be consistent.
        return True


    def PreProcessArtwork(self, task):
        """
        This method preprocesses the uploaded artwork.
        If the uploaded file is not a JPEG file, it will be JPEG encoded.
        On success, after calling this method, the ``"preprocessedpath"`` attribute of the task dictionary is
        set to a valid JPEG file.

        Args:
            task (dict): the task object of an upload-task

        Returns:
            ``True`` on success, otherwise ``False``.
        """
        origfile = task["uploadpath"]
        extension= self.uploaddirectory.GetFileExtension(origfile)
        jpegfile = origfile[:-len(extension)] + "jpg"
        if extension != "jpg":
            logging.debug("Transcoding artwork file form %s (\"%s\") to JPEG (\"%s\")", extension, origfile, jpegfile);
            try:
                im = Image.open(origfile)
                im = im.convert("RGB")
                im.save(jpegfile, "JPEG", optimize=True, progressive=True)
            except Exception as e:
                logging.error("Transcoding %s -> %s failed with exception: %s", origfile, jpegfile, str(e))
                return False

        task["preprocessedpath"] = jpegfile
        return True




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

