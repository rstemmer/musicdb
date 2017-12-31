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
"""
This module handles the different tags for songs and albums.
It can be used to explore the tags-table, add tags, remove tags and tag songs and albums.

There are three types of tags:

genre:
    Genre tags are of class ``"genre"`` and have no parents.
    They annotate the main genre to a song or album.
    For example *Classic*, *Metal*, *Pop*, *Hip Hop*, …
    Genre tags for albums are used by MusicDB to show or hide them in the web UI.
    Further more the randomizer :mod:`~mdbapi.randy` only chooses from songs that genres are activated.
    The Music AI (:mod:`~mod.musicai`) also works on these main genres.

subgenre:
    Subgenre tags are of class ``"subgenre"`` and have a main genre as parent.
    They are for a more detailed classification.
    For example the genre *Metal* can have the subgenres *Dark Metal*, *Folk Metal*, *Industrial Metal*, ….

mood:
    Mood tags are a bit more exotic than the other two types.
    They are of class ``"mood"`` and have no parents.
    A mood tag annotats a mood to a song.
    For example: *Peacefull*, *Wild*, *Sad*, *Funny*, ….
    Mood tags are a dominant feature of MusicDB.
    They are placed in form of icons into the HUD of the web UI.
    The position in the mood-tag grid in the HUD as well as the Icon can also be specified.
    As icon, an unicode character can be used.
    (Further types like SVG may be added in future if people want it)



Main commands
-------------

In the following list, *class* is a string "genre", "subgenre" or "mood" depending which class of tag shall be addressed

    * ``-c class`` - Create a new tag
    * ``-m class`` - Modify an existing tag
    * ``-d class`` - Delete an existing tag
    * ``-l class`` - List all existing tags of a class

If a specific tag shall be addressed, use the ``--name tagname`` argument.
In case a subgenre gets created, the ``--set-parent genre`` argument is mandatory.

For the list and delete command (``-l|-d``) all other arguments will be ignored.

For the create-command (``-c``) only the ``--set-name`` and the ``--set-parent`` argument will be used.

.. note::

    After changing something, the server or clients my need to update cached tag lists.
    This can be done sending the command ``refresh`` via named pipe to the server.

    .. code-block:: bash

        echo "refresh" > /data/musicdb/musicdb.fifo

Style Guide
-----------

To handle tags correctly, the following rules shall be kept in mine.

    #. Do not use other Names or Icons than the one from the database
    #. Use the Color only on Icons. Use the secondary color for names, and for icons when no other color is given
    #. For developers: Use an Unicode font that is as complete as possible
    #. For developers: Do not ignore the position give by the database


Example calls
-------------

Create a new tags (``-c $CLASS``)

.. code-block:: bash

    # create a genre "Metal"
    musicdb tags -c genre --set-name Metal

    # Create a subgenre of Metal
    musicdb tags -c subgenre --set-parent Metal --set-name "Dark Metal"

    # Signal server to force cache updates on server and clients
    echo "refresh" > /data/musicdb/musicdb.fifo


Modify a tag (``-m $CLASS``)

.. code-block:: bash

    # change color of the greedy-mood
    musicdb tags -m mood --name Greedy --set-color #08D008 --set-icon \$

    # Rename a tag
    musicdb tags -m subgenre --name "Deathmetal" --set-name "Death Metal"


Delete a tag (``-d $CLASS``)

.. code-block:: bash

    # Delete a main genre (!! THERE IS NO CHECK FOR DEPENDENCIES !!)
    musicdb tags -d genre Ambient
    

List entries (``-l $CLASS``)

.. code-block:: bash

    # List all genres
    musicdb tags -l genre


Create an initial set of mood tags

.. code-block:: bash

    LOGFILE="moodlog.ansi"

    musicdb -q --logfile $LOGFILE tags -c mood --set-name Sing    --set-posx 1 --set-posy 0 --set-icon ♫︎
    musicdb -q --logfile $LOGFILE tags -c mood --set-name Lucky   --set-posx 2 --set-posy 0 --set-icon ☺︎ --set-color "#00A000"
    musicdb -q --logfile $LOGFILE tags -c mood --set-name Sad     --set-posx 3 --set-posy 0 --set-icon ☹︎
"""

import argparse
import os
from lib.modapi     import MDBModule
from mdbapi.tags    import MusicDBTags


class tags(MDBModule, MusicDBTags):
    def __init__(self, config, database):
        MusicDBTags.__init__(self, config, database)


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="manage tags")
        parser.set_defaults(module=modulename)

        group = parser.add_mutually_exclusive_group()
        group.add_argument("-c", "--create", metavar="CLASS", action="store", type=str, help="Create genre/subgenre/mood")
        group.add_argument("-m", "--modify", metavar="CLASS", action="store", type=str, help="Modify genre/subgenre/mood")
        group.add_argument("-d", "--delete", metavar="CLASS", action="store", type=str, help="Delete genre/subgenre/mood")
        group.add_argument("-l", "--list",   metavar="CLASS", action="store", type=str, help="List   genre/subgenre/mood")
        
        parser.add_argument("-n", "--name", metavar="NAME",  action="store", type=str, help="Name to identify a specific genre/subgenre/mood")
#        parser.add_argument(      "--id",   action="store", type=int, help="ID of the genre/subgenre/mood")

        parser.add_argument("--set-parent", metavar="GENRE", action="store", type=str, help="Name of the parent genre")
        parser.add_argument("--set-name", metavar="NEWNAME", action="store", type=str, help="New name")
        parser.add_argument("--set-icon",   metavar="ICON",  action="store", type=str, help="New icon (unicode char)")
        parser.add_argument("--set-color",  metavar="COLOR", action="store", type=str, help="New HTML like color code")
        parser.add_argument("--set-posx",   metavar="X",     action="store", type=int, help="New position X")
        parser.add_argument("--set-posy",   metavar="Y",     action="store", type=int, help="New position Y")



    def List(self, tagclassname):
        if tagclassname == "genre":
            taglist = self.GetAllGenres()
        elif tagclassname == "subgenre":
            taglist = self.GetAllSubgenres()
        elif tagclassname == "mood":
            taglist = self.GetAllMoods()

        print("\033[1;36m ID \033[1;31m|\033[1;36m Name                 \033[1;31m|\033[1;36mCls\033[1;31m|\033[1;36mParent\033[1;31m|\033[1;36m Icon              \033[1;31m|\033[1;36m  Color  \033[1;31m|\033[1;36m Position")
        print("\033[1;31m----+----------------------+---+------+-------------------+---------+----------")

        separator = "\033[1;31m | "
        for tag in taglist:
            print("\033[1;34m%3i"  %(tag["id"]),       end=separator)
            print("\033[1;36m%-20s"%(tag["name"]),     end=separator)
            print("\033[1;34m%1i"  %(tag["class"]),    end=separator)
            
            if tag["parentid"] != None:
                print("\033[1;34m %3i"  %(tag["parentid"]), end=separator)
            else:
                print("\033[1;30mNone", end=separator)

            if tag["icontype"] != None:
                print("\033[0;36m[%1i]\033[1;34m %13s"  %(tag["icontype"], tag["icon"][0]), end=separator)
            else:
                print("\033[1;30mNone", end=separator)

            if tag["color"] != None:
                print("\033[1;34m%-8s" %(tag["color"]),    end=separator)
            else:
                print("\033[1;30m   None", end=separator)
            
            if tag["posx"] != None and tag["posy"] != None:
                print("\033[1;34m(%2i/%2i)" %(tag["posx"], tag["posy"]), end="")
            elif tag["posx"] != None:
                print("\033[1;34m%4i " %(tag["posx"]), end="")
            else:
                print("\033[1;30m None", end="")
            print("")



    def Create(self, tagname, tagclassname, parentname):
        print("\033[1;34mCreating tag \033[1;36m%s"%(tagname))

        if tagclassname == "genre":
            self.CreateGenre(tagname)
        elif tagclassname == "subgenre":
            self.CreateSubgenre(tagname, parentname)
        elif tagclassname == "mood":
            self.CreateMood(tagname)


    def Delete(self, tagname, tagclassname):
        print("\033[1;34mDeleting tag \033[1;36m%s"%(tagname))

        if tagclassname == "genre":
            self.DeleteGenre(tagname)
        elif tagclassname == "subgenre":
            self.DeleteSubgenre(tagname)
        elif tagclassname == "mood":
            self.DeleteMood(tagname)



    def Modify(self, tagname, tagclassname, newname, newparent, newicon, newcolor, newposx, newposy):
        print("\033[1;34mModifing tag \033[1;36m%s"%(tagname))

        if tagclassname == "genre":
            retval = self.ModifyGenre(tagname, newname, newicon, newcolor, newposx, newposy)
        elif tagclassname == "subgenre":
            retval = self.ModifySubgenre(tagname, newname, newparent, newicon, newcolor, newposx, newposy)
        elif tagclassname == "mood":
            retval = self.ModifyMood(tagname, newname, newicon, newcolor, newposx, newposy)
        else:
            retval = False  # should never happen

        if retval == False:
            print("\033[1;31mAn error occured - see logfile for details!\033[0m")



    # return exit-code
    def MDBM_Main(self, args):

        # Check arguments
        if args.create:
            tagclass = args.create

            if args.set_name == None:
                print("\033[1;31mNo name specified. Use --set-name to specify a name!")
                return 1

            if args.create == "subgenre" and args.set_parent == None:
                print("\033[1;31mNo parent specified. Use --set-parent to specify a parent genre!")
                return 1


        elif args.modify:
            tagclass = args.modify

            if args.name == None:
                print("\033[1;31mNo name specified. Use --name to specify a name of an entry that shall be modified!")
                return 1


        elif args.delete:
            tagclass = args.delete

            if args.name == None:
                print("\033[1;31mNo name specified. Use --name to specify a name of an entry that shall be deleted!")
                return 1


        elif args.list:
            tagclass = args.list


        else:
            print("\033[1;31mNo task specified. Use -c,-m,-d,-l to specify a task.")
            return 1


        # Check tag class
        if tagclass not in ["genre", "subgenre", "mood"]:
            print("\033[1;31mCLASS must be genre, subgenre or mood!")
            return 1


        # Execute command
        if args.list:
            self.List(tagclass)
        elif args.create:
            self.Create(args.set_name, tagclass, args.set_parent)
            self.Modify(args.set_name, tagclass, 
                    None, 
                    None, 
                    args.set_icon, 
                    args.set_color, 
                    args.set_posx, 
                    args.set_posy)
        elif args.delete:
            self.Delete(args.name, tagclass)
        elif args.modify:
            self.Modify(args.name, tagclass, 
                    args.set_name, 
                    args.set_parent, 
                    args.set_icon, 
                    args.set_color, 
                    args.set_posx, 
                    args.set_posy)

        return 0


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

