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
This module handles HDF5 files for the MusicDB project.
Its main advantage is to handle huge sets of binary data.

The data handling and storage is done by the `h5py <http://www.h5py.org/>`_ library and the `HDF5 <https://support.hdfgroup.org/HDF5/>`_ file format.

Example:

    .. code-block:: python

        # Open storage
        storage = HDF5Storage("./test.h5")

        # Generate some datasets
        din  = numpy.random.rand(1000, 16, 16)
        dout = numpy.zeros((1000, 4))

        # Write datasets
        storage.WriteDataset("inputs",  din)
        storage.WriteDataset("outputs", dout)

        # Read datasets
        inputset  = storage.ReadDataset("inputs")
        outputset = storage.ReadDataset("outputs")

        # Print datasets
        setlen = inputset.shape[0]
        for i in range(setlen):
            print(inputset[i])
            print("="*10)

        # Close storage
        storage.Close()
"""

import h5py

class HDF5Storage(object):
    """
    This class handles HDF5 files for the MusicDB project.
    It opens the HDF5 file given to the constructor.
    If the file does not exist, a new one will be created.
    All datasets have the following format:

        * Dimension 0 defines the size of the set.
        * The sets are unlimited
        * The chuncksize is 1024 elements
        * The data gets **NOT** compressed. - It took too much time to decompress!

    The creation of a dataset is done as shown in the following code:

    .. code-block:: python

        shape     = data.shape
        maxshape  = (None,) + shape[1:]
        chunkshape= (1024,) + shape[1:]

        dataset = self.datafile.create_dataset(
                name, 
                shape, 
                maxshape=maxshape, 
                chunks=chunkshape
                )

    Args:
        path (str): path to the HDF5 file that shall be processed. It may or may not exist.

    """
    def __init__(self, path):
        self.path     = path
        self.datafile = h5py.File(self.path, "a")


    def Close(self):
        """
        Close the HDF5 file.

        Returns:
            *Nothing*
        """
        if not self.datafile:
            raise AssertionError("No file opend!")
        self.datafile.close()
        self.datafile = None


    def __CreateDataset(self, name, data):
        """
        .. warning::

            Do not call this method directly. Just call the :meth:`lib.hdf5storage.HDF5Storage.WriteDataset` method.

        This method creates a new dataset.
        It will be called when :meth:`lib.hdf5storage.HDF5Storage.WriteDataset` cannot finde a set with the name *name*.
        After creation, the data will also be stored.

        Args:
            name (str): Name of the dataset the data shall be stored at or appended to
            data: the *numpy* data to store

        Returns:
            *Nothing*
        """
        if not self.datafile:
            raise AssertionError("No file opend!")

        shape     = data.shape
        maxshape  = (None,) + shape[1:]
        chunkshape= (1024,) + shape[1:]

        dataset = self.datafile.create_dataset(
                name, 
                shape, 
                maxshape=maxshape, 
                chunks=chunkshape
                )
        dataset[...] = data


    def WriteDataset(self, name, data):
        """
        Append *data* to the dataset with name *name* if it exists.
        If it does not exist it will be created.

        The dimension with index 0 is the number of elements in the set.
        The rest of the dimension tuple is the actual dimension of one data entry in the set.
        If the existing dataset has the dimension (z, y, x) and the *data* one (a, y, x),
        the resulting dimension is (z+a, y, x).

        Args:
            name (str): Name of the dataset the data shall be stored at or appended to
            data: the *numpy* data to store

        Returns:
            *Nothing*

        Example:

            .. code-block:: python
                
                entry   = numpy.zeros((10, 20)) # create a 10x20 matrix with zeros
                dataset = [entry, entry, entry] # create a dataset with 3 matrices

                storage.WriteDataset("testdata", dataset)
                storage.WriteDataset("testdata", entry)
                
                dataset = storage.ReadDataset("testdata")
                print(dataset.shape) # prints (4,10,20)

        """
        if not self.datafile:
            raise AssertionError("No file opend!")

        if not name in self.datafile:
            self.__CreateDataset(name, data)
            return

        dataset = self.datafile[name]
        oldlen  = dataset.shape[0]
        newlen  = oldlen + data.shape[0]
        newshape = (newlen,) + dataset.shape[1:]

        dataset.resize(newshape)
        dataset[oldlen: ] = data


    def ReadDataset(self, name):
        """
        This method returns the h5py dataset with the name *name*.
        In fact, this method returns only a handler to the HDF5 reader implementation of the h5py library.
        This can be used to iterate over a large set of data.

        Args:
            name (str): Name of the dataset that shall be read

        Returns:
            a h5py dataset

        Raises:
            AssertionError: When file not opened or dataset does not exist

        Example:

            .. code-block:: python
                
                # print the dataset testdata
                dataset = storage.ReadDataset("testdata")
                for i in range(dataset.shape[0]):
                    print(dataset[i])
        """
        if not self.datafile:
            raise AssertionError("No file opend!")
        if not name in self.datafile:
            raise AssertionError("Dataset does not exist!")
        return self.datafile[name]


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

