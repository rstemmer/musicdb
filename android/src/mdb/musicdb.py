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
        self.UpdateSongs(servertables["songs"])



    def UpdateArtists(self, serverartists):
        """
        This method compares the local artists with the artists from the server.
        If the artist does not exists on the local device, a directory named by the artists ID will be created.
        Then, a new artist entry in the local database will be created.

        If there occurs an error while adding the new artist, it will be skipped.
        When only creating the artists directory fails, then it only exists in the database.
        This is OK since one should not trust the file system where every user could remove files.

        Args:
            serverartists: A list of all rows of the servers artists table

        Returns:
            *Nothing*
        """
        localartistids = self.localdb.GetAllArtistIDs()
        for artist in serverartists:
            artistid = artist["id"]

            # if artist exists, continue with the next one
            if artistid in localartistids:
                continue

            # Create new artist entry
            artist["path"] = str(artistid)   # use the ID as directory
            success = self.localdb.CreateArtistEntry(artist)
            if not success:
                continue

            # Create artist directory
            artistdir = os.path.join(self.musicdir, artist["path"])
            try:
                os.makedirs(artistdir)
            except OSError:
                continue



    def UpdateAlbums(self, serveralbums):
        """
        This method compared the local albums with the albums from the server.
        If the album does not exists, it will be created.
        Creating an album will be done in three steps:

            #. Downloading the artwork from the server into the artwork directory
            #. Creating an album entry in the local database
            #. Creating the album directory on the file system

        When one of the steps fails, the other steps gets ignored and the next album will be checked.

        The album path is ``$ARTISTID/$ALBUMID/.``

        Args:
            serveralbums: A list of all rows of the servers album table

        Returns:
            *Nothing*
        """
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
            success = self.DownloadArtworkFile(serverartworkpath, clientartworkpath)
            if not success:
                logging.error("Downloading artwork \"%s\" failed!", serverartworkpath)
                continue
            album["artworkpath"] = clientartworkpath

            # Create new album entry
            album["path"] = os.path.join(str(artistid), str(albumid))
            success = self.localdb.CreateAlbumEntry(album)
            if not success:
                logging.error("Creating album entry for \"%s\" failed!", album["name"])
                continue

            # Create album directory
            albumdir = os.path.join(self.musicdir, album["path"])
            try:
                os.makedirs(albumdir)
            except OSError:
                continue



    def UpdateSongs(self, serversongs):
        """
        This method compares the local songs with the songs from the server.
        If a song does not exist, it will be downloaded from the server.
        
        The update process will be done in the following steps:

            #. Mark all local songs as Outdated
            #. For all server song entries, check if they exist in the database
            #. Downloading new Songs
            #. Removing old songs

        When one of the steps fails, the other steps gets ignored and the next song will be checked.

        Args:
            serversongs: A list of all rows of the servers song table

        Returns:
            *Nothing*
        """
        # Mark all songs as old
        self.localdb.SetAllSongsAsOutdated()

        # Create new entry for new songs, and mark already existing songs as Up To Date
        for song in serversongs:
            self.localdb.CreateOrUpdateSongEntry(song)

        # Download new songs
        newsongs = self.localdb.GetAllNewSongs()
        for newsong in newsongs:
            serversongpath  = newsong["path"]    # For new songs, the path still contains the server side path
            clientsongpath  = os.path.join(str(newsong["artistid"]), str(newsong["albumid"]))
            clientsongpath  = os.path.join(clientsongpath, str(newsong["id"]))
            clientsongpath += os.path.splitext(newsong["path"])[1]
            success = self.DownloadSongFile(serversongpath, clientsongpath)
            if not success:
                logging.error("Downloading song \"%s\" failed!", serversongpath)
                continue

            self.localdb.SetSongAsDownloaded(newsong["id"], clientsongpath)

        # Remove old songs
        oldsongs = self.localdb.GetAllOldSongs()
        for oldsong in oldsongs:
            abssongpath = os.path.join(self.musicdir, oldsong["path"])
            try:
                os.remove(abssongpath)
            except Exception:
                continue

        self.localdb.DeleteAllOldSongs()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

