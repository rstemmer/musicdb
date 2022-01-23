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
This class handles the different tags for songs and albums.
Details about the concept of tags can be found here in the :mod:`musicdb.lib.db.musicdb` documentation.

Example:

    .. code-block:: python

        database = MusicDatabase("./music.db")
        config   = MusicDBConfig("./musicdb.ini")
        tags     = MusicDBTags(config, database)

        tags.CreateGenre("Metal")                   # Create a genre "Metal"
        tags.CreateSubgenre("Dark Metal", "Metal")  # Create a subgenre of "Metal" and name it "Dark Metal"


"""

from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
import logging

class MusicDBTags(object):
    """
    Args:
        config: MusicDB configuration object
        database: MusicDB database

    Raises:
        TypeError: when *config* or *database* not of type :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` or :class:`~musicdb.lib.db.musicdb.MusicDatabase`
    """
    def __init__(self, config, database):
        if type(config) != MusicDBConfig:
            print("\033[1;31mFATAL ERROR: Config-class of unknown type!\033[0m")
            raise TypeError("config argument not of type MusicDBConfig")
        if type(database) != MusicDatabase:
            print("\033[1;31mFATAL ERROR: Database-class of unknown type!\033[0m")
            raise TypeError("database argument not of type MusicDatabase")

        self.db     = database
        self.cfg    = config


    def DeriveAlbumTags(self, albumid):
        """
        This method derives album tags from its song tags.
        It looks for all songs of the album and their specific genre and sub genre tags.
        Tags with a confidence level greater or equal to 1.0 will be collected and set as genres for the album.
        The set genres have a confidence of the average appearance of the tag over all the album's songs.

        Args:
            albumid (int): ID of the album that tags shall be updated

        Returns:
            *Nothing*
        """
        songs = self.db.GetSongsByAlbumId(albumid)

        histogram = {}
        # Get genres of all songs on the album
        for song in songs:
            tags = self.db.GetTargetTags("song", song["id"])
            if not tags:
                continue

            for tag in tags:
                # Skill every tag that is not a genre or sub genre
                if tag["class"] != MusicDatabase.TAG_CLASS_GENRE and tag["class"] != MusicDatabase.TAG_CLASS_SUBGENRE:
                    continue

                # Ignore tags set by the AI
                if tag["approval"] == 0:
                    continue

                # Consider tag in histogram
                key = str(tag["id"])
                if not key in histogram:
                    histogram[key]  = 1
                else:
                    histogram[key] += 1

        # Set new tags
        numofsongs = len(songs)
        for key in histogram:
            tagid = int(key)
            count = histogram[key]
            confidence = count / numofsongs

            self.db.SetTargetTag("album", albumid, tagid, approval=0, confidence=confidence)
            


    def GetAllGenres(self):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.GetAllTags`
        """
        return self.db.GetAllTags(MusicDatabase.TAG_CLASS_GENRE)
    
    def GetAllSubgenres(self):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.GetAllTags`
        """
        return self.db.GetAllTags(MusicDatabase.TAG_CLASS_SUBGENRE)

    def GetAllMoods(self):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.GetAllTags`
        """
        return self.db.GetAllTags(MusicDatabase.TAG_CLASS_MOOD)



    def CreateGenre(self, name):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.CreateTag`
        """
        self.db.CreateTag(name, MusicDatabase.TAG_CLASS_GENRE)
        return None

    def CreateSubgenre(self, name, parentname):
        """
        The parent name gets translated to its genre id.
        As mentioned in the tag concept (see :mod:`~musicdb.lib.db.musicdb`), only subgenre can have parents.
        And those parents must be of class genre.

        For further details see :meth:`musicdb.lib.db.musicdb.MusicDatabase.CreateTag`
        """
        parenttag = self.db.GetTagByName(parentname, MusicDatabase.TAG_CLASS_GENRE)
        self.db.CreateTag(name, MusicDatabase.TAG_CLASS_SUBGENRE, parenttag["id"])
        return None

    def CreateMood(self, name):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.CreateTag`
        """
        self.db.CreateTag(name, MusicDatabase.TAG_CLASS_MOOD)
        return None



    def DeleteGenre(self, name):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.DeleteTag`
        """
        self.db.DeleteTagByName(name, MusicDatabase.TAG_CLASS_GENRE);
        return None

    def DeleteSubgenre(self, name):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.DeleteTag`
        """
        self.db.DeleteTagByName(name, MusicDatabase.TAG_CLASS_SUBGENRE);
        return None

    def DeleteMood(self, name):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.DeleteTag`
        """
        self.db.DeleteTagByName(name, MusicDatabase.TAG_CLASS_MOOD);
        return None



    def ModifyGenre(self, tagname, newname=None, newicon=None, newcolor=None, newposx=None, newposy=None):
        """
        See :meth:`~musicdb.mdbapi.tags.MusicDBTags.ModifyTag`.

        All arguments can also be ``None``
        
        Args:
            tagname (str): Name of the tag that shall be modified
            newname (str): New name of the tag
            newicon (str): New icon for the tag - the icon-type gets detected automatically
            newcolor (str): New color for the tag
            newposx (int): New position
            newposy (int): New position
        """
        return self.ModifyTag(tagname, MusicDatabase.TAG_CLASS_GENRE, 
                newname, None, newicon, newcolor, newposx, newposy)

    def ModifySubgenre(self, tagname, newname=None, newparent=None, newicon=None, newcolor=None, newposx=None, newposy=None):
        """
        See :meth:`~musicdb.mdbapi.tags.MusicDBTags.ModifyTag`.

        All arguments can also be ``None``
        
        Args:
            tagname (str): Name of the tag that shall be modified
            newname (str): New name of the tag
            newparent (str): Name of the new parent tag
            newicon (str): New icon for the tag - the icon-type gets detected automatically
            newcolor (str): New color for the tag
            newposx (int): New position
            newposy (int): New position
        """
        return self.ModifyTag(tagname, MusicDatabase.TAG_CLASS_SUBGENRE, 
                newname, newparent, newicon, newcolor, newposx, newposy)

    def ModifyMood(self, tagname, newname=None, newicon=None, newcolor=None, newposx=None, newposy=None):
        """
        See :meth:`~musicdb.mdbapi.tags.MusicDBTags.ModifyTag`.

        All arguments can also be ``None``
        
        Args:
            tagname (str): Name of the tag that shall be modified
            newname (str): New name of the tag
            newicon (str): New icon for the tag - the icon-type gets detected automatically
            newcolor (str): New color for the tag
            newposx (int): New position
            newposy (int): New position
        """
        return self.ModifyTag(tagname, MusicDatabase.TAG_CLASS_MOOD, 
                newname, None, newicon, newcolor, newposx, newposy)


    def ModifyTag(self, tagname, tagclass, newname, newparent, newicon, newcolor, newposx, newposy):
        """
        See :meth:`musicdb.lib.db.musicdb.MusicDatabase.ModifyTag`

        The icontype gets determined by the *newicon*-value if not ``None``.

        The parentid gets determined by the *newparent*-name.

        returns:
            ``True``: On success
            ``False``: in case something fails

        Raises:
            AssertionError: Whenever this method does not find wrong values but the database implementation does.
        """
        if newname != None:
            self.db.ModifyTag(tagname, tagclass, "name", newname)

        if newparent != None:
            if tagclass != MusicDatabase.TAG_CLASS_SUBGENRE:
                logging.warning("Cannot change the parant of a non-subgenre tag!")
                return False
            
            parenttag = self.GetTagByName(newparent, MusicDatabase.TAG_CLASS_GENRE)
            self.db.ModifyTag(tagname, tagclass, "parentid", parenttag["id"])

        if newicon != None:
            newicontype, newicon = self.AnalyseIcon(newicon)
            if newicontype == None or newicon == None:
                logging.warning("Unable to detect icontype!")
                return False

            self.db.ModifyTag(tagname, tagclass, "icontype", newicontype)
            self.db.ModifyTag(tagname, tagclass, "icon",     newicon)

        if newcolor != None:
            if newcolor[0] != "#" or len(newcolor) != 7:
                logging.warning("Color-Format is not #RRGGBB! - %c != #; len(\"%s\") != 7", newcolor[0], newcolor)
                return False

            self.db.ModifyTag(tagname, tagclass, "color", newcolor)

        if newposx != None:
            self.db.ModifyTag(tagname, tagclass, "posx", newposx)

        if newposy != None:
            self.db.ModifyTag(tagname, tagclass, "posy", newposy)

        return True



    def AnalyseIcon(self, icon):
        if type(icon) == None:
            return None, None

        if type(icon) != str:
            logging.error("Invalid datatype of icon! \033[1;30m(Setting Icon and Type to None)")
            return None, None
        
        #if len(icon) == 1:
        #    return MusicDatabase.TAG_ICONTYPE_UNICODE, icon
        # !! len("☺︎") == 2 !! - Do not trust len!!
        
        if icon[0] == "<" and icon[-1] == ">":
            return MusicDatabase.TAG_ICONTYPE_HTML, icon

        #logging.error("Unable to determin the icontype! icon: \"%s\"; type: %s; len: %i \033[1;30m(Setting Icon and Type to None)", str(icon), str(type(icon)), len(icon))

        # default assumtion is, that the icon is unicode
        return MusicDatabase.TAG_ICONTYPE_UNICODE, icon


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

