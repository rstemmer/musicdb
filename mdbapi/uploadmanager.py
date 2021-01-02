# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
The communication is handled via notification to allow continuing uploading even when the connection gets lost in the meanwhile.

The upload is performed chunk-wise.
After initiating an Upload, this upload manager requests chunks of data via MusicDB Notifications from the clients.
All clients are informed about the upload process, not only the client that initiated the upload.
So each client can show the progress and state.

Task states

    * ``"waitforchunk"``: A new chunk of data was requested, and is expected from the client
    * ``"uploadcomplete"``: The whole file is now available in the temporary upload directory
    * ``"uploadfailed"``: The upload failed
    * ``"notexisting"`` *virtual state* in case an Upload ID does not match an Upload. This task does not exist.
    * ``"preprocessed"``: The uploaded file was successfully pre-processed and is ready for importing
    * ``"invalidcontent"``: Pre-processing failed. The content was unexpected or invalid.
    * ``"integrated"``: The uploaded file was successfully integrated into the music directory
    * ``"integrationfailed"``: Integrating the uploaded file into the music directory failed

After upload is complete,
the Management Thread takes care about post processing or removing no longer needed content

The uploaded file follows the following naming scheme: *contenttype* + ``-`` + *checksum* + ``.`` + source-file-extension

The upload manager also takes care about the validity of the uploaded file (via SHA-1 checksum).

The task state is persistently stored inside the uploads directory within a JSON file in a *tasks* sub-directory.
The file name is the task ID (equivalent to the Upload ID) + ``.json``.

"""
# TODO: Describe task-keys
# TODO: Visualize state machine

import json
import time
import logging
import datetime
import threading
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.filesystem     import Filesystem
from lib.fileprocessing import Fileprocessing
from lib.metatags       import MetaTags

Config      = None
Thread      = None
Callbacks   = []
RunThread   = False
Tasks       = None

def StartUploadManagementThread(config, musicdb):
    """
    This method starts the Upload management thread.

    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~lib.db.musicdb.MusicDatabase` instance

    Returns:
        ``True`` on Success, otherwise ``False``

    Raises:
        TypeError: When the arguments are not of the correct type.
    """
    global Config
    global Thread
    global RunThread
    global Callbacks
    global Tasks

    if Thread != None:
        logging.warning("Upload Management Thread already running")
        return False

    if type(config) != MusicDBConfig:
        raise TypeError("config argument not of type MusicDBConfig")
    if type(musicdb) != MusicDatabase:
        raise TypeError("database argument not of type MusicDatabase")


    logging.debug("Starting Upload Management Thread")
    Config    = config
    RunThread = True
    Thread    = threading.Thread(target=UploadManagementThread)
    Thread.start()

    return True



def StopUploadManagementThread():
    """
    This function stops the Upload Management Thread.
    The function is blocking and waits until the thread is closed.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global RunThread
    global Thread

    if Thread == None:
        logging.warning("There is no Upload Management Thread running!")
        return False

    logging.debug("Waiting for Upload Management Thread to stop…")

    RunThread = False
    Thread.join()
    Thread = None

    logging.debug("Upload Management Thread shut down.")
    return True



def UploadManagementThread():
    """
    """
    # TODO: Remove left over uploads (uploaded files without task-ID)
    # TODO: Continue uploads that were interrupted
    # TODO: Identify discontinued uploads
    # TODO: Handle failed uploads (clean up)
    global Config
    global Thread
    global RunThread
    global Callbacks
    global Tasks

    filesystem = Filesystem(Config.uploads.path)
    manager    = UploadManager(Config)

    if not Config.uploads.allow:
        logging.warning("Uploads not allowed! \033[1;30m(See MusicDB Configuration: [uploads]->allow)")

    # Start streaming …
    while RunThread:
        # Sleep a bit to reduce the load on the CPU. If nothing to do, sleep a bit longer
        if len(Tasks) > 0:
            time.sleep(1)
        else:
            time.sleep(1)

        for key, task in Tasks.items():
            state = task["state"]
            if state == "uploadfailed":
                pass    # TODO: Clean up everything
            elif state == "uploadcomplete":
                manager.PreProcessUploadedFile(task)

    return



class UploadManager(object):
    """
    This class manages uploading content to the server MusicDB runs on.
    All data is stored in the uploads-directory configured in the MusicDB configuration.
    
    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: (optional) A :class:`~lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database=None):
        if type(config) != MusicDBConfig:
            raise TypeError("config argument not of type MusicDBConfig")
        if database != None and type(database) != MusicDatabase:
            raise TypeError("database argument not of type MusicDatabase or None")

        self.db         = database
        self.cfg        = config
        self.uploadfs   = Filesystem(self.cfg.uploads.path)
        self.musicfs    = Filesystem(self.cfg.music.path)
        self.artworkfs  = Filesystem(self.cfg.artwork.path)
        # TODO: check write permission of all directories
        self.fileprocessing = Fileprocessing(self.cfg.uploads.path)

        global Tasks
        if Tasks == None:
            self.LoadTasks()



    #####################################################################
    # Callback Function Management                                      #
    #####################################################################



    def RegisterCallback(self, function):
        """
        Register a callback function that reacts on Upload related events.
        For more details see the module description at the top of this document.

        Args:
            function: A function that shall be called on an event.

        Returns:
            *Nothing*
        """
        global Callbacks
        Callbacks.append(function)



    def RemoveCallback(self, function):
        """
        Removes a function from the list of callback functions.

        Args:
            function: A function that shall be called removed.

        Returns:
            *Nothing*
        """
        global Callbacks

        # Not registered? Then do nothing.
        if not function in Callbacks:
            logging.warning("A Streaming Thread callback function should be removed, but did not exist in the list of callback functions!")
            return

        Callbacks.remove(function)



    def NotifyClient(self, notification, task, message=None):
        """
        This method triggers a client-notification.
        The notification comes with the current status of the upload process.
        This includes the following keys - independent of the state of the upload:

            * uploadid: ID of the upload the notification is associated with
            * offset: Offset of the requested data in the source file
            * chunksize: The maximum chunk size
            * state: The current state of the upload task
            * message: ``null``/``None`` or a message from the server
            * annotation: object with annotated information
            * uploadslist: Except for ``ChunkRequest`` events, the WebSocket server append the result of :meth:`lib.ws.mdbwsi.MusicDBWebSocketInterface.GetUploads` to the notification

        *task* can be ``None`` in case the notification is meant to be an information that a given upload ID is invalid.

        Args:
            notification (str): Name of the notification
            task (dict): Task structure
            message (str): (optional) text message (like an error message) to the client

        Returns:
            *Nothing*

        Raises:
            ValueError: When notification has an unknown notification name
        """
        if not notification in ["ChunkRequest", "UploadComplete", "UploadFailed", "InternalError", "Processed", "Annotated"]: # TODO -> documentation
            raise ValueError("Unknown notification \"%s\""%(notification))

        status = {}
        if task != None:
            status["uploadid"]  = task["id"]
            status["offset"]    = task["offset"]    # offset of the data to request
            status["chunksize"] = 4096*100          # Upload 400KiB (TODO: Make configurable)
            status["state"]     = task["state"]
            status["annotations"]= task["annotations"]
        else:
            status["uploadid"]  = None
            status["offset"]    = None
            status["chunksize"] = None
            status["state"]     = "notexisting"
            status["annotations"]= None

        status["message"]   = message

        global Callbacks
        for callback in Callbacks:
            try:
                callback(notification, status)
            except Exception as e:
                logging.exception("A Upload Management event callback function crashed!")


    #####################################################################
    # State management                                                  #
    #####################################################################



    def SaveTask(self, task):
        """
        This method saves a task in the uploads directory under ``tasks/${Task ID}.json``

        Args:
            task (dict): The task to save

        Returns:
            *Nothing*
        """
        taskid = task["id"]
        data = json.dumps(task)
        path = self.cfg.uploads.path + "/tasks/" + taskid + ".json"

        if not self.uploadfs.IsDirectory("tasks"):
            logging.debug("tasks directory missing. Creating \"%s\"", self.cfg.uploads.path + "/tasks")
            self.uploadfs.CreateSubdirectory("tasks")

        with open(path, "w+") as fd:
            fd.write(data)

        return



    def LoadTasks(self):
        """
        Loads all task from the JSON files inside the tasks-directory.
        The list of active tasks will be replaced by the loaded tasks.

        Returns:
            *Nothing*
        """
        logging.debug("Loading Upload-Tasks…")
        
        taskfilenames = self.uploadfs.ListDirectory("tasks")

        global Tasks
        Tasks = {}
        for taskfilename in taskfilenames:
            taskpath = self.cfg.uploads.path + "/tasks/" + taskfilename

            if self.uploadfs.GetFileExtension(taskpath) != "json":
                continue

            try:
                with open(taskpath) as fd:
                    task = json.load(fd)
            except Exception as e:
                logging.warning("Loading task file \"%s\" failed with error \"%s\". \033[1;30m(File will be ignored)", str(taskpath), str(e))
                continue

            if "id" not in task:
                logging.warning("File \"%s\" is not a valid task (ID missing). \033[1;30m(File will be ignored)", str(taskpath), str(e))
                continue

            Tasks[task["id"]] = task

        return



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
        if type(uploadid) != str:
            raise TypeError("Upload ID must be of type string")
        if type(mimetype) != str:
            raise TypeError("mime type must be of type string")
        if type(contenttype) != str:
            raise TypeError("content type must be of type string")
        if contenttype not in ["video", "album", "artwork"]:
            raise ValueError("content type \"%s\" not valid. \"video\", \"album\" or \"artwork\" expected."%(str(contenttype)))
        if type(filesize) != int:
            raise TypeError("file size must be of type int")
        if filesize <= 0:
            raise ValueError("file size must be greater than 0")
        if type(checksum) != str:
            raise TypeError("Checksum must be of type string")
        if type(sourcefilename) != str:
            raise TypeError("Source file name must be of type string")

        if not self.cfg.uploads.allow:
            self.NotifyClient("InternalError", None, "Uploads deactivated")
            logging.warning("Uploads not allowed! \033[1;30m(See MusicDB Configuration: [uploads]->allow)")
            return

        fileextension   = self.uploadfs.GetFileExtension(sourcefilename)
        destinationname = contenttype + "-" + checksum + "." + fileextension
        destinationpath = self.cfg.uploads.path + "/" + destinationname

        # TODO: Check if there is already a task with the given ID.
        # If this task is in waitforchunk state, the upload can be continued instead of restarting it.

        # Remove existing upload if destination path exists
        self.uploadfs.RemoveFile(destinationpath)  # Removes file when it exists
        
        # Create File
        with open(destinationpath, "w+b"):
            pass

        task = {}
        task["id"             ] = uploadid
        task["filesize"       ] = filesize
        task["offset"         ] = 0
        task["contenttype"    ] = contenttype
        task["mimetype"       ] = mimetype
        task["sourcefilename" ] = sourcefilename
        task["sourcechecksum" ] = checksum
        task["destinationpath"] = destinationpath
        task["videofile"      ] = None              # Path to the video file in the music directory
        task["state"          ] = "waitforchunk"
        task["annotations"    ] = {}
        self.SaveTask(task)

        global Tasks
        Tasks[uploadid] = task

        self.NotifyClient("ChunkRequest", task)
        return



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
            TypeError: When *uploadid* is not of type ``str``
            ValueError: When *uploadid* is not included in the Task Queue
        """
        if type(rawdata) != bytes:
            raise TypeError("raw data must be of type bytes. Type was \"%s\""%(str(type(rawdata))))
        if type(uploadid) != str:
            raise TypeError("Upload ID must be a string. Type was \"%s\""%(str(type(uploadid))))

        global Tasks
        if uploadid not in Tasks:
            self.NotifiyClient("InternalError", None, "Invalid Upload ID")
            raise ValueError("Upload ID \"%s\" not in Task Queue.", str(uploadid))

        task      = Tasks[uploadid]
        chunksize = len(rawdata)
        filepath  = task["destinationpath"]

        try:
            with open(filepath, "ab") as fd:
                fd.write(rawdata)
        except Exception as e:
            logging.warning("Writing chunk of uploaded data \"%s\" failed: %s", filepath, str(e))
            self.NotifyClient("InternalError", task, "Writing data failed with error: \"%s\""%(str(e)))
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
        destchecksum = self.fileprocessing.Checksum(task["destinationpath"], "sha1")
        if destchecksum != task["sourcechecksum"]:
            task["state"] = "uploadfailed"
            logging.error("Upload Failed: \033[0;36m%s \e[1;30m(Checksum mismatch)", task["destinationpath"]);
            self.NotifyClient("UploadFailed", task, "Checksum mismatch")
            return False

        task["state"] = "uploadcomplete"
        self.SaveTask(task)

        logging.info("Upload Complete: \033[0;36m%s", task["destinationpath"]);
        self.NotifyClient("UploadComplete", task)
        # Now, the Management Thread takes care about post processing or removing no longer needed content
        return True


    def GetTasks(self):
        """
        Returns:
            The dictionary with all upload tasks
        """

        global Tasks
        return Tasks



    def PreProcessUploadedFile(self, task):
        """
        This method initiates pre-processing of an uploaded file.
        Depending on the *contenttype* different post processing methods are called:

            * ``"video"``: :meth:`~PreProcessVideo`

        The task must be in ``"uploadcomplete"`` state, otherwise nothing happens but printing an error message.
        If post processing was successful, the task state gets updated to ``"preprocessed"``.
        When an error occurred, the state will become ``"invalidcontent"``.

        Args:
            task (dict): the task object of an upload-task

        Returns:
            *Nothing*
        """
        if task["state"] != "uploadcomplete":
            logging.error("task must be in \"uploadcomplete\" state for post processing. Actual state was \"%s\". \033[1;30m(Such a mistake should not happen. Anyway, the task won\'t be post process and nothing bad will happen.)", task["state"])
            return

        # Perform post processing
        logging.debug("Preprocessing upload %s -> %s", str(task["sourcefilename"]), str(task["destinationpath"]))
        success = False
        if task["contenttype"] == "video":
            success = self.PreProcessVideo(task)
        else:
            logging.warning("Unsupported content type of upload: \"%s\" \033[1;30m(Upload will be ignored)", str(task["contenttype"]))
            return

        # Update task state
        if success == True:
            task["state"] = "preprocessed"
        else:
            task["state"] = "invalidcontent"
        self.SaveTask(task)

        self.NotifyClient("Processed", task)
        return



    def PreProcessVideo(self, task):
        """

        Args:
            task (dict): the task object of an upload-task
        """
        meta = MetaTags()
        try:
            meta.Load(task["destinationpath"])
        except ValueError:
            logging.error("The file \"%s\" uploaded as video to %s is not a valid video or the file format is not supported. \033[1;30m(File will be not further processed.)", task["sourcefilename"], task["destinationpath"])
            return False

        # Get all meta infos (for videos, this does not include any interesting information.
        # Maybe the only useful part is the Load-method to check if the file is supported by MusicDB
        #tags = meta.GetAllMetadata()
        #logging.debug(tags)
        return True


    def AnnotateUpload(self, uploadid, annotations):
        """

        Args:
            uploadid (str): ID to identify the upload

        Raises:
            TypeError: When *uploadid* is not of type ``str``
            ValueError: When *uploadid* is not included in the Task Queue
        """
        if type(uploadid) != str:
            raise TypeError("Upload ID must be a string. Type was \"%s\""%(str(type(uploadid))))

        global Tasks
        if uploadid not in Tasks:
            self.NotifiyClient("InternalError", None, "Invalid Upload ID")
            raise ValueError("Upload ID \"%s\" not in Task Queue.", str(uploadid))

        task = Tasks[uploadid]

        for key in ["name", "artistname", "artistid", "release", "origin"]:
            if key in annotations:
                task["annotations"][key] = annotations[key]

        self.SaveTask(task)
        self.NotifyClient("Annotated", task)
        return



    def IntegrateUploadedFile(self, uploadid):
        """
        This method integrated the uploaded files into the music directory.
        The whole file tree will be created following the MusicDB naming scheme.

        The upload task must be in ``preprocesses`` state. If not, nothing happens.

        Args:
            uploadid (str): ID to identify the upload

        Raises:
            TypeError: When *uploadid* is not of type ``str``
            ValueError: When *uploadid* is not included in the Task Queue
        """
        if type(uploadid) != str:
            raise TypeError("Upload ID must be a string. Type was \"%s\""%(str(type(uploadid))))

        global Tasks
        if uploadid not in Tasks:
            self.NotifiyClient("InternalError", None, "Invalid Upload ID")
            raise ValueError("Upload ID \"%s\" not in Task Queue.", str(uploadid))

        task = Tasks[uploadid]
        if task["state"] != "preprocessed":
            logging.warning("Cannot integrate an upload that is not in \"preprocessed\" state. Upload with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return

        # Perform post processing
        success = False
        if task["contenttype"] == "video":
            success = self.IntegrateVideo(task)
        else:
            logging.warning("Unsupported content type of upload: \"%s\" \033[1;30m(Upload will be ignored)", str(task["contenttype"]))
            return

        # Update task state
        if success == True:
            task["state"] = "integrated"
        else:
            task["state"] = "integrationfailed"
        self.SaveTask(task)

        self.NotifyClient("Processed", task)
        return



    def IntegrateVideo(self, task):
        """
        When an annotation needed for creating the video file path in the music directory is missing, ``False`` gets returned and an error message written into the log
        """
        uploadedfile  = task["destinationpath"]    # uploaded file
        try:
            artistname    = task["annotations"]["artistname"]
            releasedate   = task["annotations"]["release"]
            videoname     = task["annotations"]["name"]
        except KeyError as e:
            logging.error("Collection video information for creating its path name failed with key-error for: %s \033[1;30m(Make sure all important annotations are given to that upload: name, artistname, release)", str(e))
            return False

        fileextension = self.uploadfs.GetFileExtension(uploadedfile)
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





# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

