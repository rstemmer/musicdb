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
MusicAI is made to set genre tags to songs based on the tags set to albums.

This AI works for on a predefined set of genre.
This set can be defined in the MusicDB Configuration ``[MusicAI]->genrelist``.
The list is bound to the model name also set in the configuration.
If the gerelist changes, the model name should change, too.
Otherwise the datasets loose their relation to the genres.

This module changes two environment variables:

    * ``TF_CPP_MIN_LOG_LEVEL`` will be set to ``2`` to suppress printing warnings.
    * ``CUDA_VISIBLE_DEVICES`` will be set to ``0``. This is the GPU ID that will be used by TensorFlow.
"""

import logging
import json
import os
from lib.cfg.musicdb    import MusicDBConfig
from lib.hdf5storage    import HDF5Storage
from lib.filesystem     import Filesystem
from PIL                import Image
from tqdm               import tqdm
import numpy
import datetime
import random

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Do not show warnings
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # ID of GPU that shall be used
import tflearn
import tensorflow
from tflearn.layers.conv        import conv_2d, max_pool_2d
from tflearn.layers.core        import input_data, dropout, fully_connected, flatten
from tflearn.layers.estimator   import regression


class MusicAI(object):
    """

    Args:
        config: Instance of :class:`lib.cfg.musicdb.MusicDBConfig`.

    Raises:
        TypeError: If *config* is of an invalid type
    """
    def __init__(self, config):
        if type(config) != MusicDBConfig:
            logging.critical("FATAL ERROR: Config-class of unknown type \"%s\"!", str(type(config)))
            raise TypeError()

        self.config     = config
        self.fs         = Filesystem(self.config.music.path)
        self.genrelist  = self.config.musicai.genrelist
        self.modelname  = self.config.musicai.modelname
        self.modelfile  = self.config.musicai.modelpath + "/" + self.modelname + ".DCNN.tfl"


    def LoadModel(self, modelfilepath):
        """
        This method creates a neural network model and loads the trained data from the model in ``modelfilepath`` if the file ``modelfilepath + ".index"`` exists.
        The model will be created to run on the GPU if the related configuration is set to ``True``, otherwise the model will run on the CPU.
        Currently only ``/gpu:0`` and ``/cpu:0`` are supported.
        This method also resets *TensorFlows* and *TFLearn* internals by calling ``tensorflow.reset_default_graph()`` and ``tflearn.config.init_graph()``.
        The model can then be saved by :meth:`~mdbapi.musicai.MusicAI.SaveModel`

        If model creation fails, an exception gets raised.

        .. warning::

            The model data can become invalid if the code for creating the model (:meth:`~mdbapi.musicai.MusicAI.CreateModel`) changes the architecture of the model.

        Args:
            modelfilepath (str): Path where the models data are stored

        Returns:
            The TFLearn-model

        Raises:
            tensorflow.errors.InternalError: When creating the model failes.
        """
        # Reset tensorflow
        tensorflow.reset_default_graph()
        tflearn.config.init_graph()
        model = None

        # Create Model
        if self.config.musicai.usegpu:
            device = "/gpu:0"
        else:
            device = "/cpu:0"

        logging.debug("Create Model for device %s"%(device))

        try:
            with tensorflow.device(device):
                model = self.CreateModel()
        except tensorflow.errors.InternalError as e:
            ename = str(type(e).__name__)
            logging.exception(
                    "Creating Tensorflow Model for device \"%s\" failed with error \"%s\""
                    %(str(device), ename)
                    )
            print(
                    "\033[1;31mCreating Tensorflow Model for device \"%s\" failed with error \"%s\" \033[1;30m(My be related to Out-Of-Memory error for GPU usage)\033[0m"
                    %(str(device), ename)
                    )
            raise(e)

        # Load weights/biases if available
        if self.fs.Exists(modelfilepath+".index"):
            model.load(modelfilepath)

        return model


    def SaveModel(self, model, modelfilepath):
        """
        This method stores the configuration (weights, biases, …) in ``modelfilepath``.
        *TFLearn* creates multiple files with ``modelfilepath`` as suffix.

        The model can then be loaded by :meth:`~mdbapi.musicai.MusicAI.LoadModel`

        .. warning::

            The model data can become invalid if the code for creating the model (:meth:`~mdbapi.musicai.MusicAI.CreateModel`) changes the architecture of the model.

        Args:
            model: The *TFLearn* model of the neural network
            modelfilepath (str): The path and filename-(prefix) where the data of the model will be saved

        Returns:
            *Nothing*
        """
        model.save(modelfilepath)


    def GetStatistics(self):
        """
        This method returns statistics of the sizes of the training and feature sets.

        Returns:
            A dictionary with statistics or ``None`` if there is no training set

        Example:

            .. code-block:: python

                stats = musicai.GetStatistics()
                print("Set Size: ", stats["setsize"])
                print("Number of Songs in Set: ", stats["numofsongs"])

        """
        trainingfilepath = self.config.musicai.modelpath + "/" + self.modelname + ".h5"
        if not self.fs.Exists(trainingfilepath):
            return None

        trainingfile = HDF5Storage(trainingfilepath)
        # Check if the song was already added to the trainingset
        try:
            songset   = trainingfile.ReadDataset("songids")
            outputset = trainingfile.ReadDataset("outputs")
        except AssertionError:
            trainingfile.Close()
            return None

        stats = {}
        stats["setsize"]    = outputset.shape[0]
        stats["numofsongs"] = songset.shape[0]
        return stats


    
    # This MUST BE THREADSAFE to process multiple files at once
    # Accessing own database is allowed
    # returns file to spetrogram on success or None if something failed
    def CreateSpectrogram(self, songid, songpath):
        """
        This method creates the spectrograms used for the feature set.
        If the spectrogram already exists, it will skip the process.
        The spectrogram is a png-image.

        .. warning::

            This method must be thread safe to process multiple files at once

        This method represents the following shell commands:

        .. code-block:: bash

            # decode song to wave-file
            ffmpeg -v quiet -y -i $songpath "$songid-stereo.wav"

            # make mono wave file out of the stereo wave file
            sox "$songid-stereo.wav" "$songid-mono.wav" remix 1,2

            # create spectrogram out of the mono wave file
            sox "$songid-mono.wav" -n spectrogram -y $slizesize -X 50 -m -r -o "$songid.png"

        The temporary wave files are stored in the *musicai-tmppath*.
        They will be removed if the spectrogram was created successfully.
        Otherwise they will be kept.
        The spectrogram in the *musicai-specpath*.
        The slicesize denotes the height of the spectrogram which basically means the granularity of frequencies.
        This value gets increased by 1 to cover the offset (f=0).
        One column in the spectrogram represents 50ms of the song.
        All those variables can be set in the MusicDB Configuration.

        .. warning::

            Before changing the slice-size read the ``sox`` manpages for the ``-y`` parameter carefully.

        Args:
            songid: The song ID is used to create temporary files
            songpath (str): The path to the song that shall be analyzed

        Returns:
            path to the spectrogram
        """
        # prepare pathes
        sourcefile  = self.fs.AbsolutePath(songpath)
        wavefile    = self.config.musicai.tmppath  + "/" + str(songid) + "-stereo.wav"
        monofile    = self.config.musicai.tmppath  + "/" + str(songid) + "-mono.wav"
        spectrogram = self.config.musicai.specpath + "/" + str(songid) + ".png"

        # we are already done
        if self.fs.Exists(spectrogram):
            return spectrogram

        # create wave-file
        # ffmpeg -i audio.aac stereo.wav
        if not self.fs.Exists(wavefile):
            process = [
                    "ffmpeg",
                    "-v", "quiet",      # don't be verbose
                    "-y",               # overwrite existing file
                    "-i", sourcefile,
                    wavefile
                    ]
            try:
                self.fs.Execute(process)
            except Exception as e:
                logging.error("Error \"%s\" while executing: %s", str(e), str(process))
                return None

        # create mono-file
        # sox stereo.wav mono.wav remix 1,2
        if not self.fs.Exists(monofile):
            process = [
                    "sox",
                    wavefile,
                    monofile,
                    "remix", "1,2"
                    ]
            try:
                self.fs.Execute(process)
            except Exception as e:
                logging.error("Error \"%s\" while executing: %s", str(e), str(process))
                return None

        # create spectrogram
        # sox mono.wav -n spectrogram -Y 200 -X 50 -m -r -o mono.png
        if not self.fs.Exists(spectrogram):
            process = [
                    "sox",
                    monofile,
                    "-n", "spectrogram",
                    "-y", str(self.config.musicai.slicesize + 1),
                    "-X", "50",
                    "-m", "-r",
                    "-o", spectrogram
                    ]
            try:
                self.fs.Execute(process)
            except Exception as e:
                logging.error("Error \"%s\" while executing: %s", str(e), str(process))
                return None

        # remove tempfiles - Keep spectrogram because it looks so cool. Maybe it finds its place in the UI
        self.fs.RemoveFile(wavefile)
        self.fs.RemoveFile(monofile)
        return spectrogram
        
    
    # This MUST BE THREADSAFE to process multiple files at once
    # Accessing own database is allowed
    # returns True on success
    def CreateFeatureset(self, songid, songpath):
        """
        This function generates the feature set for the MusicAI.
        The features are generated by the following steps:

            #. First step is to create the spectrogram calling :meth:`~mdbapi.musicai.MusicAI.CreateSpectrogram`.
            #. Next it takes slices from the resulting image and converts it into a normalized *numpy* array.
            #. The begin and end of a song will be chopped of and gets ignored.

        A slicesize can be defind in the MusicDB Configuration under musicai->slicesize. **Be careful with this configuration and check the influence to other methods in this class!**
        The first 10 and the last 10 slices will be skipped to avoid unnecessary much intro/outro-data-noise.
        
        The resulting data (a feature) is a *numpy* 3D (slicesize, slicesize, 1) matrix of type float in range of 0.0 to 1.0.
        This matrix of all features of a song gets stored in a HDF5 file under ``$spectrograms/$SongID.h5``

        Args:
            songid: ID of the song the feature set belongs to
            songpath (str): path to the song that shall be analyzed

        Returns:
            ``True`` on success, otherwise ``False``

        Example:

            .. code-block:: python

                musicai = MusicAI("./musicdb.ini")
                musicai.CreateFeatureset(mdbsong["id"], mdbsong["path"]):
        """
        # Create Spectrogram
        spectrogram = self.CreateSpectrogram(songid, songpath)
        if not spectrogram:
            return False

        # Open it and make raw data out of the image
        image           = Image.open(spectrogram)
        width, height   = image.size
        slicesize       = self.config.musicai.slicesize
        numslices       = int(width / slicesize) - 20   # \_ skip slices (intro+outro)
        startoffset     = 10 * slicesize                # / 

        if numslices <= 0:
            logging.warning("song %s too small! \033[1;30m(do not use for featureset)"%(songpath))
            return False
    
        # create data
        dataset = numpy.zeros((numslices, slicesize, slicesize, 1))
        for i in range(numslices):
            # Crop into slices
            startpixel = i * slicesize + startoffset
            imageslice = image.crop((startpixel, 0, startpixel + slicesize, slicesize))

            # Make numpy-arrays out of it
            data = numpy.asarray(imageslice, dtype=numpy.uint8) # image -> ndarray
            data = data / 255.0                                 # [0 … 255] -> [0.0 … 1.0] (and makes float)
            data = data.reshape((slicesize, slicesize, 1))      # X² -> X³

            # Store the feature dataset
            dataset[i] = data

        # Open storage for the features
        featurefilepath = self.config.musicai.specpath + "/" + str(songid) + ".h5"
        featurefile     = HDF5Storage(featurefilepath)
        featurefile.WriteDataset("featureset", dataset)
        featurefile.Close()
        return True


    def HasFeatureset(self, songid):
        """
        This method checks if a song has already a feature set.
        If there is a HDF5 file in the spectrogram directors the method assumes that this file contains the feature set.
        The file gets not read.
        The png encoded spectrogram is not the final feature set and so its existence is not relevant for this method.

        Args:
            songid: ID of the song that shall be checked

        Returns:
            ``True`` if the songs feature set is available, otherwise ``False``
        """
        featurefilepath = self.config.musicai.specpath + "/" + str(songid) + ".h5"
        if self.fs.Exists(featurefilepath):
            return True
        return False


    def AddSongToTrainingset(self, songid, genre):
        """
        This method can be used to add a song to the available training sets.
        To do so, first the feature set must be created.

        The feature set file gets read and a genre vector generated.
        The resultuing two sets (*inputs* = feature set and *outputs* = genre vector) will be stored in the training file.

        The **inputs** are a HDF5 dataset handler shaping a numpy-array of size *n* of input matrices:
        ``(n, slicesize, slicesize, 1)``

        The **outputs** are a HDF5 dataset handler shaping a numpy-array of size *n* of genre-vectors formatted as shown in :meth:`mdbapi.musicai.MusicAI.GetGenreMatrix`:
        ``(n, 4, 1)``

        The genre name should be the same as the related genre tag is named in the database.
        It also must be part of the list of genres this AI works with.

        Args:
            songid: ID of the song that shall be used for training
            genre (str): Lower case name of the genre (as stored in the database) the song belongs to

        Returns:
            ``True`` if the song has a feature set so that it was added to the database. Otherwise ``False``

        Example:

            .. code-block:: python

                musicai = MusicAI("./musicdb.ini")
                musicai.CreateFeatureset(mdbsong["id"], mdbsong["path"]):
                musicai.AddSongToTrainingset(mdbsong["id"], "metal")

        """
        if not genre in self.genrelist:
            logging.error("The genre \"%s\" is not in the genrelist: \"%s\"!", genre, str(self.genrelist))
            return False

        if not self.HasFeatureset(songid):
            logging.waring("Song with id %s does not have a featureset", str(songid))
            return False

        featurefilepath  = self.config.musicai.specpath  + "/" + str(songid)    + ".h5"
        trainingfilepath = self.config.musicai.modelpath + "/" + self.modelname + ".h5"

        featurefile  = HDF5Storage(featurefilepath)
        trainingfile = HDF5Storage(trainingfilepath)

        # Check if the song was already added to the trainingset
        try:
            songids = trainingfile.ReadDataset("songids")
        except AssertionError:
            songids = []

        if songid in songids:
            logging.waring("Song with id %s does already exist in trainingset", str(songid))
            featurefile.Close()
            trainingfile.Close()
            return False

        # Read Featureset
        featureset   = featurefile.ReadDataset("featureset")    # read features
        setsize      = featureset.shape[0]                      # determin size of the workingset
        genrevector  = self.GetGenreMatrix()[genre]             # get genre vector
        genrevector  = numpy.array(genrevector)                 # \_ create outputs-set
        genreset     = numpy.tile(genrevector, (setsize, 1))    # /
        songidset    = numpy.tile(numpy.array(songid), (1,1))

        # Write trainingset
        trainingfile.WriteDataset("inputs",  featureset)
        trainingfile.WriteDataset("outputs", genreset)
        trainingfile.WriteDataset("songids", songidset)

        featurefile.Close()
        trainingfile.Close()
        return True


    def CreateModel(self):
        """
        This method creates and returns the following deep convolutional neural network.

        The architecture of the network is close to the one provided the following blog article:
        
            Julien Despois, *"Finding the genre of a song with Deep Learning -- A.I. Odyyssey part. 1"*, Nov. 2016, internet (non-scientific source), https://chatbotslife.com/finding-the-genre-of-a-song-with-deep-learning-da8f59a61194

        Inside the method there are some configurable variables to easily change some basic settings of the network:

            * ``useflatten = True``: Create a flatten-layer between the convolutional part and the fully connected end
            * ``keepprob = 0.5``: Probability of an input gets propagated through the dropout-layer
            * ``activation = "elu"``: Name of the activation function used for the convolutional networks as used by *tensorflow*
            * ``weightinit = "Xavier"``: Initialisation function for the convolutional layers
            * ``weightdecay = 0.001``
            * ``learningrate = 0.001``

        The reason for using ``"elu"`` as activation function can be found in the following paper:

            Djork-Arné Clevert, Thomas Unterthiner and Sepp Hochreiter, *"Fast and Accurate Deep Network Learning by Exponential Linear Units (ELUs)"*, Nov. 2015, CoRR (scientific source), https://arxiv.org/abs/1511.07289


        Returns:
            The created TFLearn-model

        """
        slicesize   = self.config.musicai.slicesize      # the slice size of the spectrograms define the size of the input layer
        genrecount  = len(self.config.musicai.genrelist) # number of genres and so the number of output neurons

        # Some general architechture configuration
        useflatten  = True      # Use a flatten layer afrer the convolutional layers
        keepprob    = 0.5       # configures the dropout layer
        activation  = "elu"     # elu? warum nicht das übliche relu? -> Weil besser: https://arxiv.org/abs/1511.07289
        weightinit  = "Xavier"  # Initialisation function for the convolutional layers
        weightdecay = 0.001
        learningrate= 0.001

        convnet = input_data(shape=[None, slicesize, slicesize, 1], name='input')

        convnet = conv_2d(convnet,  64, 2, activation=activation, weights_init=weightinit, weight_decay=weightdecay)
        convnet = max_pool_2d(convnet, 2)

        convnet = conv_2d(convnet, 128, 2, activation=activation, weights_init=weightinit, weight_decay=weightdecay)
        convnet = max_pool_2d(convnet, 2)

        convnet = conv_2d(convnet, 256, 2, activation=activation, weights_init=weightinit, weight_decay=weightdecay)
        convnet = max_pool_2d(convnet, 2)

        convnet = conv_2d(convnet, 512, 2, activation=activation, weights_init=weightinit, weight_decay=weightdecay)
        convnet = max_pool_2d(convnet, 2)

        if useflatten:
            convnet = flatten(convnet)

        convnet = fully_connected(convnet, 1024, activation=activation, weight_decay=weightdecay)
        convnet = dropout(convnet, keepprob)

        convnet = fully_connected(convnet, genrecount, activation='softmax', weight_decay=weightdecay)
        convnet = regression(convnet, 
                optimizer       = 'rmsprop', 
                loss            = 'categorical_crossentropy', 
                learning_rate   = learningrate
                )

        model = tflearn.DNN(convnet,
                tensorboard_verbose = 3,    # many nice graphs inside tensorboard
                tensorboard_dir     = self.config.musicai.logpath
                )

        return model


    def GetGenreMatrix(self):
        r"""
        This method returns a dictionary with the categorization vector for each genre.
        When training a neural network for categorizing, each element of the result-vector is mapped to one category.
        This static mapping is returned by this method.
        The matrix gets dynamic generated out of the configuration of MusicDB.
        The configured genre list gets just transformed into the matirx.

        For example, the mapping for the genrelist ``Metal, NDH, Gothic, Elector`` is the following:

        .. math::

            \begin{pmatrix}
                \text{Metal}\\
                \text{NDH}\\
                \text{Gothic}\\
                \text{Electro}
            \end{pmatrix}

        The format of the mapping is a dictionary with each genre as key.
        Each entry in the dictionary is a vector with the related cell set to 1.0 and the other cells to 0.0. For *Gothic* music, the vector would look like this:

        .. math::

            \text{Gothic} = \begin{pmatrix}
                0.0\\
                0.0\\
                1.0\\
                0.0
            \end{pmatrix}

        Returns:
            A dictionary with expected-prediction-vectors for training
        """

        matrix = {}
        for index, genre in enumerate(self.genrelist):
            matrix[genre]        = [0.0] * len(self.genrelist)
            matrix[genre][index] = 1.0

        return matrix


    def HasTrainingset(self, songid):
        """
        This method checks if a song is used for training - if there exists a training set.
        The check is done in two steps:

            #. Does the training set file for the model exist.
            #. Is the song ID listed in the set of training songs in the training set file.

        Args:
            songid: ID of the song that shall be checked

        Returns:
            ``True`` if there exists a training set, otherwise ``False``
        """
        trainingfilepath = self.config.musicai.modelpath + "/" + self.modelname + ".h5"
        if not self.fs.Exists(trainingfilepath):
            return False

        trainingfile = HDF5Storage(trainingfilepath)
        # Check if the song was already added to the trainingset
        try:
            songids = trainingfile.ReadDataset("songids")
        except AssertionError:
            trainingfile.Close()
            return False

        # if the song is listed in this list, it exists in the trainingset
        if songid in songids:
            trainingfile.Close()
            return True

        return False


    def PerformTraining(self):
        """
        This method performs the training of the neural network.
        The training is done in several steps:

            #. Loading the model using :meth:`~mdbapi.musicai.MusicAI.LoadModel`
            #. Loading the training set from file
            #. Performing the training itself. This can be canceled by pressing ctrl-c.
            #. Saving new model state by calling :meth:`~mdbapi.musicai.MusicAI.SaveModel`

        The size of the training set is determined by the MusicDB Configuration.

        Each run gets logged in the log-directory that can be configured in the MusicDB Configuration.
        The name of each run is the module-name extended with the date (YY-MM-DD) and time (HH:MM) of the training.
        These logs can be used for visualization using TensorBoard.

        Returns:
            ``True`` on success, otherwise ``False``
        """
        # shorten config
        runid     = self.modelname + " " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        batchsize = self.config.musicai.batchsize
        epoch     = self.config.musicai.epoch

        # load model
        print("\033[1;34mLoading model … \033[0m")
        model = self.LoadModel(self.modelfile)

        # getting features
        print("\033[1;34mLoading training data … \033[0;36m")
        trainingfilepath = self.config.musicai.modelpath + "/" + self.modelname + ".h5"
        trainingfile     = HDF5Storage(trainingfilepath)
        try:
            inputset         = trainingfile.ReadDataset("inputs")
            outputset        = trainingfile.ReadDataset("outputs")
        except AssertionError as e:
            logging.exception("Reading the Trainingset failed!")
            print("\033[1;31m … failed!\033[0m")
            trainingfile.Close()
            return False

        # run training
        print("\033[1;34mRunning training process … \033[0m")
        try:
            model.fit(
                    inputset, outputset,
                    n_epoch         = epoch,
                    batch_size      = batchsize,
                    shuffle         = True, 
                    validation_set  = 0.01,
                    snapshot_step   = 100, 
                    show_metric     = True, 
                    run_id          = runid)
        except KeyboardInterrupt as e:
            logging.info("Training canceled by user. \033[1;30m(Progress will not be saved)\033[0m")
            print("\033[1;33m … canceled by user. \033[1;30m(Progress will not be saved)\033[0m")
            trainingfile.Close()
            return False

        # save model
        print("\033[1;34mSaving Model … \033[0m")
        self.SaveModel(model, self.modelfile)
        trainingfile.Close()
        return True


    def PerformPrediction(self, songid):
        r"""
        This method starts a prediction of the genre for a song addressed by its song ID.
        It returns a vector of confidence for the genres as described in :meth:`~mdbapi.musicai.MusicAI.GetGenreMatrix`.
        The confidence is the average of all features in the set.
        The featureset gets loaded from the related HDF5 file in the spectrogram directory configured
        in the MusicDB Configuration.
        A feature set can be created using the :meth:`~mdbapi.musicai.MusicAI.CreateFeatureset`
        If the file does not exist ``None`` gets returned.

        The result is calculated the following way from the set *P* of predictions based on a feature
        for each genre in the set of genres *G*.

        .. math::

            p_{g} = \frac{1}{\lvert P \rvert}\sum_{i}^{\lvert P \rvert}{p_{i}} \qquad p_{i} \in P; \; g \in G

        Args:
            songid: The ID of the song that shall be categorized

        Returns:
            A confidence-vector for the genres that were predicted, or ``None`` if an error occurs

        Example:
            
            .. code-block:: python

                # Create a feature set if there is none yet
                if not musicai.HasFeatureset(mdbsong["id"]):
                    musicai.CreateFeatureset(mdbsong["id"], mdbsong["path"])

                # Perform prediction
                confidence = musicai.PerformPrediction(mdbsong["id"])

                if confidence == None:
                    print("Prediction Failed! No featureset available?")
                    return

                # Print results
                # The order of the Genre-List is important! The mapping (index, genre) must be correct!
                for index, genre in enumerate(config.musicai.genrelist):
                    print("%.2f: %s" % (confidence[index], genre))

        """
        if not self.HasFeatureset(songid):
            logging.warning("Song with id %s does not have a featureset", str(songid))
            return None

        # load features
        featurefilepath = self.config.musicai.specpath + "/" + str(songid) + ".h5"
        featurefile     = HDF5Storage(featurefilepath)
        try:
            featureset  = featurefile.ReadDataset("featureset")
        except AssertionError as e:
            logging.error("Reading Featureset failed with error %s!", str(e))
            featureset = None
            featurefile.Close()

        if featureset == None:
            return None

        # load model
        model = self.LoadModel(self.modelfile)

        # run prediction
        predictionset = model.predict(featureset)
        featurefile.Close()

        # accumulate results
        numofgenres = len(self.genrelist)
        prediction = [0.0] * numofgenres

        for entry in predictionset:
            for i in range(numofgenres):
                prediction[i] += entry[i]
        
        for i in range(numofgenres):
            prediction[i] /= len(predictionset)

        return prediction



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

