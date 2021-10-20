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



    # TODO: This may be useful to integrate any music from the file system that is already available
    #       and not recently uploaded.
    def InitiateIntegration(self):
        """
        """
        raise NotImplementedError
        #self.InitiateProcess(uploadid, mimetype, contenttype, filesize, checksum, sourcefilename, "waitforchunk")
        #return



    def IntegrateUploadedFile(self, taskid, triggerimport=False):
        """
        This method integrated the uploaded files into the music directory.
        The whole file tree will be created following the MusicDB naming scheme.

        The upload task must be in ``readyforintegration`` state. If not, nothing happens.

        When *triggerimport* is ``true``, the integration manager triggers the import by the
        :mod:`~musicdb.taskmanagement.importmanager`
        This happens asynchronously inside the task management thread.

        Args:
            taskid (str): ID to identify the upload
            triggerimport (bool): Optional, default: ``False``. If ``True`` the import process of the content into the Music Database will be triggered.

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            TypeError: When *taskid* is not of type ``str``
            ValueError: When *taskid* is not included in the Task Queue
        """
        try:
            task = self.GetTaskByID(taskid)
        except Exception as e:
            logging.error("Integration of uploaded file failed because of the following error: %s", str(e))
            return False

        if task["state"] != "readyforintegration":
            logging.warning("Cannot integrate an upload that is not in \"readyforintegration\" state. Task with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return False

        # Perform integration
        self.UpdateTaskState(task, "integrating")
        success = False
        if task["contenttype"] == "video":
            success = self.IntegrateVideo(task)
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
            success = self.musicdirectory.CopyFile(uploadedfile, videofile)
        except PermissionError:
            logging.error("Copying video file to \"%s\" failed! - Permission denied! \033[1;30m(MusicDB requires write permission to the music file tree)", str(videofile))
            self.NotifyClient("InternalError", task, "Copying failed - Permission denied")
            return False

        if(success):
            logging.info("New video file at %s", str(videofile))
        else:
            logging.warning("Copying video file to \"%s\" failed!", str(videofile))
        return success




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

