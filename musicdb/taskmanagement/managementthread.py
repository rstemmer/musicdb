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
The import management is responsible for managing Uploads, Integration and Import of music into the MuiscDB system.
The whole process is split into several tasks managed by the :meth:`~TaskManagementThread`.

The communication is handled via notification to allow continuing uploading even when the connection gets lost in the meanwhile.

Furthermore uploading a file, integrating it into the music directory and importing it into the Music Database
shall be possible in separate steps.

The upload is performed chunk-wise.
After initiating an Upload, this upload manager (:doc:`/mdbapi/uploadmanager`)
requests chunks of data via MusicDB Notifications from the clients.
All clients are informed about the upload process, not only the client that initiated the upload.
So each client can show the progress and state.

The whole process is split into several tasks. Each task has its own state.
The task state is persistently stored inside the uploads directory within a JSON file in a *tasks* sub-directory.
The file name is the task ID (equivalent to the Upload ID) + ``.json``.

Possible Task states:

    * Unrelated states
        * ``"notexisting"`` In case a Task ID does not match any file. This task does not exist.
        * ``"invalidcontent"``: Processing failed. The content was unexpected or invalid.
        * ``"remove"``: Upload is going to be removed. The task itself as well. After this state appears, the task ID should no longer be considered as valid.
    * Upload related states:
        * ``"waitforchunk"``: A new chunk of data was requested, and is expected from the client
        * ``"uploadcomplete"``: The whole file is now available in the temporary upload directory
        * ``"uploadfailed"``: The upload failed
        * ``"preprocessed"``: The uploaded file was successfully pre-processed and is ready for integration or importing
    * Integration related states:
        * ``"integrated"``: The uploaded file was successfully integrated into the music directory
        * ``"integrationfailed"``: Integrating the uploaded file into the music directory failed
    * Import related states:
        * ``"startimport"``: Importing the integrated file into the music database started
        * ``"importfailed"``: Import process failed (importing the music or generating the artwork)
        * ``"importartwork"``: Importing succeeded and generating the artwork started
        * ``"importcomplete"``: Import process complete and successful

To each task, there are several additional information, also stored in the JSON file.
The following keys are in dictionary that represent a task:

    * Unrelated information
        * ``"id"`` (str): The task ID
        * ``"state"`` (str): One of the task states listed above
        * ``"contenttype"`` (str): Type of the content: (``"video"``, ``"album"``, ``"artwork"``)
        * ``"mimetype"`` (str): MIME-Type of the file (For example ``"image/png"``)
        * ``"annotations"`` (dict): Additional annotations that can be provided by the user and be optionally used by some task processing.
    * Upload related information (May not be valid if there was no upload task)
        * ``"filesize"`` (int): The size of the file in Bytes
        * ``"offset"`` (int): The amount of existing bytes of a file that is currently being uploaded.
        * ``"uploadpath"`` (str): Path of the file in that the uploaded data gets written to Relative to the Upload Directory.
        * ``"preprocessedpath"`` (str): Path of preprocessed data. If available, it should be preferred to ``"uploadpath"``. The path is relative to the Upload directory.
        * ``"sourcefilename"`` (str): Name of the original file that got uploaded.
        * ``"sourcechecksum"`` (str): Checksum of the original file that got uploaded.
    * Integration related information (May not be valid if the file is not yet integrated into the Music Directory)
        * ``"videopath"`` (str): Path to a video file, relative to the Music Directory

After upload is complete,
the Management Thread takes care about post processing or removing no longer needed content
The uploaded file follows the following naming scheme: *contenttype* + ``-`` + *checksum* + ``.`` + source-file-extension
The upload manager also takes care about the validity of the uploaded file (via SHA-1 checksum).

"""
# TODO: Visualize state machine
# TODO: Module description: move upload details into upload module
# TODO: Make globals thread safe

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

from musicdb.taskmanagement.taskmanager     import TaskManager
from musicdb.taskmanagement.uploadmanager   import UploadManager

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
        filesystem      = Filesystem(Config.directories.uploads)
        taskmanager     = TaskManager(Config, musicdb)
        uploadmanager   = UploadManager(Config, musicdb)
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
            time.sleep(1)
        else:
            time.sleep(1)

        deletekeys = []
        for taskid, task in tasks.items():
            try:
                keeptask = ProcessTask(taskid, task, taskmanager, uploadmanager)
                if not keeptask:
                    deletekeys.append(taskid)
            except Exception as e:
                logging.exception("Processing task (ID: %s) failed with exception: %s \033[1;30m(Task will be removed, its files remain.)", str(taskid), str(e))

        # Remove all deleted tasks
        for taskid in deletekeys:
            taskmanager.RemoveTask(taskid)
    return



def ProcessTask(taskid, task, taskmanager, uploadmanager):
    """
    Returns:
        ``True`` when the processing can continue. ``False`` when the task with taskid can be removed from the list of tasks
    """
    state       = task["state"]
    contenttype = task["contenttype"]
    logging.debug("Task with state \"%s\" found. (%s)", str(state), str(contenttype));

    if state == "uploadfailed" or state == "importfailed" or state == "importcomplete":
        if contenttype in ["artwork"]:
            taskmanager.UpdateTaskState(task, "remove")

    elif state == "uploadcomplete":
        uploadmanager.PreProcessUploadedFile(task)

    elif state == "startimport":
        if contenttype == "video":
            success = uploadmanager.ImportVideo(task)
        elif contenttype == "artwork":
            success = uploadmanager.ImportArtwork(task)
        else:
            logging.error("Invalid content type \"%s\". \033[1;30m(forcing state importfailed)", contenttype);
            success = False

        # TODO: This should be done by the manager class
        if success:
            if contenttype in ["album", "video"]:
                task["state"] = "importartwork"
            else:
                task["state"] = "importcomplete"
            uploadmanager.SaveTask(task)
            uploadmanager.NotifyClient("StateUpdate", task)
        else:
            uploadmanager.UpdateState(task, "importfailed")

    elif state == "importartwork":
        if contenttype == "video":
            success = uploadmanager.ImportVideoArtwork(task)
        else:
            logging.error("Invalid content type \"%s\". \033[1;30m(forcing state importfailed)", contenttype);
            success = False

        # TODO: This should be done by the manager class
        if success:
            uploadmanager.UpdateState(task, "importcompleted")
        else:
            uploadmanager.UpdateState(task, "importfailed")

    elif state == "remove":
        # Different manager may have to perform further tasks
        #taskmanager.RemoveTask(task)
        return False

    return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

