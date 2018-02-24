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


from mdb.localdb import LocalDatabase
from mdb.mdbint  import MusicDBInterface
import os


try:
    import logging
except:
    from kivy.logger import Logger as logging



class MusicDB(MusicDBInterface):
    """
    Imports self.musicdir, self.artworkdir
    """

    def __init__(self, wsurl, httpurl, datadir):
        MusicDBInterface.__init__(self, wsurl, httpurl, datadir)
        self.localdb  = LocalDatabase(os.path.join(datadir, "music.db"))



    def Synchronize(self):
        # Get server tables
        servertables = self.GetDatabaseEntries()

        # Synchronize database
        self.UpdateArtists(servertables["artists"])
        self.UpdateAlbums(servertables["albums"])



    def UpdateArtists(self, serverartists):
        localartistids = self.localdb.GetAllArtistIDs()
        for artist in serverartists:
            artistid = artist["id"]

            # if artist exists, continue with the next one
            if artistid in localartistids:
                continue

            # Create new artist entry
            artist["path"] = str(artistid)   # use the ID as directory
            self.localdb.CreateArtistEntry(artist)

            # Create artist directory
            artistdir = os.path.join(self.musicdir, artist["path"])
            try:
                os.makedirs(artistdir)
            except OSError:
                continue



    def UpdateAlbums(self, serveralbums):
        localalbumids = self.localdb.GetAllAlbumIDs()
        for album in serveralbums:
            artistid = album["artistid"]
            albumid  = album["id"]

            # if album exists, continue with the next one
            if albumid in localalbumids:
                continue

            # Download artwork
            serverartworkpath = album["artworkpath"]
            clientartworkpath = str(album["id"]) + ".jpg"
            self.DownloadArtworkFile(serverartworkpath, clientartworkpath)
            album["artworkpath"] = clientartworkpath

            # Create new album entry
            album["path"] = os.path.join(str(artistid), str(albumid))
            self.localdb.CreateAlbumEntry(album)

            # Create album directory
            albumdir = os.path.join(self.musicdir, album["path"])
            try:
                os.makedirs(albumdir)
            except OSError:
                continue




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

