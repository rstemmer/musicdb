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
import logging
import threading
import uuid
from pathlib            import Path
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.filesystem     import Filesystem

TaskManagerLock = threading.RLock() # RLock is mandatory for nested calls!
Callbacks = []
Tasks     = None

class TaskManager(object):
    """
    This is a base class that provides a common interface used by the
    :meth:`~musicdb.taskmanagement.managementthread.TaskManagementThread`
    to perform the upload, integration and import tasks.

    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: (optional) A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """
    def __init__(self, config, database):
        if type(config) != MusicDBConfig:
            raise TypeError("config argument not of type MusicDBConfig")
        if database != None and type(database) != MusicDatabase:
            raise TypeError("database argument not of type MusicDatabase or None")

        self.db  = database
        self.cfg = config
        self.uploaddirectory = Filesystem(self.cfg.directories.uploads)
        self.tasksdirectory  = Filesystem(self.cfg.directories.tasks)

        global Tasks
        with TaskManagerLock:
            if Tasks == None:
                self.LoadTasks()



    #####################################################################
    # Callback Function Management                                      #
    #####################################################################



    def RegisterCallback(self, function):
        """
        Register a callback function that reacts on Upload, Integration or Import related events.
        For more details see the module description at the top of this document.

        The function must expect two parameters: The notification type (a string) and a dictionary with the status.
        Details can be found in the :meth:`~NotifyClient` description.

        Args:
            function: A function that shall be called on an event.

        Returns:
            *Nothing*
        """
        global Callbacks
        with TaskManagerLock:
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
        with TaskManagerLock:
            if not function in Callbacks:
                logging.warning("A Streaming Thread callback function should be removed, but did not exist in the list of callback functions!")
                return

            Callbacks.remove(function)



    def NotifyClient(self, notification, task, message=None):
        """
        This method triggers a client-notification.

        There are three kind of notifications:

            * ``"ChunkRequest"``: A new chunk of data is requested
            * ``"StateUpdate"``: The state or annotations of an upload-task has been changed. See ``"state"`` value.
            * ``"InternalError"``: There is an internal error occurred during. See ``"message"`` value.

        The notification comes with the current status of the upload process.
        This includes the following keys - independent of the state of the upload:

            * taskid: ID of the upload the notification is associated with
            * offset: Offset of the requested data in the source file
            * chunksize: The maximum chunk size
            * state: The current state of the upload task
            * message: ``null``/``None`` or a message from the server
            * task: The task dictionary itself
            * uploadslist: Except for ``ChunkRequest`` events, the WebSocket server append the result of :meth:`musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface.GetUploads` to the notification

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
        if not notification in ["ChunkRequest", "StateUpdate", "InternalError"]:
            raise ValueError("Unknown notification \"%s\""%(notification))

        status = {}
        if task != None:
            status["taskid"]    = task["id"]
            status["offset"]    = task["offset"]    # offset of the data to request
            status["chunksize"] = 4096*100          # Upload 400KiB (TODO: Make configurable)
            status["state"]     = task["state"]
            status["task"]      = task
        else:
            status["taskid"]    = None
            status["offset"]    = None
            status["chunksize"] = None
            status["state"]     = "notexisting"
            status["task"]      = None

        status["message"]   = message

        global Callbacks
        for callback in Callbacks:
            try:
                callback(notification, status)
            except Exception as e:
                logging.exception("A Task Management event callback function crashed!")



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
        path = self.tasksdirectory.GetRoot() /  Path(taskid+".json")

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
        
        taskfilepaths = self.tasksdirectory.ListDirectory()

        global Tasks
        with TaskManagerLock:
            Tasks = {}
            for taskfilepath in taskfilepaths:
                taskpath = self.tasksdirectory.AbsolutePath(taskfilepath)

                if self.tasksdirectory.GetFileExtension(taskpath) != "json":
                    logging.debug("Unexpected file in task directory: %s", str(taskfilepath))
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



    def CreateTaskID(self):
        """
        This method creates a new Task ID.
        In detail, it is a `Version 4 Universally Unique Identifier (UUID) <https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>`_ .
        It will be returned as a string.

        Returns:
            A UUID to be used as entry ID
        """
        return str(uuid.uuid4())



    def CreateNewTask(self):
        """
        This method returns an empty but initialized task.
        The task state will be set to ``"new"``.
        The task ID will be created by :meth:`~CreateTaskID`.
        All other entries are set to ``None``.

        The new task will not be saved and not scheduled!

        Returns:
            A new task dictionary
        """
        task = {}
        # General Data
        task["id"             ] = self.CreateTaskID()
        task["state"          ] = "new"
        task["contenttype"    ] = None
        task["mimetype"       ] = None
        task["annotations"    ] = {}
        # Upload Related
        task["filesize"       ] = None
        task["offset"         ] = None
        task["sourcefilename" ] = None
        task["sourcechecksum" ] = None
        task["uploadpath"     ] = None
        task["preprocessedpath"]= None
        # Import/Integration Related
        task["videopath"      ] = None              # Path to the video file in the music directory
        task["albumpath"      ] = None              # Path to the album directory in the music directory
        task["awsourcetype"   ] = None
        task["awsourcepath"   ] = None

        return task



    def GetTasks(self):
        """
        Returns:
            The dictionary with all upload tasks
        """
        global Tasks
        return Tasks



    def GetTaskByID(self, taskid):
        """
        This method returns an existing task from the tasklist.
        The task gets identified by its ID aka Task ID

        When the task does not exits, the clients get an ``"InternalError"`` notification.
        The tasks state is then ``"notexisting"``.

        Args:
            taskid (str): ID of the task

        Returns:
            A task dictionary

        Raises:
            TypeError: When *taskid* is not a string
            ValueError: When *taskid* is not a valid key in the Tasks-dictionary
        """
        if type(taskid) != str:
            raise TypeError("Task ID must be a string. Type was \"%s\"."%(str(type(taskid))))

        global Tasks
        if taskid not in Tasks:
            self.NotifyClient("InternalError", None, "Invalid Task ID")
            raise ValueError("Task ID \"%s\" not in Task Queue."%(str(taskid)))

        return Tasks[taskid]



    def UpdateTaskState(self, task, state, errormessage=None):
        """
        This method updates and saves the state of an task.
        An ``"StateUpdate"`` notification gets send as well.
        If the task already is in the state, nothing happens.

        If *errormessage* is not ``None``, the notification gets send as ``"InternalError"`` with the message

        Args:
            task (dict): Task object to update
            state (str): New state
            message (str): Optional message

        Returns:
            *Nothing*
        """
        if task["state"] == state:
            return

        task["state"] = state
        self.SaveTask(task)

        if errormessage:
            self.NotifyClient("InternalError", task, errormessage)
        else:
            self.NotifyClient("StateUpdate", task)

        return



    # TODO: Move this to the upload manager
    def InitiateProcess(self, taskid, mimetype, contenttype, filesize, checksum, sourcefilename, initialstate):
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
            initialstate (str): The Initial state of this process. See :doc:`/taskmanagement/importmanager`.

        Raises:
            TypeError: When one of the arguments has not the expected type
            ValueError: When *contenttype* does not have the expected values
        """
        if type(taskid) != str:
            raise TypeError("Task ID must be of type string")
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
        if type(initialstate) != str:
            raise TypeError("Initial State must be of type string")

        # TODO: Only for Upload Processes!
        if len(self.cfg.uploads.allow) == 0:
            self.NotifyClient("InternalError", None, "Uploads deactivated")
            logging.warning("Uploads not allowed! \033[1;30m(See MusicDB Configuration: [uploads]->allow)")
            return
        if not contenttype in self.cfg.uploads.allow:
            self.NotifyClient("InternalError", None, "Upload of %s not allowed"%(contenttype))
            logging.warning("Uploads of %s not allowed! \033[1;30m(See MusicDB Configuration: [uploads]->allow)", contenttype)
            return

        fileextension   = self.uploaddirectory.GetFileExtension(sourcefilename)
        destinationname = contenttype + "-" + checksum + "." + fileextension
        uploadpath = self.cfg.directories.uploads + "/" + destinationname

        # TODO: Check if there is already a task with the given ID.
        # If this task is in waitforchunk state, the upload can be continued instead of restarting it.

        # Remove existing upload if destination path exists
        self.uploaddirectory.RemoveFile(uploadpath)  # Removes file when it exists
        
        # Create File
        with open(uploadpath, "w+b"):
            pass

        task = self.CreateNewTask()
        # General Data
        task["id"             ] = taskid
        task["state"          ] = initialstate
        task["contenttype"    ] = contenttype
        task["mimetype"       ] = mimetype
        # Upload Related
        task["filesize"       ] = filesize
        task["offset"         ] = 0
        task["sourcefilename" ] = sourcefilename
        task["sourcechecksum" ] = checksum
        task["uploadpath"     ] = uploadpath

        self.SaveTask(task)
        self.ScheduleTask(task)

        self.NotifyClient("ChunkRequest", task)
        return


    def ScheduleTask(self, task):
        """
        This method adds a new task into the list of tasks that will be processed by the :meth:`~musicdb.taskmanagement.managementthread.ManagementThread`.

        Args:
            task (dict): A new task

        Returns:
            *Nothing*
        """
        taskid = task["id"]

        global Tasks
        with TaskManagerLock:
            Tasks[taskid] = task



    def RemoveTask(self, taskid):
        """
        This method removed a task and all temporary data that belongs to it.
        It also removes the task from the tasks list.

        Temporary files are ``"uploadpath"``, ``"preprocessedpath"``

        Args:
            taskid (str): ID Of the task that shall be removed

        Returns:
            *Nothing*
        """
        task = self.GetTaskByID(taskid)
        logging.debug("Removing task \"%s\" including uploaded and temporary files.", task["id"])

        taskfile = task["id"] + ".json"
        datapath = task["uploadpath"]
        preppath = task["preprocessedpath"]

        if preppath:
            logging.debug("Removing %s", self.uploaddirectory.AbsolutePath(preppath))
            self.uploaddirectory.RemoveFile(preppath)

        if datapath:
            logging.debug("Removing %s", self.uploaddirectory.AbsolutePath(datapath))
            self.uploaddirectory.RemoveFile(datapath)

        global Tasks
        with TaskManagerLock:
            if taskid in Tasks:
                Tasks.pop(taskid)

        logging.debug("Removing %s", self.tasksdirectory.AbsolutePath(taskfile))
        self.tasksdirectory.RemoveFile(taskfile)
        return True




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

