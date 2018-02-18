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



    def GetSongFile(self, mdbsongpath, destination):
        pass



    def GetArtworkFile(self, mdbawpath, destination):
        pass



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

