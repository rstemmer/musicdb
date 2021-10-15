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
This module takes care of the WebUI configuration.

The following sections and keys are available:

    .. code-block:: ini

        [meta]
        version=3

        [WebUI]
        videomode=disabled
        lyrics=enabled
        showstreamplayer=False

        [ArtistsView]
        showrelease=True

        [GenreSelectionView]
        showother=True

        [Stream]
        url=http://127.0.0.1:8000/stream
        username=
        password=

        [debug]
        blurartwork=false

[meta]->version (integer):
    Version of the configuration scheme

[WebUI]->videomode (string: ``"enabled"``, ``"disabled"``):
    Defines if the video mode should be present in the WebUI or not.
    This includes, but is not limited to, the buttons of the main menu

[WebUI]->lyrics (string: ``"enabled"``, ``"disabled"``):
    Defines if lyrics should be present in the WebUI or not.
    This includes, but is not limited to, the lyrics state buttons in the Song Lists of the albums

[WebUI]->showstreamplayer (boolean):
    If True, then the MusicDB audio stream player is shown in the main menu.
    This player can them be used to connect to the audio stream from the WebUI.

[ArtistsView]->showrelease (boolean):
    If true, the release date of an album is shown next to its name.
    If false, the release date will not be shown.
    In any case, the albums of an artist are sorted by their release date.

[GenreSelectionView]->showother (boolean):
    If true, the default genre "Other" will be listed.

[Stream]->url,username,password (strings):
    Access data to the audio stream that gets managed by MusicDB.
    If the stream is not protected by the authentication methods of Icecast,
    no user name or password is required.

[debug]->blurartwork (boolean):
    If true, all artworks are blurred.
    This is useful to avoid copyright violations on screenshots that shall be public available

"""

from musicdb.lib.cfg.config import Config
import time
import logging
import os


class WebUIConfig(Config):
    """
    This class holds the configuration for the WebUI.

    Args:
        path: Absolute path to the WebUI configuration file
    """

    def __init__(self, path):

        Config.__init__(self, path)

        version = self.Get(int, "meta", "version", 0)
        if version < 1:
            logging.info("Creating webui.ini")
            self.Set("meta",  "version",     1)
            self.Set("WebUI", "videomode",   "disabled")
            self.Set("WebUI", "lyrics",      "enabled")
            self.Set("debug", "blurartwork", False)
        if version < 2:
            logging.info("Updating webui.ini to version 2")
            self.Set("meta",  "version",     2)
            self.Set("ArtistsView",        "showrelease", True)
            self.Set("GenreSelectionView", "showother",   True)
        if version < 3:
            logging.info("Updating webui.ini to version 3")
            self.Set("meta",  "version",     3)
            self.Set("WebUI", "showstreamplayer", False)
            self.Set("Stream","url",        "http://127.0.0.1:8000/stream")
            self.Set("Stream","username",   "")
            self.Set("Stream","password",   "")



    def LoadConfig(self):
        """
        This method loads the current WebUI configuration and returns them in a dictionary.

        Returns:
            dict with the whole WebUI configuration
        """
        cfg = {}
        cfg["meta"] = {}
        cfg["meta"]["version"] = self.Get(int,  "meta",  "version",     0)

        cfg["WebUI"] = {}
        cfg["WebUI"]["videomode"]   = self.Get(str,  "WebUI", "videomode",   "disabled")
        cfg["WebUI"]["lyrics"]      = self.Get(str,  "WebUI", "lyrics",      "enabled")
        cfg["WebUI"]["showstreamplayer"]    = self.Get(bool,  "WebUI", "showstreamplayer",   "False")

        cfg["ArtistsView"] = {}
        cfg["ArtistsView"]["showrelease"] = self.Get(bool, "ArtistsView", "showrelease", True)

        cfg["GenreSelectionView"] = {}
        cfg["GenreSelectionView"]["showother"] = self.Get(bool, "GenreSelectionView", "showother", True)

        cfg["Stream"] = {}
        cfg["Stream"]["url"]        = self.Get(str, "Stream", "url",      "http://127.0.0.1:8000/stream")
        cfg["Stream"]["username"]   = self.Get(str, "Stream", "username", "")
        cfg["Stream"]["password"]   = self.Get(str, "Stream", "password", "")

        cfg["debug"] = {}
        cfg["debug"]["blurartwork"] = self.Get(bool, "debug", "blurartwork", False)
        return cfg;



    def SaveConfig(self, cfg):
        """
        This method saves the current WebUI configuration.
        It is important that the whole configuration is included in *cfg*.

        Args:
            cfg (dict): Dictionary with the whole configuration

        Returns:
            *Nothing*
        """
        self.Set("meta",               "version",     cfg["meta"]["version"])
        self.Set("WebUI",              "videomode",   cfg["WebUI"]["videomode"])
        self.Set("WebUI",              "lyrics",      cfg["WebUI"]["lyrics"])
        self.Set("WebUI",              "showstreamplayer",  cfg["WebUI"]["showstreamplayer"])
        self.Set("ArtistsView",        "showrelease", cfg["ArtistsView"]["showrelease"])
        self.Set("GenreSelectionView", "showother",   cfg["GenreSelectionView"]["showother"])
        self.Set("Stream",             "url",         cfg["Stream"]["url"])
        self.Set("Stream",             "username",    cfg["Stream"]["username"])
        self.Set("Stream",             "password",    cfg["Stream"]["password"])
        self.Set("debug",              "blurartwork", cfg["debug"]["blurartwork"])
        return


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

