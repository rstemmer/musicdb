MusicAI
=======

MusicAI uses a Convolutional Deep Neural Network (CDNN) to categorize music by its main genre.

External Dependencies
---------------------

*MusicAI* is using the `TensorFlow <https://www.tensorflow.org/>`_ library. In detail, it uses the high level API `TFLearn <http://tflearn.org/>`_.
With TensorFlow comes a tool called `TensorBoard <https://www.tensorflow.org/get_started/summaries_and_tensorboard>`_ 
that provides detail about the model and training process and progress.
To access the data of the MusicAIs neural network via TensorBoard, the following command must be executed.
Paths are depending on the MusicDB configuration.

.. code-block:: bash

   tensorboard --logdir /data/musicdb/musicai/log

After starting ``tensorboard``, the data can be accessed using a web browser.
The tool prints the port number to *stdout*.

Training Time
-------------

The training time of the API depends on the used hardware (GPU recommended!).
To estimate the time the training needs this section may help you.

First of all a test run must be done to get a basic time estimation of a small training session.
After the run, the time used for the training gets printed to the screen.

.. math::
   :nowrap:

   \begin{align*}
   e_m & = 1                     & \text{training epoches} \\
   s_m & = 2000                  & \text{feature set size} \\
   t_m & =                       & \text{measured time from testrun}\\
   t   & = \frac{t_m}{e_m \cdot s_m} & \text{avarage time per training step}
   \end{align*}

The real time the full training will take can be calculated with *e* and *s* as they will be used then.

.. math::
   :nowrap:

   \begin{align*}
   e_t & = 20                & \text{training epoches} \\
   s_t & = 120000            & \text{feature set size} \\
   t_e & = t \cdot e_t \cdot s_t & \text{esitmated training time}
   \end{align*}

On my workstation, it took 39:52 hours to train the network with 176433 features from 2138 songs in 20 epochs.

   * **CPU:** Intel i7-5930K CPU @ 3.50GHz
   * **GPU:** nVidia GeForce GTX 1070 (8GiB)
   * **RAM:** Kingston HyperX Savage DDR4-Speicher 3000MHz (16GiB)
   * **SSD:** Samsung 950 Pro M.2

Removing an old model
---------------------

To remove an old model the following steps are needed, with *modelpath* and *logpath* as set in the MusicDB Configuration.

.. code-block:: bash

   rm $modelpath/*
   rm -r $logpath/*

Data Handling
-------------

For training the CDNN, a lot of data is needed.
In my case, it is over 16GiB of input data.
This cannot be handled using only a sqlite3 database from that all data gets loaded into a python list object.

So for training and the training data, the `h5py <http://www.h5py.org/>`_ library is used and the data gets stored in a `HDF5 <https://support.hdfgroup.org/HDF5/>`_ file.
In context of MusicDB, use the :class:`lib.hdf5storage.HDF5Storage` class.

There are two categories of files:

   The `Featureset`_:
      This is a file for each song named ``$spectrogrampath/$SongID.h5``. This file contains the features itself and nothing more.

   The `Trainingset`_:
      This is a much larger file named ``$modelpath/$AIName.h5`` containing lots of features and its annotation.

Featureset
^^^^^^^^^^

This file has only one dataset called *featureset*.
It is stored in the same directory the spectrogram images are stored.

The dimension of the featureset is ``(x, slicesize, slicesize, 1)``. 
With *x* as the amount of features in the featureset, 
and *slicesize* the configured size of spectrogram-slices used to create the feature.
The additional dimension is needed by *TensorFlow*


Trainingset
^^^^^^^^^^^

This file is organized as follows

   * *inputs*: input feature set (``chunksize=(1024,128,128,1)``)
   * *outputs*: output vectors (categories) (``chunksize=(1024,4,1)``)
   * *songids*: list of all song IDs thats features are in the featureset

The *songids* can be used to check whether a song is included in the training set or not.


MusicAI Module
--------------

.. automodule:: mdbapi.musicai

MusicAI Class
-------------

.. autoclass:: mdbapi.musicai.MusicAI
   :members:

