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
The task management is responsible for managing
    * Uploads new content to the server (:doc:`/taskmanagement/uploadmanager`)
    * Integration of new content into the Music Directory (:doc:`/taskmanagement/integrationmanager`)
    * Import of music into the MuiscDB Database (:doc:`/taskmanagement/importmanager`)
    * Importing artwork for an album (:doc:`/taskmanagement/artworkmanager`)
    * Scanning the file system for new or invalid data (:doc:`/taskmanagement/filesystemmanager`)

The whole process is split into several tasks managed by the :meth:`~TaskManagementThread`.

The communication is handled via notification to allow continuing reporting of status updates
without blocking and even when the connection gets lost in the meanwhile.

Furthermore uploading a file, integrating it into the music directory and importing it into the Music Database
is possible in separate steps.

The whole process is split into several tasks. Each task has its own state.
The task state is persistently stored inside the uploads directory within a JSON file in a *tasks* sub-directory.
The file name is the task ID (equivalent to the Upload ID) + ``.json``.

Possible Task states:

    * Unrelated states
        * ``"new"``: A new created, not yet initialized task.
        * ``"notexisting"`` In case a Task ID does not match any file. This task does not exist.
        * ``"invalidcontent"``: Processing failed. The content type was unexpected or invalid (Not: artwork, video, album).
        * ``"remove"``: Upload is going to be removed. The task itself as well. After this state appears, the task ID should no longer be considered as valid.
    * Upload related states:
        * ``"waitforchunk"``: A new chunk of data was requested, and is expected from the client
        * ``"uploadfailed"``: The upload failed
        * ``"uploadcomplete"``: The whole file is now available in the temporary upload directory and is ready for being preprocessed.
        * ``"preprocessing"``: The file is currently in preprocessing state. For example if an archive gets unpacked.
    * Integration related states:
        * ``"readyforintegration"``: The integration of the file can be started
        * ``"startintegration"``: Start the integration process
        * ``"integrating"``: The integration process has started
        * ``"integrationfailed"``: Integrating the uploaded file into the music directory failed
    * Import related states:
        * ``"readyforimport"``: The uploaded file was successfully integrated into the music directory. The content can now be imported into the MusicDB Database. Everything is now based on file management inside the managed Music Directory. From this state, ``"remove"`` gets triggered.
        * ``"startmusicimport"``: Importing the integrated file into the music database started
        * ``"importingmusic"``: The music import process has started
        * ``"importfailed"``: Import process failed (importing the music or generating the artwork)
        * ``"startartworkimport"``: Importing succeeded and generating the artwork started
        * ``"importingartwork"``: The artwork import process has started
        * ``"importcomplete"``: Import process complete and successful
    * File system scanning states:
        * ``"startfsscan"``:
        * ``"scanningfs"``:
        * ``"fsscanfailed"``:
        * ``"fsscancomplete"``:

To each task, there are several additional information, also stored in the JSON file.
The following keys are in dictionary that represent a task:

    * Unrelated information
        * ``"id"`` (str): The task ID
        * ``"state"`` (str): One of the task states listed above
        * ``"contenttype"`` (str): Type of the content: (``"video"``, ``"albumfile"``, ``"artwork"``, ``"any"``). An album file can a song but also a booklet PDF, a video clip or any other additional content of an album.
        * ``"mimetype"`` (str): MIME-Type of the file (For example ``"image/png"``)
        * ``"annotations"`` (dict): Additional annotations that can be provided by the user and be optionally used by some task processing.
        * ``"initializationtime"`` (int): The unix time stamp when the task has been created
        * ``"updatetime"`` (int): Unix time stamp when the task has been updated the last time via :meth:`~musicdb.taskmanagement.taskmanager.TaskManager.UpdateTaskState`. After initialization it is ``None``.
    * Upload related information (May not be valid if there was no upload task)
        * ``"filesize"`` (int): The size of the file in Bytes
        * ``"offset"`` (int): The amount of existing bytes of a file that is currently being uploaded.
        * ``"uploadpath"`` (str): Path of the file in that the uploaded data gets written to Relative to the Upload Directory.
        * ``"preprocessedpath"`` (str): Path of preprocessed data. If available, it should be preferred to ``"uploadpath"``. The path is relative to the Upload directory.
        * ``"sourcefilename"`` (str): Name of the original file that got uploaded.
        * ``"sourcechecksum"`` (str): Checksum of the original file that got uploaded.
    * Integration related information (May not be valid if the file is not yet integrated into the Music Directory)
        * ``"videopath"`` (str): Path to a video file, relative to the Music Directory
        * ``"albumpath"`` (str): Path to an album directory, relative to the Music Directory
        * ``"albumfilepath"`` (str): Path to file of an album, relative to the Music Directory
    * Artwork related
        * ``"awsourcetype"`` (str): Type of the artwork source: ``"imagefile"``, ``"songfile"`` or ``"videofile"``.
        * ``"awsourcepath"`` (str): Path to the artwork source

After upload is complete,
the Management Thread takes care about post processing or removing no longer needed content
The uploaded file follows the following naming scheme: *contenttype* + ``-`` + *checksum* + ``.`` + source-file-extension
The upload manager also takes care about the validity of the uploaded file (via SHA-1 checksum).

After an import is completed successfully, all clients connected to the server get a ``"sys:refresh"`` notification
to update their caches.
This notification is generated via :meth:`musicdb.mdbapi.server.UpdateCaches`.
"""
# TODO: Visualize state machine
# TODO: Module description: move upload details into upload module
# TODO: Make globals thread safe

import time
import logging
import threading
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
import musicdb.mdbapi.server    as server

from musicdb.taskmanagement.taskmanager     import TaskManager
from musicdb.taskmanagement.uploadmanager   import UploadManager
from musicdb.taskmanagement.integrationmanager  import IntegrationManager
from musicdb.taskmanagement.importmanager   import ImportManager
from musicdb.taskmanagement.artworkmanager  import ArtworkManager
from musicdb.taskmanagement.filesystemmanager   import FilesystemManager

Config      = None
Thread      = None
RunThread   = False

def StartTaskManagementThread(config, musicdb):
    """
    This method starts the task management thread.

    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

    Returns:
        ``True`` on Success, otherwise ``False``

    Raises:
        TypeError: When the arguments are not of the correct type.
    """
    global Config
    global Thread
    global RunThread

    if Thread != None:
        logging.warning("Task Management Thread already running")
        return False

    if type(config) != MusicDBConfig:
        raise TypeError("config argument not of type MusicDBConfig")
    if type(musicdb) != MusicDatabase:
        raise TypeError("database argument not of type MusicDatabase")


    logging.debug("Starting Task Management Thread")
    Config    = config
    RunThread = True
    Thread    = threading.Thread(target=TaskManagementThread)
    Thread.start()

    return True



def StopTaskManagementThread():
    """
    This function stops the Task Management Thread.
    The function is blocking and waits until the thread is closed.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global RunThread
    global Thread

    if Thread == None:
        logging.warning("There is no Task Management Thread running!")
        return False

    logging.debug("Waiting for Task Management Thread to stop…")

    RunThread = False
    Thread.join()
    Thread = None

    logging.debug("Task Management Thread shut down.")
    return True



def TaskManagementThread():
    """
    This thread handles the upload, integration and import process.
    It maintains the storage of temporary data and allows asynchronous file management and importing.
    """
    # TODO: Remove left over uploads (uploaded files without task-ID)
    # TODO: Continue uploads that were interrupted
    # TODO: Identify discontinued uploads
    # TODO: Handle failed uploads (clean up)
    global Config
    global Thread
    global RunThread

    try:
        musicdb         = MusicDatabase(Config.files.musicdatabase)
        taskmanager     = TaskManager(Config, musicdb)
        uploadmanager   = UploadManager(Config, musicdb)
        integrationmanager = IntegrationManager(Config, musicdb)
        importmanager   = ImportManager(Config, musicdb)
        artworkmanager  = ArtworkManager(Config, musicdb)
        filesystemmanager  = FilesystemManager(Config, musicdb)
    except Exception as e:
        logging.exception("Initializing Task Management Thread failed with exception: %s", str(e))

    # TODO: Import and integration may be allowed!
    if len(Config.uploads.allow) == 0:
        logging.warning("No Uploads Allowed! \033[1;30m(See MusicDB Configuration: [uploads]->allow)")

    # Start processing …
    while RunThread:
        # Sleep a bit to reduce the load on the CPU. If nothing to do, sleep a bit longer
        tasks = taskmanager.GetTasks()
        if len(tasks) > 0:
            time.sleep(0.01)
        else:
            time.sleep(1)

        deletekeys = []
        # Process all tasks
        for taskid, task in tasks.items():
            #logging.debug("Processing task %s in state %s", task["id"], task["state"])

            # Remove tasks older than 24h
            try:
                age = CalculateAge(task)
                if(age > 24*60*60): # older than 24h
                    logging.warning("Task \"%s\" is older than 24h. Most likely there went something wrong with this task. \033[1;30m(Task will be removed)", task["id"])
                    taskmanager.UpdateTaskState(task, "remove");
            except Exception as e:
                logging.exception("Checking age of task (ID: %s) failed with exception: %s \033[1;30m(Task will be removed, its files remain.)", str(taskid), str(e))

            # Process task
            try:
                keeptask = ProcessTask(taskid, task,
                        taskmanager,
                        uploadmanager,
                        integrationmanager,
                        importmanager,
                        artworkmanager,
                        filesystemmanager)
                if not keeptask:
                    deletekeys.append(taskid)
            except Exception as e:
                logging.exception("Processing task (ID: %s) failed with exception: %s \033[1;30m(Task will be removed, its files remain.)", str(taskid), str(e))

        # Remove all deleted tasks
        for taskid in deletekeys:
            try:
                taskmanager.RemoveTask(taskid)
            except Exception as e:
                logging.exception("Removing task (ID: %s) failed with exception: %s \033[1;30m(Oh.)", str(taskid), str(e))

    return



def CalculateAge(task):
    """
    This method calculates how old the task is (in seconds).
    If the task is new created (``"updatetime"`` is ``None``), ``0`` gets returned.

    Args:
        task (dict): Task dictionary

    Returns:
        age as integer in seconds
    """
    lastupdate = task["updatetime"]
    if type(lastupdate) != int:
        return 0

    currenttime = int(time.time())
    return currenttime - lastupdate



def ProcessTask(taskid, task, taskmanager, uploadmanager, integrationmanager, importmanager, artworkmanager, filesystemmanager):
    """
    After an import is completed successfully, all clients connected to the server get a ``"sys:refresh"`` notification
    to update their caches.
    This notification is generated via :meth:`musicdb.mdbapi.server.UpdateCaches`.

    Returns:
        ``True`` when the processing can continue. ``False`` when the task with taskid can be removed from the list of tasks
    """
    state       = task["state"]
    contenttype = task["contenttype"]
    #logging.debug("Task with state \"%s\" found. (%s)", str(state), str(contenttype));

    # Check if the tasks still exists in the file system.
    # Remove if not, because the user may have removed that file for a purpose
    # Note that updating the task state to "remove" will recreate the removed task file!
    if not taskmanager.ExistsTaskFile(task):
        taskmanager.UpdateTaskState(task, "remove")
        logging.info("Found task did not exist as file in the tasks directory anymore. Task will be removed.");

    # Check if there are some things to do to proceed with the task
    if state == "uploadcomplete":
        uploadmanager.PreProcessUploadedFile(task)

    elif state == "readyforintegration":
        # further steps should be triggered by the user!
        pass

    elif state == "startintegration":
        integrationmanager.IntegrateUploadedFile(task)

    elif state == "readyforimport":
        # further steps should be triggered by the user!
        # From this moment on, the task manager is no longer needed.
        # Everything is now based on file management inside the managed Music Directory
        taskmanager.UpdateTaskState(task, "remove")

    elif state == "startmusicimport":
        importmanager.ImportMusic(task)

    elif state == "startartworkimport":
        artworkmanager.ImportArtwork(task)

    elif state == "importcomplete":
        server.UpdateCaches(); # Trigger all Clients to update their caches

    elif state == "startfsscan":
        filesystemmanager.ScanFilesystem(task)

    elif state == "remove":
        return False

    # Now check if the task can be removed
    if state in ["uploadfailed", "importfailed", "importcomplete", "invalidcontent", "fsscanfailed", "fsscancomplete"]:
        taskmanager.UpdateTaskState(task, "remove")

    return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

