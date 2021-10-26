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
This module organizes the import process of artwork the MusicDB Database.
"""

import logging
from pathlib            import Path
from PIL                import Image
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.fileprocessing import Fileprocessing
from musicdb.mdbapi.database    import MusicDBDatabase
from musicdb.mdbapi.artwork     import MusicDBArtwork
from musicdb.mdbapi.videoframes import VideoFrames
from musicdb.mdbapi.musicdirectory      import MusicDirectory
from musicdb.taskmanagement.taskmanager import TaskManager


class ArtworkManager(TaskManager):
    """
    This class manages importing artwork.
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



    # TODO: This may be useful to import any artwork from the file system that is already available
    #       and not recently uploaded.
    def InitiateImport(self):
        """
        """
        raise NotImplementedError



    def ImportArtwork(self, task):
        """
        This method imports artwork from the download directory or from an integrated or imported music file.
        Depending on the *contenttype* different import methods are called:

            * ``"video"``: :meth:`~ImportVideoArtwork` - Import from video file
            * ``"artwork"``: :meth:`~ImportArtworkFromUpload` - Import from upload directory

        The task must be in ``"startartworkimport"`` state, otherwise nothing happens but printing an error message.
        If post processing was successful, the task state gets updated to ``"importcomplete"``.
        When an error occurred, the state will become ``"invalidcontent"`` or ``"importfailed"``.

        Args:
            task (dict): the task object of an import-task

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if task["state"] != "startartworkimport":
            logging.error("The task %s must be in \"startartworkimport\" state for importing. Actual state was \"%s\". \033[1;30m(Such a mistake should not happen. Anyway, the task won\'t be further processed and nothing bad will happen.)", task["id"], task["state"])
            return False

        # Perform artwork import
        self.UpdateTaskState(task, "importingartwork")
        success = False
        if task["contenttype"] == "video":
            logging.debug("Importing Artwork from Video File: %s", task["videofile"])
            success = self.ImportVideoArtwork(task)
        elif task["contenttype"] == "artwork":
            logging.debug("Importing Artwork from Upload Directory: %s", task["artworkfile"])
            success = self.ImportArtworkFromUpload(task)
        else:
            logging.warning("Unsupported content type to import: \"%s\" \033[1;30m(Content will be ignored)", str(task["contenttype"]))
            self.UpdateTaskState(task, "invalidcontent", "Unsupported content type")
            return False

        # Update task state
        if success == True:
            logging.debug("Artwork Import succeeded");
            newstate = "importcomplete"
        else:
            newstate = "importfailed"

        self.UpdateTaskState(task, newstate)
        return success



    def ImportVideoArtwork(self, task):
        """
        Returns:
            ``True`` on success
        """
        logging.error("The Import Video Process needs to be reviewed!") # FIXME
        # Check task state and type
        if task["state"] != "importvideoartwork":
            logging.warning("Cannot import artwork that is not in \"importvideoartwork\" state. Upload with ID \"%s\" was in \"%s\" state! \033[1;30m(Nothing will be done)", str(task["id"]), str(task["state"]))
            return False

        if task["contenttype"] != "video":
            logging.warning("Video expected. Actual type of upload: \"%s\" \033[1;30m(No video will be imported)", str(task["contenttype"]))
            return False

        # Start generating the artworks
        videopath    = task["videofile"]
        framemanager = VideoFrames(self.cfg, self.db)

        video = self.db.GetVideoByPath(videopath)
        if not video:
            logging.error("Getting video \"%s\" from database failed. \033[1;30m(Artwork import canceled)", str(videopath), str(e))
            self.NotifyClient("InternalError", task, "Video artwork import failed")
            return False

        retval = framemanager.UpdateVideoFrames(video)
        if retval == False:
            logging.error("Generating video frames and preview failed for video \"%s\". \033[1;30m(Artwork import canceled)", str(videopath))
            self.NotifyClient("InternalError", task, "Video artwork import failed")
            return False

        logging.info("Importing Video thumbnails and previews succeeded")
        return True



    def ImportArtworkFromUpload(self, task):
        """
        This method performs the artwork import from an uploaded file.
        It loads the files into the MusicDB Artwork Directory and updates the corresponding MusicDB Database entries.

        This method can be called indirectly by calling :meth:`~ImportArtwork` or directly (For example from the MusicDB WebSocket API).

        This method expects that the state of the task is ``"importingartwork"`` or ``"readyforintegration"`` as well as the content type of ``"artwork"``.
        If one of those values is not correct, the method logs an error and returns with ``False``.

        Args:
            task (dict): The task dictionary

        Returns:
            ``True`` on success.
        """
        # Check task state and type - This should have been checked by ImportArtwork already
        if task["state"] not in ["importingartwork", "readyforintegration"]:
            logging.error("Unexpected state of task %s. Expected was \"importingartwork\" or \"readyforintegration\". Actual state was \"%s\"! \033[1;30m(Artwork will not be imported)", task["id"], task["state"])
            self.UpdateTaskState(task, "importfailed")
            return False

        if task["contenttype"] != "artwork":
            logging.error("Unexpected content type of task %s. Expected was \"artwork\". Actual content type was \"%s\"! \033[1;30m(Artwork will not be imported)", task["id"], task["contenttype"])
            self.UpdateTaskState(task, "importfailed")
            return False

        if task["state"] == "readyforintegration":
            self.UpdateTaskState(task, "importingartwork")

        # Get important information
        # TODO: if album ID is given, the other values can be obtained from the database
        try:
            artistname = task["annotations"]["artistname"]
            albumname  = task["annotations"]["albumname"]
            albumid    = task["annotations"]["albumid"]
            sourcepath = task["preprocessedpath"]
        except KeyError as e:
            logging.error("Collecting artwork information for importing failed with key-error for: %s \033[1;30m(Make sure the artist and album name is annotated as well as the album ID.)", str(e))
            self.UpdateTaskState(task, "importfailed")
            return False

        # Import artwork
        awmanager   = MusicDBArtwork(self.cfg, self.db)
        artworkname = awmanager.CreateArtworkName(artistname, albumname)
        success     = awmanager.SetArtwork(albumid, sourcepath, artworkname)

        if not success:
            logging.error("Importing artwork \"%s\" failed. \033[1;30m(Artwork import canceled)", str(sourcepath))
            self.NotifyClient("InternalError", task, "Importing artwork failed")
            self.UpdateTaskState(task, "importfailed")
            return False

        logging.info("Importing Artwork succeeded")
        self.UpdateTaskState(task, "importcomplete")
        return True




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
