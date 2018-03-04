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
Managing the MusicAI. Last argument, if it's a path, can be a path to an artist, album or song.
All flags can be combined, but should not if they do not make sense.

The arguments of this module gets checked in the following order

#. ``--feature``: :meth:`~mod.musicai.musicai.GenerateFeatureset`
#. ``--genre``: :meth:`~mod.musicai.musicai.GenerateTrainingset`
#. ``--train``: :meth:`~mod.musicai.musicai.PerformTraining`
#. ``--predict``: :meth:`~mod.musicai.musicai.PerformPrediction`
#. ``--stats``: :meth:`~mod.musicai.musicai.ShowStatistics`

The genre argument for ``--genre`` must be one of the genres configured in the MusicDB Configuration under ``[MusicAI]->genrelist``.
For example: ``"Metal"`` or ``"Classic"``.

The action for the ``--predict`` option must be ``"show"`` or ``"store"``.

    ``show``:
        Show the results on the screen

    ``store``:
        Write the results to the database.
        It sets the genre tags for each song with setting *approval* to 0 (Tag set by AI) and *confidence* to the prediction confidence.

Examples:

    **Creating a training set** and generating the needed feature set:

    .. code-block:: bash

        # Create training set
        musicdb -q musicai -f -g metal /data/music/Dying\ Fetus
        # -f/--feature: generate feature set
        # -g/--genre genre: add songs to training set for the specified genre


    **Train the AI** on the training set created before:

    .. code-block:: bash

        # Perform training
        musicdb -q musicai -t
        # -t/--train: train feature

    **Predict the genre** of a song, album or artist:

    .. code-block:: bash

        # Perform prediction and show results
        musicdb -q musicai -f -p show /data/music/Blutengel/2001\ -\ Seelenschmerz
        # -f/--feature: generate the feature set needed for prediction
        # -p/--predict: perform prediction

        # Perform prediction and store results in the MusicDB MusicDatabase
        musicdb -q musicai -f -p store /data/music/Blutengel/2001\ -\ Seelenschmerz

    **Get some statistics** (among of features and songs in training set).

    .. code-block:: bash

        # Show statistics
        musicdb -q musicai -s
        # -s/--stats: show statistict

"""

import argparse
import logging
import os
from lib.modapi         import MDBModule
from lib.db.musicdb     import MusicDatabase
from lib.filesystem     import Filesystem
import concurrent.futures
import random
import datetime
from tqdm               import tqdm

try:
    from mdbapi.musicai     import MusicAI
except ModuleNotFoundError:
    AIModulesFound = False
else:
    AIModulesFound = True

class musicai(MDBModule):
    def __init__(self, config, database):
        MDBModule.__init__(self)
        self.musicdb = database
        self.config  = config
        self.fs      = Filesystem(self.config.music.path)


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        if AIModulesFound:
            logging.info("All dependencies for using AI are available.")
        else:
            logging.warning("Some dependencies to use AI are missing.")
            return

        parser = parserset.add_parser(modulename, help="Manager for the MusicDB-AI")
        parser.set_defaults(module=modulename)
        parser.add_argument("-f", "--feature", action="store_true", help="generate feature set from PATH")
        parser.add_argument("-t", "--train",   action="store_true", help="run training focusing on PATH if given")
        parser.add_argument("-p", "--predict"
            , action="store"
            , type=str
            , metavar="action"
            , help="let the AI predict the genre of PATH. Actions are \"show\" or \"store\"")
        parser.add_argument("-g", "--genre"
            , action="store"
            , type=str
            , metavar="genre"
            , help="use feature set for training for the given genre")
        parser.add_argument("-s", "--stats",   action="store_true", help="show some statistics")
        parser.add_argument(      "--test",    action="store_true", help="for testing - it's magic! Read the code!")
        parser.add_argument("path", nargs="?", help="Artist, Album or Song-Path for the songs to work with")

    
    def AnalysisThread(self, songid, songpath):
        """
        Calls the function :func:`~mdbapi.musicai.MusicAI.CreateFeatureset`. 
        This function is made to be used concurrently.

        Args:
            songid (int): ID of the song that shall be analyzed
            songpath (str): Path to the song that shall be analyzed

        Returns:
            status from the CreateFeatureset-call
        """
        musicai = MusicAI(self.config)
        print("\033[1;34m - Analysing \033[0;36m%s\033[0m" % songpath)
        logging.info("Analysing \033[0;36m%s\033[0m" % songpath)
        retval = musicai.CreateFeatureset(songid, songpath)
        return retval

    def GenerateFeatureset(self, mdbsongs):
        """
        This method creates feature sets for a list of songs.
        If one of the songs already has a feature set the song gets skipped.

        The creation is done by calling :meth:`~mod.musicai.musicai.AnalysisThread` in 6 threads in parallel.
        If an analysis fails the song gets skipped.

        Args:
            mdbsongs: A list of MusicDB song dictionaries

        Returns:
            *Nothing*
        """
        # It is faster to do this befor all the workers-environment ist set up
        print("\033[1;34mChecking for \033[0;36m%d\033[1;34m if feature-sets exists\033[0m"%(len(mdbsongs)))
        logging.info("\033[1;34mGenerating \033[0;36m%d\033[1;34m feature-sets\033[0m"%(len(mdbsongs)))
        requestlist = []
        musicai     = MusicAI(self.config)
        for mdbsong in mdbsongs:
            if musicai.HasFeatureset(mdbsong["id"]):
                print("\033[1;34m - Song \033[0;36m%s\033[1;34m already analysed\033[0m" % mdbsong["name"])
                logging.debug("Song \033[0;36m%s\033[1;30m already analysed" % mdbsong["name"])
            else:
                requestlist.append((mdbsong["id"], mdbsong["path"]))

        if len(requestlist) == 0:
            print("\033[1;34mFeature-set already generated")
            logging.info("Feature-set already generated")
            return

        print("\033[1;34mGenerating \033[0;36m%d\033[1;34m feature-sets\033[0m"%(len(requestlist)))
        logging.info("\033[1;34mGenerating \033[0;36m%d\033[1;34m feature-sets\033[0m"%(len(requestlist)))
        t_start = datetime.datetime.now()

        # do analyses IN THREADS
        errors  = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            thread = {executor.submit(self.AnalysisThread, request[0], request[1]): request for request in requestlist}
            for future in concurrent.futures.as_completed(thread):
                try:
                    retval = future.result(60)   # timeout of 1 minute
                    if retval != True:
                        raise AssertionError("generation faied!")
                except Exception as e:
                    print("\033[1;33mAnalysis Thread generated an exception: %s\033[0m" % e)
                    logging.warning("Analysis Thread generated an exception: %s" % e)
                    errors += 1

        t_diff = datetime.datetime.now() - t_start
        print("\033[1;34mFeature-set generated in \033[0;36m%s\033[0m"%(str(t_diff)))
        logging.info("\033[1;34mFeature-set generated in \033[0;36m%s\033[0m"%(str(t_diff)))
        if errors > 0:
            print("\033[1;33m%d / %d analysis failed!\033[0m"%(errors, len(mdbsongs)))
            logging.warning("%d / %d analysis failed!\033[0m"%(errors, len(mdbsongs)))


    def GenerateTrainingset(self, mdbsongs, genre):
        """
        This method creates training sets out of the feature set by augmenting them with a genre.
        If a song already has a training set, or no feature set it is skipped.

        Args:
            mdbsongs: A list of MusicDB song dictionaries
            genre (str): The genre the songs belong to
        """
        if not genre in self.genrelist:
            logging.error("The genre \"%s\" is not in the genrelist: \"%s\"!", genre, str(self.genrelist))
            print("\033[1;31mThe genre \"%s\" is not in the genrelist: \"%s\"!\033[0m"%(genre, str(self.genrelist)))
            return

        newsets = 0
        musicai = MusicAI(self.config)

        print("\033[1;34mGenerating \033[0;36m%d\033[1;34m training-sets for genre \033[0;36m%s\033[0;36m"%(len(mdbsongs), genre))
        logging.info("\033[1;34mGenerating \033[0;36m%d\033[1;34m training-sets for genre \033[0;36m%s\033[0;36m"%(len(mdbsongs), genre))

        # Add to trainingsset
        for mdbsong in tqdm(mdbsongs, unit="Songs"):
            songid = mdbsong["id"]
            
            if musicai.HasTrainingset(songid):
                print("\033[1;34mSong already registered for training! \033[1;30m(%s)\033[0m"%(mdbsong["name"]))
                logging.info("Song already registered for training! \033[1;30m(%s)\033[0m"%(mdbsong["name"]))
                continue

            if not musicai.HasFeatureset(songid):
                print("\033[1;31mSong does not have a featureset! \033[1;30m(%s)\033[0m"%(mdbsong["name"]))
                logging.error("\033[1;31mSong does not have a featureset! \033[1;30m(%s)\033[0m"%(mdbsong["name"]))
                continue

            musicai.AddSongToTrainingset(songid, genre)
            newsets += 1

        print("\033[0;36m%d\033[1;34m new training sets registered.\033[0m"%(newsets))
        logging.info("\033[0;36m%d\033[1;34m new training sets registered.\033[0m"%(newsets))


    def PerformTraining(self):
        """
        Direct interface to :meth:`mdbapi.musicai.MusicAI.PerformTraining`.

        Returns:
            *Nothing*
        """
        print("\033[1;34mStart training session\033[0m")
        logging.info("\033[1;34mStart training session\033[0m")
        musicai = MusicAI(self.config)

        # train on set
        t_start = datetime.datetime.now()
        musicai.PerformTraining()
        t_diff = datetime.datetime.now() - t_start
        print("\033[?25h\033[1;34mTraining session took \033[0;36m%s\033[0m"%(str(t_diff)))
        logging.info("\033[?25h\033[1;34mTraining session took \033[0;36m%s\033[0m"%(str(t_diff)))
        

    def PerformPrediction(self, mdbsongs):
        """
        This method performs a prediction on a list of songs.
        For each song the method :meth:`mdbapi.musicai.MusicAI.PerformPrediction` gets called.

        When calling this method after a CUDA update, the prediction of the first song will take some minutes because the network gets recompiled for the new libraries.

        The results will be returned and can then be used.
        It is a list of predictions. Each prediction is a tuple of *songid* and *confidence*.
        The confidence is a list with each element representing the confidence of one of the genres in the genre list.

        Args:
            mdbsongs: A list of MusicDB song dictionaries

        Returns:
            A set of values representing the prediction

        Example:

            .. code-block:: python

                predictionset = self.PerformPrediction(songs)
                for genreindex, genrename in enumerate(self.config.musicai.genrelist):
                    print("Genre name: %s" % (genrename))
                    for prediction in predictionset:
                        print("Song ID: %d",   % (prediction[0]))
                        print("Confidence: %d" % (prediction[1][genreindex]))
        """
        musicai = MusicAI(self.config)

        print("\033[1;34mStart prediction\033[0;36m")
        logging.info("\033[1;34mStart prediction\033[0;36m")
        predictionset = []
        t_start = datetime.datetime.now()
        for mdbsong in tqdm(mdbsongs, unit="Songs"):
            prediction = musicai.PerformPrediction(mdbsong["id"])
            if prediction == None:
                print("\033[1;31mNo feature set available!\033[0;36m")
                continue
            predictionset.append((mdbsong["id"], prediction))

        t_diff = datetime.datetime.now() - t_start
        print("\033[?25h\033[1;34mPrediction took \033[0;36m%s\033[0m"%(str(t_diff)))
        logging.info("\033[?25h\033[1;34mPrediction took \033[0;36m%s\033[0m"%(str(t_diff)))
        return predictionset

    def ShowPrediction(self, mdbsongs, predictionset):
        """
        The results will be printed in a table.
        The table shows the confidence of a song (abscissa) for each genre (ordinate).
        The last column shows the mean value of all songs that can be seen as genre-prediction for an Album or an Artist.

        The predictionset must be a list of tuple *(Song ID , Confidence)*

        Args:
            mdbsongs: A list of MusicDB song dictionaries
            predictionset: Set of predictions as returned by :meth:`~mod.musicai.musicai.PerformPrediction`

        Returns:
            *Nothing*
        """

        def Colormapper(value):
            prefix = "\033[1;"
            if value >= 0.79:
                return prefix + "37m"
            elif value >= 0.49:
                return prefix + "36m"
            elif value >= 0.29:
                return prefix + "34m"
            return prefix + "30m"

        # Print single song prediction
        print("\033[1;44;37m", end="")
        for genre in self.config.musicai.genrelist:
            print("%s" % (genre.ljust(5)[:5]), end=" ")
        print((" " * 2) + "Song name \033[0m")

        for index, mdbsong in enumerate(mdbsongs):
            # in predictionset[index][0] is the song ID - that should match with the current song
            try:
                probability = next(p[1] for p in predictionset if p[0] == mdbsong["id"])
            except StopIteration:
                # There may be no analysis of some songs because they are too short (like Intros)
                continue

            for prob in probability:
                print("%s%.3f"%(Colormapper(prob), prob), end=" ")
            print(" \033[1;34m%s"%(mdbsong["name"]))

        # Print song IDs for the results (table headline)
        print("\033[1;44;37mSong ID:  ", end="")
        for mdbsong in mdbsongs:
            print("%4i" % (mdbsong["id"]), end=" ")
        print((" " * 2) + "Album \033[0m")

        # Print single results
        for index, genre in enumerate(self.config.musicai.genrelist):
            print("\033[1;36m%s\033[1;34m"%(genre.ljust(7)), end=" | ")
            mean = 0
            for mdbsong in mdbsongs:
                try:
                    probabilityset = next(p[1] for p in predictionset if p[0] == mdbsong["id"])
                    probability    = probabilityset[index]
                except StopIteration:
                    # There may be no analysis of some songs because they are too short (like Intros)
                    probability = 0
                    print("%s%s"%("\033[0;33m", "None"), end=" ")
                else:
                    color = Colormapper(probability)
                    print("%s%.2f"%(color, probability), end=" ")
                mean += probability

            if predictionset:
                mean /= len(predictionset)
                color = Colormapper(mean)
                print("\033[1;34m| %s%.3f\033[0m"%(color, mean))
            else:
                print("\033[1;34m| \033[0;33mNo feature set found\033[0m")


    def StorePrediction(self, predictionset):
        """
        This method stores the predicted genres into the MusicDatabase.
        Son´, for each song, its genre gets stored with *approval* set to 0 (Tag set by AI), and the *confidence* set to the prediction confidence of the AI.
        The threshold of confidence so that the tag gets set is 0.3.

        Args:
            predictionset: Set of predictions as returned by :meth:`~mod.musicai.musicai.PerformPrediction`

        Returns:
            *Nothing*
        """
        # Get all necessary tags from the database
        genretags = {}
        for genrename in self.config.musicai.genrelist:
            mdbgenre = self.musicdb.GetTagByName(genrename, MusicDatabase.TAG_CLASS_GENRE)
            
            if not mdbgenre:
                logging.error("The genre \"%s\" does not exist in database!", genre)
                print("\033[1;31mThe genre \"%s\" does not exist in database!\033[0m"%(genre))
                return

            genretags[genrename] = mdbgenre

        for prediction in predictionset:
            songid      = prediction[0]
            confidences = prediction[1]

            for index, genre in enumerate(self.config.musicai.genrelist):
                confidence = confidences[index]

                if confidence >= 0.3:
                    genretag = genretags[genre]
                    self.musicdb.SetTargetTag("song", songid, genretag["id"], 0, confidence)


    def ShowStatistics(self):
        """
        This method prints the number of songs in the training set and the size of the training sets.

        Returns:
            *Nothing*
        """
        musicai = MusicAI(self.config)
        stats = musicai.GetStatistics()
        print("\033[1;34mTrainingset Size:  \033[1;36m%7i \033[0;34mFeatures\033[0m" 
                % (stats["setsize"]))
        print("\033[1;34mNum. Songs in Set: \033[1;36m%7i \033[0;34mSongs\033[0m" 
                % (stats["numofsongs"]))



    def GetSongsFromPath(self, path):
        """
        This method returns a list of MusicDB songs depending if the path points to a single song, an album or an artist.
        If the path is invalid ``None`` will be returned.

        Args:
            path (str): a path to a song, an album or an artist

        Returns:
            List of MusicDB songs if *path* is valid, otherwise ``None``
        """
        if not path:
            return None

        path = os.path.abspath(path)

        if not os.path.exists(path):
            print("\033[1;31mERROR: Path "+path+" does not exist!\033[0m")
            return None

        try:
            path = self.fs.RemoveRoot(path)
        except:
            print("\033[1;31mERROR: Path "+path+" is not part of the music collection!\033[0m")
            return None

        print("\033[1;34mCollecting songs from "+path)
        # Get song-pathes and ids from path
        if self.fs.IsArtistPath(path, self.config.music.ignorealbums, self.config.music.ignoresongs):
            mdbartist = self.musicdb.GetArtistByPath(path)
            mdbsongs  = self.musicdb.GetSongsByArtistId(mdbartist["id"])
            print("\033[1;34mWorking on \033[1;37mArtist-path\033[1;34m for artist \033[1;36m%s\033[0m"%(mdbartist["name"]))

        elif self.fs.IsAlbumPath(path, self.config.music.ignoresongs):
            mdbalbum = self.musicdb.GetAlbumByPath(path)
            mdbsongs = self.musicdb.GetSongsByAlbumId(mdbalbum["id"])
            print("\033[1;34mWorking on \033[1;37mAlbum-path\033[1;34m for album \033[1;36m%s\033[0m"%(mdbalbum["name"]))

        elif self.fs.IsSongPath(path):
            mdbsong  = self.musicdb.GetSongByPath(path)
            mdbsongs = [mdbsong]
            print("\033[1;34mWorking on \033[1;37mSong-path\033[1;34m for song \033[1;36m%s\033[0m"%(mdbsong["name"]))

        else:
            print("\033[1;31mERROR: Path does not address a Song, Album or Artist\033[0m")
            return None

        return mdbsongs


    # return exit-code
    def MDBM_Main(self, args):

        if not AIModulesFound:
            logging.error("Some dependencies to use AI are missing!")
            return 1

        if args.test:
            musicai = MusicAI(self.config)
            musicai.GetGenreMatrix()
            #print("\033[1;35mDoing a performance-test …\033[0m")
            #musicai = MusicAI(self.config)
            #x = musicai.GetTrainingset()
            return 0


        # Check parameters
        mdbsongs = self.GetSongsFromPath(args.path)
        if not mdbsongs:
            if args.feature or args.genre or args.predict:
                print("\033[1;31mThe path does not address songs. A path to a song, album or artist is needed for some given parameters!\033[0m")
                logging.error("The path does not address songs. A path to a song, album or artist is needed for some given parameters!")
                return 1

        # generate featureset
        if args.feature:
            self.GenerateFeatureset(mdbsongs)

        # generate trainingset
        if args.genre:
            self.GenerateTrainingset(mdbsongs, args.genre)

        # perform training
        if args.train:
            self.PerformTraining()

        # run prediction
        if args.predict:
            prediction = self.PerformPrediction(mdbsongs)
            if args.predict == "show":
                self.ShowPrediction(mdbsongs, prediction)
            elif args.predict == "store":
                self.StorePrediction(prediction)

        # show some statistics 
        if args.stats:
            self.ShowStatistics()


        return 0




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

