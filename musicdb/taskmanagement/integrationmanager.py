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
This module organizes the integration of uploaded content into the Music Directory.
"""

import logging
from musicdb.mdbapi.musicdirectory      import MusicDirectory
from musicdb.taskmanagement.taskmanager import TaskManager


class IntegrationManager(TaskManager):
    """
    This class manages integration of content into the MusicDB Music Directory.
    It expects the data to integrate inside the upload directory.

    This class is derived from :class:`musicdb.taskmanagement.taskmanager.TaskManager`.
    
    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: (optional) A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        TaskManager.__init__(self, config, database)

        self.musicdirectory   = MusicDirectory(self.cfg)



    def InitiateIntegration(self, taskid, targetpath):
        """
        This method initiates the integration of an uploaded file or directory.
        The ``targetpath`` will be the destination at that the uploaded content will be moved to.
        This path must be relative to the music directory.

        If the content type of the uploaded content is ``"artwork"``, then
        the ``targetpath`` must be a path to an album or a video that already exists in the database.
        It determines if the artwork will be imported for an album or a video.
        The target type is determined by using :meth:`musicdb.mdbapi.musicdirectory.MusicDirectory.AnalysePath`.

        Otherwise it is mandatory that a file addressed by ``targetpath`` does not yet exist inside the Music Directory.
        When a parent directory of ``targetpath`` does not exist it will be created.

        The addressed task by ``taskid`` must be in the state ``"readyforintegration"``.

        Args:
            taskid (str): ID of the task that performed the upload
            targetpath (str): Path relative to the music directory

        Returns:
            The task ID as string or ``None`` if something failed.

        Raises:
            TypeError: When one of the parameters are of a wrong data type
            ValueError: When one of the parameters has an unexpected value
        """
        task = self.GetTaskByID(taskid)
        if task["state"] != "readyforintegration":
            logging.warning("Cannot integrate an upload that is not in \"readyforintegration\" state. Task with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return False

        # Update task dictionary with target path
        if task["contenttype"] == "artwork":
            targettype = None
            fileinfos  = self.musicdirectory.AnalysePath(targetpath)
            if fileinfos["video"] and self.musicdirectory.IsFile(targetpath):
                targettype = "video"
            elif fileinfos["album"] and self.musicdirectory.IsDirectory(targetpath):
                targettype = "album"

            task["state"] = "startartworkimport"
            task["awsourcetype"] = "imagefile"
            task["awsourcepath"] = task["preprocessedpath"]
            if targettype == "album":
                task["albumpath"] = targetpath
            elif targettype == "video":
                task["videopath"] = targetpath
            else:
                raise ValueError("Target path \"%s\" does not address a valid video file or album directory"%(str(targetpath)))

        elif task["contenttype"] == "albumfile":
            task["state"] = "startintegration"
            task["albumfilepath"] = targetpath

        self.SaveTask(task)
        self.ScheduleTask(task)
        return task["id"]



    def IntegrateUploadedFile(self, task, triggerimport=False):
        """
        This method integrated the uploaded files into the music directory.
        The whole file tree will be created following the MusicDB naming scheme.

        It is not guaranteed that after the integration all files and directory actually follow the MusicDB naming scheme.
        Files that have been integrated may violate that scheme.
        Adjusting the file and directory names is part of the import process.
        The integration process is for storing music files inside the music directory without any effort for the user.

        The upload task must be in ``startintegration`` state. If not, nothing happens.

        When *triggerimport* is ``true``, the integration manager triggers the import by the
        :mod:`~musicdb.taskmanagement.importmanager`
        This happens asynchronously inside the task management thread.

        Args:
            task (dict): dictionary of a task
            triggerimport (bool): Optional, default: ``False``. If ``True`` the import process of the content into the Music Database will be triggered.

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            TypeError: When *taskid* is not of type ``str``
            ValueError: When *taskid* is not included in the Task Queue
        """

        if task["state"] != "startintegration":
            logging.warning("Cannot integrate an upload that is not in \"startintegration\" state. Task with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return False

        # Perform integration
        self.UpdateTaskState(task, "integrating")
        success = False
        if task["contenttype"] == "video":
            success = self.IntegrateVideo(task)
        elif task["contenttype"] == "albumfile":
            success = self.IntegrateAlbumFile(task)
        #elif task["contenttype"] == "artwork":
        #    success = True # Importing artwork does not require the file at any specific place
        else:
            logging.warning("Unsupported content type of upload: \"%s\" \033[1;30m(Upload will be ignored)", str(task["contenttype"]))
            self.UpdateTaskState(task, "invalidcontent", "Unsupported content type")
            return False

        # Update task state
        if success == False:
            self.UpdateTaskState(task, "integrationfailed")
            return False

        logging.debug("Integration succeeded");
        if triggerimport:
            self.UpdateTaskState(task, "startmusicimport")
        else:
            self.UpdateTaskState(task, "readyforimport")
        return True



    # Individual Integration of Different Content Types


    def IntegrateVideo(self, task):
        """
        When an annotation needed for creating the video file path in the music directory is missing, ``False`` gets returned and an error message will be written into the log.
        """
        if task["preprocessedpath"] != None:
            uploadedfile = task["preprocessedpath"]
        else:
            uploadedfile  = task["uploadpath"]
        absuploadpath = self.uploaddirectory.AbsolutePath(uploadedfile)

        try:
            artistname    = task["annotations"]["artistname"]
            releasedate   = task["annotations"]["release"]
            videoname     = task["annotations"]["name"]
        except KeyError as e:
            logging.error("Collected video information for creating its path name failed with key-error for: %s \033[1;30m(Make sure all important annotations are given to that upload: name, artistname, release)", str(e))
            return False

        fileextension = self.uploaddirectory.GetFileExtension(uploadedfile)
        videofile     = artistname + "/" + releasedate + " - " + videoname + "." + fileextension

        task["videofile"] = videofile
        logging.debug("Integrating upload %s -> %s", str(uploadedfile), str(videofile))

        # Check if video file already exists
        if self.musicdirectory.Exists(videofile):
            logging.warning("File \"%s\" already exists in the music directory! \033[1;30m(It will NOT be overwritten)", str(videofile))
            self.NotifyClient("InternalError", task, "File already exists in the music directory")
            return False

        # Check if artist directory exists
        if not self.musicdirectory.IsDirectory(artistname):
            logging.info("Artist directory for \"%s\" does not exist and will be created.", str(artistname))
            try:
                self.musicdirectory.CreateSubdirectory(artistname)
            except PermissionError:
                logging.error("Creating artist sub-directory \"%s\" failed! - Permission denied! \033[1;30m(MusicDB requires write permission to the music file tree)", str(artistname))
                self.NotifyClient("InternalError", task, "Creating artist directory failed - Permission denied")
                return False

        # Copy file, create Artist directory if not existing
        try:
            success = self.musicdirectory.CopyFile(absuploadpath, videofile)
        except PermissionError:
            logging.error("Copying video file to \"%s\" failed! - Permission denied! \033[1;30m(MusicDB requires write permission to the music file tree)", str(videofile))
            self.NotifyClient("InternalError", task, "Copying failed - Permission denied")
            return False

        if(success):
            logging.info("New video file at %s", str(videofile))
        else:
            logging.warning("Copying video file to \"%s\" failed!", str(videofile))
        return success



    def IntegrateAlbumFile(self, task):
        """
        This method copies a file form the upload directory into the music directory.
        It is expected that the file is part of an album.
        If the file already exists, ``False`` gets returned.

        The file is copied form the location ``"preprocessedpath"`` if set.
        Otherwise it is copied form ``"uploadpath"``.
        The destination path is expected to be defined in ``"albumfilepath"``.

        If the parent directory (artist or album directory) does not exist, it will be created.

        Args:
            task (dict): Data structure of a task that contains the keys mention in the method description

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if task["preprocessedpath"] != None:
            uploadedfile = task["preprocessedpath"]
        else:
            uploadedfile  = task["uploadpath"]

        absuploadedfile = self.uploaddirectory.AbsolutePath(uploadedfile)
        albumfilepath   = task["albumfilepath"]


        # Check if video file already exists
        albumdirectorypath = self.musicdirectory.GetDirectory(albumfilepath)
        if not self.musicdirectory.IsDirectory(albumdirectorypath):
            logging.info("Album directory for \"%s\" does not exist and will be created.", str(albumfilepath))
            try:
                self.musicdirectory.CreateSubdirectory(albumdirectorypath)
            except PermissionError:
                logging.error("Creating album directory \"%s\" failed! - Permission denied! \033[1;30m(MusicDB requires write permission to the music file tree)", str(albumdirectorypath))
                self.NotifyClient("InternalError", task, "Creating album directory failed - Permission denied")
                return False

        # Copy file
        logging.debug("Copying album file \"%s\" -> \"%s\"", uploadedfile, albumfilepath)
        try:
            success = self.musicdirectory.CopyFile(absuploadedfile, albumfilepath)
        except FileNotFoundError:
            logging.error("Copying album file from \"%s\" to \"%s\" failed! - File not found! \033[1;30m", str(uploadedfile), str(albumfilepath))
            self.NotifyClient("InternalError", task, "Copying failed - File not found")
            return False
        except PermissionError:
            logging.error("Copying album file to \"%s\" failed! - Permission denied! \033[1;30m(MusicDB requires write permission to the music file tree)", str(albumfilepath))
            self.NotifyClient("InternalError", task, "Copying failed - Permission denied")
            return False

        if(success):
            logging.info("New album file at %s", str(albumfilepath))
        else:
            logging.warning("Copying album file to \"%s\" failed!", str(albumfilepath))
        return success



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

