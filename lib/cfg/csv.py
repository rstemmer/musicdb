#!/usr/bin/env python3

# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2018  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module handles the reading and writing of csv-files.
"""

import csv

class CSVFile(object):
    r"""
    This class reads `Comma Separated Value (CSV) <https://tools.ietf.org/html/rfc4180>`_ files as used by MusicDB.

    The class does not cache the files content.
    Every read access accesses the actual file.
    Writing does the file update.

    The csv files this class works with must have the following dialect:

        * first line is a header line
        * delimiter:  ``,`` 
        * escapechar: ``\``
        * quotechar:  ``"``
        * quoting:    ``csv.QUOTE_NONNUMERIC``
        * line break: ``\n``

    It is allowed to modify the CSV files with external programs, but not guaranteed that
    MusicDB will not overwrite the changes.
    It is recommended to only read the files outside of MusicDB.
    Do not change the layout of the files!

    Args:
        path (str): Absolute path of the csv file the class works with
    """

    def __init__(self, path):

        self.path       = path
        self.delimiter  = ","
        self.escapechar = "\\"
        self.quotechar  = "\""
        self.quoting    = csv.QUOTE_NONNUMERIC


    def Read(self):
        """
        This method reads the file and returns its a table represented as a list of dictionaries.
        The dictionary has a key for each column in the header of the file.
        So each entry in the list represents one row of the file,
        and each entry in the dictionary represents one cell or column in that row.

        Example:

            .. code-block:: js

                name, id
                a, 1
                b, 2
                c, 3

            .. code-block:: python

                table = csv.Read()
                print(table)

            .. code-block:: js

                [
                    {'name': 'a', 'id': 1},
                    {'name': 'b', 'id': 2},
                    {'name': 'c', 'id': 3}
                ]

                
        Returns:
            A list of dictionaries with one entry or each cell. When the file does not exist, ``None`` gets returned.

        Raises:
            StopIteration: When the CSV file is empty
        """
        table = None    # in case the file does not exist

        with open(self.path) as csvfile:
            reader = csv.reader(csvfile, 
                    delimiter  = self.delimiter,
                    escapechar = self.escapechar,
                    quotechar  = self.quotechar,
                    quoting    = self.quoting)

            # read header and prepare a dict with a list for each column
            header = next(reader, None)
            table  = []

            # read value rows and map them to the dict columns
            for csvrow in reader:
                tablerow = {}
                for index, value in enumerate(csvrow):
                    key           = header[index]
                    tablerow[key] = value

                table.append(tablerow)

        return table 
  

    def Write(self, table, header=None):
        """
        Write rows into the csv file.
        The first row will be the header of the table.

        Example:

            .. code-block:: js

                [
                    {'name': 'a', 'id': 1},
                    {'name': 'b', 'id': 2},
                    {'name': 'c', 'id': 3}
                ]

            .. code-block:: python

                print(table)
                csv.Write(table)
                # or: csv.Write(table, ["name", "id"])

            .. code-block:: js

                name, id
                a, 1
                b, 2
                c, 3


        Args:
            table (list): A list with dictionaries of values for each column
            header (list): The header of the CSV file. Each entry must also be a key in the ``table`` dictionary! If ``None``, then all keys of the dictionaries will be used.

        Returns:
            ``None``

        Raises:
            TypeError: when ``table`` is not a list
            ValueError: when the ``table`` list has not at least one entry
            TypeError: when the ``table`` list elements are not dictionaries
            TypeError: when ``header`` is not a list and not ``None``
        """
        # Check table
        if type(table) != list:
            raise TypeError("The table argument must be of type list!")
        if len(table) < 1:
            raise ValueError("The table argument must be a list with at least one entry!")
        if type(table[0]) != dict:
            raise TypeError("The table argument must be a list with elements of type dict!")

        # Check header
        if header == None:
            header = list(table[0].keys())

        if type(header) != list:
            raise TypeError("The header argument must be of type list!")

        with open(self.path, "w") as csvfile:
            writer = csv.writer(csvfile, 
                    delimiter  = self.delimiter,
                    escapechar = self.escapechar,
                    quotechar  = self.quotechar,
                    quoting    = self.quoting)

            # write header
            writer.writerow(header)

            for row in table:
                # Write row
                csvrow = [row[key] for key in header]
                writer.writerow(csvrow)

        return None

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

