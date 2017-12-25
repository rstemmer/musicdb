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
This module can be used to manage the Tracker.

The last parameter is a path to a song or an artist.
This path can be relative to the music directory, or an absolute path.
All options set will be applied on that song or artist.
The following options are available:

    #. ``--dot``: :meth:`~mod.tracker.GenerateDotFile`
    #. ``--show``: :meth:`~mod.tracker.ShowRelations`

Examples:

    Create a dot-file and make a graph out of it

    .. code-block:: bash

        musicdb -q tracker --dot ./graph.dot /data/music/Rammstein
        neato -Tpng graph.dot > graph.png

"""

import argparse
from lib.modapi         import MDBModule
from lib.db.trackerdb   import TrackerDatabase
from lib.filesystem     import Filesystem


class tracker(MDBModule):
    def __init__(self, config, database):
        self.config     = config
        self.musicdb    = database
        self.fs         = Filesystem(self.config.music.path)
        self.trackerdb  = TrackerDatabase(self.config.tracker.dbpath)



    def GenerateDotFile(self, target, targetid, relations, dotfile):
        """
        This method generates a dot file visualizing the relations between the target and the related songs or artists.
        Also, the weights get visualized by the thickness of the edges of the generated graph.

        .. warning::

            If the file exists, its content gets replaced!

        Args:
            target (str): The target all IDs apply to. Can be ``"song"`` or ``"artist"``.
            targetid (int): ID of the song or artists, the relations belong to
            relations: A list of relations as returned by :meth:`lib.db.tracker.TrackerDatabase.GetRelations`
            dotfile (str): A path to write the dotfile to.

        Returns:
            ``True`` on success. If there is any error, ``False`` gets returned.
        """
        if target not in ["song", "artist"]:
            return False

        # give the IDs a name
        if target == "song":
            targetname = self.musicdb.GetSongById(targetid)["name"]
        elif target == "artist":
            targetname = self.musicdb.GetArtistById(targetid)["name"]
        else:
            return False

        for relation in relations:
            if target == "song":
                relation["name"] = self.musicdb.GetSongById(relation["id"])["name"]
            elif target == "artist":
                relation["name"] = self.musicdb.GetArtistById(relation["id"])["name"]
            else:
                return False

        dot = open(dotfile, "w")
        dot.write("digraph songenv {\n")

        # Related Song
        dot.write("\tsubgraph {\n")
        dot.write("\t\trank   = same; ")
        for relation in relations:
            dot.write("\""+relation["name"]+"\"; ")
        dot.write("\n\t}\n")

        # center
        dot.write("\tsubgraph {\n")
        dot.write("\t\trank = same; "+targetname+";\n")
        dot.write("\t}\n")
        
        dot.write("\tedge [ arrowhead=\"none\" ; len=7 ];\n\n")

        # edges
        for relation in relations:
            penwidth = max(1, int(relation["weight"]/10))


            dot.write("\t\""+relation["name"]+"\" -> \""+targetname+"\" [penwidth="+str(penwidth)+"];\n")

        dot.write("}\n\n")
        dot.close()
        return True



    def ShowRelations(self, target, targetid, relations):
        """
        This method lists all entries in the relations list returned by the database for the given target ID

        Args:
            target (str): The target all IDs apply to. Can be ``"song"`` or ``"artist"``.
            targetid (int): ID of the song or artists, the relations belong to
            relations: A list of relations as returned by :meth:`lib.db.tracker.TrackerDatabase.GetRelations`

        Returns:
            ``True`` on success. If there is any error, ``False`` gets returned.
        """
        if target not in ["song", "artist"]:
            return False

        for relation in relations:
            # Get Weight
            weight = relation["weight"]

            # Get Name
            if target == "song":
                name = self.musicdb.GetSongById(relation["id"])["name"]
            elif target == "artist":
                name = self.musicdb.GetArtistById(relation["id"])["name"]
            else:
                return False

            # Get Color
            if target == "song":
                colorweight = weight
            elif target == "artist":
                colorweight = int(weight/5)
            else:
                return False


            if colorweight <= 1:
                color = "\033[1;30m"
            elif colorweight == 2:
                color = "\033[1;34m"
            elif colorweight == 3:
                color = "\033[1;36m"
            else:
                color = "\033[1;37m"

            # Print
            print(" \033[1;35m[%2d] %s%s"%(weight, color, name))

        return True



    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="access information from the song tracker")
        parser.set_defaults(module=modulename)
        parser.add_argument("-s", "--show", action="store_true", help="Show the related songs or artists")
        parser.add_argument("-d", "--dot"
            , action="store"
            , metavar="dotfile"
            , type=str
            , help="if this option is given, a dot-file will be generated with the results")
        parser.add_argument(      "--test",    action="store_true", help="for testing - it's magic! read the code")
        parser.add_argument("path", help="Path to the song or artist on that the previos options will be applied")



    # return exit-code
    def MDBM_Main(self, args):

        if args.test:
            from tqdm import tqdm
            print("\033[1;35mTranslating old table to new table …\033[0m")

            # # Translate old table to new table
            # sql = "SELECT song, successor, weight FROM graph"
            # results = self.trackerdb.GetFromDatabase(sql)
            # for result in results:
            #     for _ in range(result[2]):
            #         self.trackerdb.AddRelation("song", result[0], result[1])

            # # Generate artistrelations out of songrelations
            # sql = "SELECT songida, songidb, weight FROM songrelations"
            # results = self.trackerdb.GetFromDatabase(sql)
            # for result in tqdm(results):

            #     artista = self.musicdb.GetSongById(result[0])["artistid"]
            #     artistb = self.musicdb.GetSongById(result[1])["artistid"]

            #     for _ in range(result[2]):
            #         self.trackerdb.AddRelation("artist", artista, artistb)

            print("\033[1;32mdone!\033[0m")
            return 0


        # Genrate path relative to the music root directory - if possible
        try:
            path = self.fs.AbsolutePath(args.path)  # Be sure the path is absolute (resolve "./")
            path = self.fs.RemoveRoot(path)         # Now make a relative artist or song path
        except Exception as e:
            print("\033[1;31mInvalid path. Determin relative path to the music root directory failed with error: %s", str(e))
            return 1

        # Identify target by path and get target ID
        if self.fs.IsFile(path):
            mdbsong = self.musicdb.GetSongByPath(path)
            if not mdbsong:
                print("\033[1;31mPath %s is a file, but it is not a song file!\033[0m"%(path))
            target   = "song"
            targetid = mdbsong["id"]

        elif self.fs.IsDirectory(path):
            mdbartist = self.musicdb.GetArtistByPath(path)
            if not mdbartist:
                print("\033[1;31mPath %s is a directory, but it is not an artist directory!\033[0m"%(path))
            target   = "artist"
            targetid = mdbartist["id"]

        else:
            print("\033[1;31mPath %s does not exist!\033[0m"%(path))
            return 1

        # Get target relation
        print("\033[1;34mGetting \033[1;36m%s\033[1;34m relations from database … \033[0m"%(target))
        relations = self.trackerdb.GetRelations(target, targetid)
        print("\033[1;36m%d\033[1;34m entries found.\033[0m"%(len(relations)))

        # Apply parameters
        if args.show:
            self.ShowRelations(target, targetid, relations)

        if args.dot:
            rootfs  = Filesystem()
            dotfile = rootfs.AbsolutePath(args.dot)
            self.GenerateDotFile(target, targetid, relations, dotfile)

        return 0


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

