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
from musicdb.mdbapi.music               import MusicDBMusic
from musicdb.taskmanagement.taskmanager import TaskManager


class FilesystemManager(TaskManager):
    """
    This class manages all files and directories inside the MusicDB Music Directory.
    It can be used to scan for new files or find lost connections between database entries and files.

    This class is derived from :class:`musicdb.taskmanagement.taskmanager.TaskManager`.
    
    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        TaskManager.__init__(self, config, database)

        self.musicdirectory   = MusicDirectory(self.cfg)
        self.music            = MusicDBMusic(self.cfg, self.db);



    def InitiateFilesystemScan(self):
        """
        This method initiates a file system scan.
        It sets the task state to ``"startfsscan"`` and the content type to ``"any"``.

        Args:
            taskid (str): ID of the task that performed the upload
            targetpath (str): Path relative to the music directory

        Returns:
            The task ID as string or ``None`` if something failed.

        Raises:
            TypeError: When one of the parameters are of a wrong data type
            ValueError: When one of the parameters has an unexpected value
        """
        task = self.CreateNewTask()
        task["state"]       = "startfsscan"
        task["contenttype"] = "any"

        self.SaveTask(task)
        self.ScheduleTask(task)
        return task["id"]



    def ScanFilesystem(self, task):
        """
        This method scans the file system for lost and new paths.
        It does the following steps:

        #. Check all database entries if the associated files and directories can be found via :meth:`musicdb.mdbapi.music.MusicDBMusic.FindLostPaths`
        #. If not, collect their database entry
        #. Find all new files and directories via :meth:`musicdb.mdbapi.music.MusicDBMusic.FindNewPaths`
        #. Collect their path and check sum (this may take some time)

        * ``"newpaths"``
            * ``"artists"``, ``"albums"``, ``"songs"``, ``"filteredsongs"``, ``"videos"``
                * Each entry is a list of dictionaries
                * All dictionaries have the entry `"path"`
                * for `"songs"` and `"videos"` one entry is `"checksum"`
        * ``"lostpaths"``
            * ``"artists"``, ``"albums"``, ``"songs"``, ``"videos"``
                * Each entry is a list of database entries as dictionary

        The found information are annotated to the task

        """
        if task["state"] != "startfsscan":
            logging.error("The task %s must be in \"startfsscan\" state for scanning the file system. Actual state was \"%s\". \033[1;30m(Such a mistake should not happen. Anyway, the task won\'t be further processed and nothing bad will happen.)", task["id"], task["state"])
            return False

        self.UpdateTaskState(task, "scanningfs")
        logging.debug("Start scanning file system for new and lost paths");

        success = True

        # Scan for lost paths
        try:
            lostpaths = self.music.FindLostPaths()
        except Exception as e:
            success = False
            logging.warning("Scanning for lost paths failed with error \"%s\"", str(e))

        # Scan for new paths
        try:
            newpaths  = self.FindNewPaths()
        except Exception as e:
            success = False
            logging.warning("Scanning for new paths failed with error \"%s\"", str(e))

        # Response to clients
        if success == True:
            logging.debug("File system scanning succeeded");
            retval = {}
            retval["lostpaths"] = lostpaths
            retval["newpaths"]  = newpaths

            task["annotations"] = retval
            newstate = "fsscancomplete"
        else:
            logging.debug("File system scanning failed");
            newstate = "fsscanfailed"

        self.UpdateTaskState(task, newstate)
        return success



    def FindNewPaths(self):
        """
        This method scans the file systems for new paths via :meth:`musicdb.mdbapi.music.MusicDBMusic.FindNewPaths`.
        If a new path is a file, its checksum gets calculated so that the file can be compared to existing database entries.

        The returned dictionary has the following structure:

        * ``"artists"``, ``"albums"``, ``"songs"``, ``"videos"`` each a list of further dictionaries
        * These dictionaries have a key ``"path"`` with paths relative to the Music Directory
        * Song and Video entries have a key ``"checksum"`` that contains the checksum of the files for comparing them with the database entries

        Return:
            A dictionary with lists as described above

        """
        newpaths = self.music.FindNewPaths()

        def MakeDict(pathlist):
            infolist = []
            for path in pathlist:
                info = {}
                info["path"] = path
                if self.musicdirectory.IsFile(path):
                    try:
                        info["checksum"] = self.musicdirectory.Checksum(path)
                    except:
                        pass
                infolist.append(info)
            return infolist

        newpathinfos = {}
        newpathinfos["artists"] = MakeDict(newpaths["artists"])
        newpathinfos["albums"]  = MakeDict(newpaths["albums"])
        newpathinfos["songs"]   = MakeDict(newpaths["songs"])
        newpathinfos["filteredsongs"]   = MakeDict(newpaths["filteredsongs"])
        newpathinfos["videos"]  = MakeDict(newpaths["videos"])
        return newpathinfos

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

