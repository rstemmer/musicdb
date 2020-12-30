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

Upload states

    * ``"waitforchunk"``
    * ``"complete"``
"""

import logging
import datetime
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.filesystem     import Filesystem

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
    global Config
    global Thread
    global RunThread
    global Callbacks
    global TaskQueue

    filesystem = Filesystem(Config.uploads.tmpdir)

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
        self.tmpfs      = Filesystem(self.cfg.uploads.tmpdir)



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



    def NotifyClient(self, notification, task):
        """
        Args:
            notification (str): Name of the notification
            task (dict): Task structure

        Returns:
            *Nothing*

        Raises:
            ValueError: When notification has an unknown notification name
        """
        if not notification in ["ChunkRequest", "UploadComplete"]:
            raise ValueError("Unknown notification \"%s\""%(notification))

        status = {}
        status["uploadid"]  = task["id"]
        status["offset"]    = task["offset"]    # offset of the data to request
        status["chunksize"] = 4096*100          # Upload 400KiB (TODO: Make configurable)
        status["state"]     = task["state"]

        global Callbacks
        for callback in Callbacks:
            try:
                callback(notification, status)
            except Exception as e:
                logging.exception("A Upload Management event callback function crashed!")


    #####################################################################
    # Management Functions                                              #
    #####################################################################



    def InitiateUpload(self, uploadid, mimetype, filesize, checksum, sourcefilename):
        """
        Initiates an upload of a file into a MusicDB managed file space

        Args:
            uploadid (str): Unique ID to identify the upload task 
            mimetype (str): MIME-Type of the file (example: ``"image/png"``)
            filesize (int): Size of the complete file in bytes
            sourcefilename (str): File name (example: ``"test.png"``)
            checksum (str): SHA-1 check sum of the source file
        """
        # TODO: Check arguments
        task = {}
        task["id"             ] = uploadid
        task["filesize"       ] = filesize
        task["offset"         ] = 0
        task["mimetype"       ] = mimetype
        task["sourcefilename" ] = sourcefilename
        task["sourcechecksum" ] = checksum
        task["destinationpath"] = self.cfg.uploads.tmpdir + "/" + sourcefilename # TODO: Generate file name
        task["state"          ] = "waitforchunk"

        # TODO: Remove existing upload if destination path exists

        global TaskQueue
        TaskQueue[uploadid] = task

        self.NotifyClient("ChunkRequest", task)
        return



    def NewChunk(self, uploadid, rawdata, lastchunk=False):
        """
        Args:
            uploadid (str): Unique ID to identify the upload task
            rawdata (bytes): Raw data to append to the uploaded data

        Raises:
            TypeError: When *rawdata* is not of type ``bytes``
            TypeError: When *uploadid* is not of type ``str``
            ValueError: When *uploadid* is not included in the Task Queue
        """
        # TODO: Send Error Notifications
        # TODO: Check arguments
        if type(rawdata) != bytes:
            raise TypeError("raw data must be of type bytes. Type was \"%s\""%(str(type(rawdata))))
        if type(uploadid) != str:
            raise TypeError("Upload ID must be a string. Type was \"%s\""%(str(type(uploadid))))

        global TaskQueue
        if uploadid not in TaskQueue:
            logging.debug(TaskQueue)
            raise ValueError("Upload ID \"%s\" not in Task Queue.", str(uploadid))

        task      = TaskQueue[uploadid]
        chunksize = len(rawdata)
        filepath  = task["destinationpath"]

        # TODO: check permission of directory
        # TODO: check permission of file

        with open(filepath, "ab") as fd:
            fd.write(rawdata)

        task["offset"] += chunksize
        if task["offset"] >= task["filesize"]:
            # Upload complete
            self.UploadCompleted(task)
        else:
            # Get next chunk of data
            self.NotifyClient("ChunkRequest", task)
        return



    def UploadCompleted(self, task):
        """
        """
        # TODO: Check checksum
        task["state"] = "complete"
        logging.info("Upload Complete: \033[0;36m%s", task["destinationpath"]);
        self.NotifyClient("UploadComplete", task)
        return



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

