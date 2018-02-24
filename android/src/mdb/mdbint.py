# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017  Ralf Stemmer <ralf.stemmer@gmx.net>
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


from lib.websocketclient import WebSocketClient
from lib.httpclient      import HTTPClient
import os


class MusicDBInterface(WebSocketClient, HTTPClient):
    """
    This class represents the interface between the MusicDB Server and the MuiscDB Mobile App.

    Args:
        wsurl (str): URL to the MusicDB WebSocket Server
        httpurl (str): URL to the HTTP server that provides MusicDB's files (Music and Artwork)
        datadir (str): Path where files like music and artwork shall be stored on the mobile device
    """
    def __init__(self, wsurl, httpurl, datadir):
        WebSocketClient.__init__(self, wsurl)
        HTTPClient.__init__(self, httpurl)
        
        self.datadir    = datadir
        self.musicdir   = os.path.join(self.datadir, "muscic")
        self.artworkdir = os.path.join(self.datadir, "artwork")

        # Check if $datadir/music and $datadir/artwork exists. Create when not.
        if not os.path.isdir(self.musicdir):
            os.makedirs(self.musicdir)
        if not os.path.isdir(self.artworkdir):
            os.makedirs(self.artworkdir)



    def DownloadSongFile(self, mdbsongpath, destination):
        """
        This method downloads a song file from the MusicDB HTTP server.
        The url that will be used consist of three parts:
        
            #. The server URL given to the constructor (``httpurl``)
            #. The music root directory alias: ``music/``
            #. The path to the song file relative to the music root directory. So, the path as it will be provided by the MusicDB WebSocket Server. This path is what must be given to the ``mdbsongpath`` parameter.

        So the final URL will be ``$httpurl + "/music/" + $mdbsongpath``

        The downloaded file will be stored at the give destination inside the local music root directory.
        This root directory is inside the user data directory.
        So the final place the downloaded song will be stored is ``$datadir + /music/ + $destination``
        The destination parameter also contains the file name.

        Example:

            .. code-block:: python

                mdbi = MusicDBInterface(wsurl, "https://server.org", android_user_dir)

                # download a song from the sever
                # and store it in the local music directory with its artist, album and song ids as names
                srcpath = song["path"] # for example "NimphaioN/2013 - Flame Of Faith/01 Dark Age Begins.mp3"
                dstpath = song["artistid"] + "/" + song["albumid"] + "/" + song["id"] + ".mp3"

                success = mdbi.GetSong(srcpath, dstpath)

        Args:
            mdbsongpath (str): Song path relative to the music root directory, that shall be downloaded.
            destination (str): Path the song will be stored at. This path includes the songs file name.

        Returns:
            ``True`` on success. Otherwise ``False``.
        """
        dstpath = os.path.join(self.musicdir, destination)
        success = self.DownloadFile("music/" + mdbsongpath, dstpath)
        return success



    def DownloadArtworkFile(self, mdbawpath, destination):
        """
        This method is very similar to :meth:`~DownloadSongFile`.
        It just downloads an album artwork instead of a song file.

        The final URL will be ``$httpurl + "/webui/artwork/" + $mdbawpath``.
        The downloaded file will be stored at ``$datadir + /artwork/ + $destination``

        Args:
            mdbawpath (str): Artwork path relative to the artwork directory provided by the server.
            destination (str): Path the artwork will be stored at. This path includes the file name.

        Returns:
            ``True`` on success. Otherwise ``False``.
        """
        dstpath = os.path.join(self.artworkdir, destination)
        success = self.DownloadFile("webui/artwork/" + mdbawpath, dstpath)
        return success



    def GetDatabaseEntries(self):
        """
        This method returns a snapshot of the Music Database of the MusicDB Server.
        It returns a dictionary with each key representing a list of table rows for each table.
        Currently, the *Artists*, *Albums* and *Songs* table gets requested from the server.

        If there is a problem with the server connection, ``None`` gets returned.

        Example:

            .. code-block:: python

                tables = self.GetDatabaseEntries()
                if tables == None:
                    raise AssertionError("No data received from server!")

                for song in tables["songs"]:
                    logging.debug("Song: %s"%song["name"])

        Returns:
            A dict with tables
        """
        args = {}
        args["tables"] = ["artists", "albums", "songs"]

        # Get data from the MusicDB WebSocket Server
        success = self.Connect()
        if not success:
            return None

        success = self.Request("GetTables", "mdbapp:GetDatabaseEntries", args)
        if success:
            response = self.WaitForResponse("mdbapp:GetDatabaseEntries")
        else:
            response = None

        self.Disconnect()

        # return None if the process was not successful
        if not response:
            return None

        return response["arguments"]



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

