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
This module organizes the import process of music inside the Music Directory into the MusicDB Database.
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


class ImportManager(TaskManager):
    """
    This class manages importing content from the Music Directory into the MusicDB Database.
    The class is derived from :class:`musicdb.taskmanagement.taskmanager.TaskManager`.
    
    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: (optional) A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        TaskManager.__init__(self, config, database)

        self.musicdirectory   = MusicDirectory(self.cfg)
        self.artworkdirectory = Filesystem(self.cfg.directories.artwork)
        self.fileprocessing   = Fileprocessing(self.cfg.directories.uploads)
        self.databasemanager  = MusicDBDatabase(config, database)



    # TODO: This may be useful to import any music from the file system that is already available
    #       and not recently uploaded.
    def InitiateImport(self):
        """
        """
        raise NotImplementedError



    def ImportMusic(self, task):
        """
        This method imports content from the Music Directory into the MusicDB Database.
        Depending on the *contenttype* different import methods are called:

            * ``"video"``: :meth:`~ImportVideo`

        The task must be in ``"startmusicimport"`` state, otherwise nothing happens but printing an error message.
        If post processing was successful, the task state gets updated to ``"importcomplete"``.
        When an error occurred, the state will become ``"invalidcontent"`` or ``"importfailed"``.

        Args:
            task (dict): the task object of an import-task

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if task["state"] != "startmusicimport":
            logging.error("The task %s must be in \"startmusicimport\" state for importing. Actual state was \"%s\". \033[1;30m(Such a mistake should not happen. Anyway, the task won\'t be further processed and nothing bad will happen.)", task["id"], task["state"])
            return False

        # Perform music import
        self.UpdateTaskState(task, "importingmusic")
        success = False
        if task["contenttype"] == "video":
            logging.debug("Importing Video %s", task["videofile"])
            success = self.ImportVideo(task)
        else:
            logging.warning("Unsupported content type to import: \"%s\" \033[1;30m(Content will be ignored)", str(task["contenttype"]))
            self.UpdateTaskState(task, "invalidcontent", "Unsupported content type")
            return False

        # Update task state
        if success == True:
            logging.debug("Import succeeded");
            newstate = "startartworkimport"
        else:
            newstate = "importfailed"

        self.UpdateTaskState(task, newstate)
        return success




    def ImportVideo(self, task):
        """
        Task state must be ``"startimport"`` and content type must be ``"video"``

        Returns:
            ``True`` on success.
        """
        logging.error("The Import Video Process needs to be reviewed!") # FIXME
        # Check task state and type
        if task["state"] != "startimport":
            logging.warning("Cannot import an upload that is not in \"startimport\" state. Upload with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return False

        success = False
        if task["contenttype"] != "video":
            logging.warning("Video expected. Actual type of upload: \"%s\" \033[1;30m(No video will be imported)", str(task["contenttype"]))
            return False

        # Get important information
        try:
            artistname = task["annotations"]["artistname"]
            videopath  = task["videofile"]
        except KeyError as e:
            logging.error("Collecting video information for importing failed with key-error for: %s \033[1;30m(Make sure the artist name is annotated to the upload)", str(e))
            return False

        # Check if the artist already exists in the database - if not, add it
        artist = self.db.GetArtistByPath(artistname)
        if artist == None:
            logging.info("Importing new artist: \"%s\"", artistname)
            try:
                self.dbmanager.AddArtist(artistname)
            except Exception as e:
                logging.error("Importing artist \"%s\" failed with error: %s \033[1;30m(Video upload canceled)", str(artistname), str(e))
                self.NotifyClient("InternalError", task, "Importing artist failed")
                return False
            artist = self.db.GetArtistByPath(artistname)

        # Import video
        try:
            success = self.dbmanager.AddVideo(videopath, artist["id"])
        except Exception as e:
            logging.error("Importing video \"%s\" failed with error: %s \033[1;30m(Video upload canceled)", str(videopath), str(e))
            self.NotifyClient("InternalError", task, "Importing video failed")
            return False

        if not success:
            logging.error("Importing video \"%s\" failed. \033[1;30m(Video upload canceled)", str(videopath), str(e))
            self.NotifyClient("InternalError", task, "Importing video failed")
            return False

        # Add origin information to database if annotated
        try:
            origin = task["annotations"]["origin"]
        except KeyError as e:
            pass
        else:
            video = self.db.GetVideoByPath(videopath)
            video["origin"] = origin
            self.db.WriteVideo(video)

        logging.info("Importing Video succeeded")
        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

