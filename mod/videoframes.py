# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module manages the video frames and previews of a video and caches several scaled versions of it.

Currently there is one main option: ``-u`` to update one (use ``--video`` or all video frames and previews.

.. attention::

    Updating all frames and preview may take a long time.

All files in the video frames directory that belong to the address video will be updated.
Existing files that follow the naming scheme for files affected by this update process will be overwritten.
Files that do not belog to the MusicDB-Workflow (like files added by the user) remain untouched.

If only one video shall be updated explicitly, it must be addressed by using the ``--video PATH`` option.

All new creates files were set to the ownership ``[music]->owner:[music]->group`` and get the permission ``rw-rw-r--``

.. attention::

    This module does not overwrite existing artworks.
    You have to delete the old files if you want to create new ones (for example after upgrading a video file).

Examples:

    Update the whole cache (Using :meth:`~mod.videoframes.videoframes.UpdateArtist`)

    .. code-block:: bash

        musicdb videoframes -u

    Update only for a new video (Using :meth:`~mod.videoframes.videoframes.UpdateVideo`)

    .. code-block:: bash

        musicdb artwork --video $Videopath -u

"""

import argparse
import logging
import os
from tqdm               import tqdm
from mdbapi.videoframes import VideoFrames
from lib.modapi         import MDBModule

class videoframes(MDBModule, VideoFrames):
    def __init__(self, config, database):
        VideoFrames.__init__(self, config, database)


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="do video frame and preview management")
        parser.set_defaults(module=modulename)
        parser.add_argument("--video",   action="store", type=str, default=None,
                help="Only update this video")

        parser.add_argument("-u", "--update",   action="store_true", help="update video frames and previews on the disk (may take a long time without --video option)")



    def UpdateVideos(self):
        """
        This method does an update for all artists in the music collection.

        Returns:
            *Nothing*
        """
        artists = self.db.GetAllArtists()
        print("\033[1;34mUpdating Video Frames and Previews\033[0;36m")
        for artist in tqdm(artists, unit="Artists"):
            videos = self.db.GetVideosByArtistId(artist["id"])
            for video in videos:
                retval = self.UpdateVideoFrames(video)
                if retval == False:
                    print("\033[1;31mGenerating video Frames and Preview failed for %s!\033[0m"%(video["path"]))



    def UpdateVideo(self, videopath):
        """
        This method does partial update. It updates only one video entry.

        This method expects absolute paths or paths relative to the music root directory.

        Args:
            videopath (str): Path to a video. This can be absolute or relative to the music directory.

        Return:
            ``True`` on success, otherwise ``False``
        """
        if type(videopath) is not str:
            print("\033[1;31mNo video path given!\033[0m")
            return False
        
        try:
            videopath = self.musicroot.AbsolutePath(videopath)  # First make userinput valid
            videopath = self.musicroot.RemoveRoot(videopath)    # Then try to get relative path
        except Exception as e:
            print("\033[1;31mInvalid video path: \"%s\". \033[0;31m(%s)\033[0m" % (videopath, str(e)))
            return False
        
        video = self.db.GetVideoByPath(videopath)
        if not video:
            print("\033[1;31mInvalid video path: \"%s\". \033[0;31m(No video with this path in database.)\033[0m" % (videopath))
            return False

        retval = self.UpdateVideoFrames(video)
        if retval == False:
            print("\033[1;31mGenerating video Frames and Preview failed!\033[0m")
            return False

        return True



    def MDBM_Main(self, args):
        # Make user paths absolute and check if they exist
        if args.video:
            args.video = os.path.abspath(args.video)
            if not os.path.exists(args.video):
                print("\033[1;31mERROR: Video path "+args.video+" does not exist!\033[0m")
                return 1

        # Update Cache and Manifest
        if args.update:
            if args.video:
                self.UpdateVideo(args.video)
            else:
                self.UpdateVideos()

        return 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

