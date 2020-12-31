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
    * ``"failed"``: The upload failed
    * ``"notexisting"`` *virtual state* in case an Upload ID does not match an Upload. This task does not exist.

The uploaded file follows the following naming scheme: *contenttype* + ``-`` + *checksum* + ``.`` + source-file-extension

The upload manager also takes care about the validity of the uploaded file (via SHA-1 checksum).

The task state is persistently stored inside the uploads directory within a JSON file in a *tasks* sub-directory.
The file name is the task ID (equivalent to the Upload ID) + ``.json``.

"""

import json
import logging
import datetime
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.filesystem     import Filesystem
from lib.fileprocessing import Fileprocessing

Config      = None
Thread      = None
Callbacks   = []
RunThread   = False
TaskQueue   = {}

def StartUploadManagementThread(config, musicdb):
    """
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
    global TaskQueue

    if Thread != None:
        logging.warning("Upload Management Thread already running")
        return False

    if type(config) != MusicDBConfig:
        raise TypeError("config argument not of type MusicDBConfig")
    if type(musicdb) != MusicDatabase:
        raise TypeError("database argument not of type MusicDatabase")

    logging.debug("Initialize Upload Management Thread environment")
    Config       = config
    Callbacks    = []
    TaskQueue    = {}

    logging.debug("Starting Upload Management Thread")
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
    global TaskQueue

    filesystem = Filesystem(Config.uploads.path)

    if not Config.uploads.allow:
        logging.warning("Uploads not allowed! \033[1;30m(See MusicDB Configuration: [uploads]->allow)")

        while RunThread:
            time.sleep(1)
        return

    # Start streaming …
    while RunThread:
        # Sleep a bit to reduce the load on the CPU. If nothing to do, sleep a bit longer
        if len(TaskQueue) > 0:
            time.sleep(0.1)
        else:
            time.sleep(1)

        for key, task in TaskQueue.items():
            state = task["state"]
            if state == "init":
                pass    # request data
            elif state == "newdata":
                pass    # process new data
            else:
                pass

    return



class UploadManager(object):
    """
    This class manages uploading content to the server MusicDB runs on.
    All data is stored in the uploads-directory configured in the MusicDB configuration.
    
    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        if type(config) != MusicDBConfig:
            raise TypeError("config argument not of type MusicDBConfig")
        if type(database) != MusicDatabase:
            raise TypeError("database argument not of type MusicDatabase")

        self.db         = database
        self.cfg        = config
        self.tmpfs      = Filesystem(self.cfg.uploads.path)
        self.musicfs    = Filesystem(self.cfg.music.path)
        self.awfs       = Filesystem(self.cfg.artwork.path)
        # TODO: check write permission of all directories
        self.fileprocessing = Fileprocessing(self.cfg.uploads.path)



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
        if not notification in ["ChunkRequest", "UploadComplete", "UploadFailed", "InternalError"]: # TODO -> documentation
            raise ValueError("Unknown notification \"%s\""%(notification))

        status = {}
        if task != None:
            status["uploadid"]  = task["id"]
            status["offset"]    = task["offset"]    # offset of the data to request
            status["chunksize"] = 4096*100          # Upload 400KiB (TODO: Make configurable)
            status["state"]     = task["state"]
        else:
            status["uploadid"]  = None
            status["offset"]    = None
            status["chunksize"] = None
            status["state"]     = "notexisting"

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
        path = self.cfg.uploads.path + "tasks/" + taskid + ".json"



    #####################################################################
    # Management Functions                                              #
    #####################################################################



    def InitiateUpload(self, uploadid, mimetype, contenttype, filesize, checksum, sourcefilename):
        """
        Initiates an upload of a file into a MusicDB managed file space.
        After calling this method, a notification gets triggered to request the first chunk of data from the clients.

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

        fileextension   = self.tmpfs.GetFileExtension(sourcefilename)
        destinationname = contenttype + "-" + checksum + "." + fileextension
        destinationpath = self.cfg.uploads.path + "/" + destinationname

        # Remove existing upload if destination path exists
        self.tmpfs.RemoveFile(destinationpath)  # Removes file when it exists
        
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
        task["state"          ] = "waitforchunk"

        global TaskQueue
        TaskQueue[uploadid] = task

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

        global TaskQueue
        if uploadid not in TaskQueue:
            self.NotifiyClient("InternalError", None, "Invalid Upload ID")
            raise ValueError("Upload ID \"%s\" not in Task Queue.", str(uploadid))

        task      = TaskQueue[uploadid]
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
            task["state"] = "failed"
            logging.error("Upload Failed: \033[0;36m%s \e[1;30m(Checksum mismatch)", task["destinationpath"]);
            self.NotifyClient("UploadFailed", task, "Checksum mismatch")
            return False

        # TODO: Analyse File (Get Meta-Data, Unzip, …) -- Other process?
        task["state"] = "uploadcomplete"
        logging.info("Upload Complete: \033[0;36m%s", task["destinationpath"]);
        self.NotifyClient("UploadComplete", task)
        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

