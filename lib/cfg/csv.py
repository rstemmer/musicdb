#!/usr/bin/env python3

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
This module handles the reading and writing of csv-files.
"""

import csv

class CSVFile(object):
    """
    The class does not cache the files content.
    Every read access accesses the actual file.
    Writing does the file update.

    The csv files this class works with must have the following dialect:

        * delimiter:  ``,`` 
        * escapechar: ``\``
        * quotechar:  ``"``
        * quoting:    ``csv.QUOTE_NONNUMERIC``


    Args:
        path (str): Name of the csv file the class works with
    """

    def __init__(self, path):

        self.path       = path
        self.delimiter  = ","
        self.escapechar = "\\"
        self.quotechar  = "\""
        self.quoting    = csv.QUOTE_NONNUMERIC


    def Read(self):
        """
        Reads the file an returns its rows as a list.
        """
        with open(self.path) as csvfile:
            rows = csv.reader(csvfile, 
                    delimiter  = self.delimiter,
                    escapechar = self.escapechar,
                    quotechar  = self.quotechar,
                    quoting    = self.quiting)

            # Format of the lines: rel. source-path, rel. destination-path
            rows = list(rows) # Transform csv-readers internal iterateable object to a python list.
        return rows
  

    def Write(self, rows):
        """
        Write rows into the csv file
        """
        with open(self.path, "w") as csvfile:
            csvwriter = csv.writer(csvfile, 
                    delimiter  = self.delimiter,
                    escapechar = self.escapechar,
                    quotechar  = self.quotechar,
                    quoting    = self.quiting)
            csvwriter.writerows(rows)
        return None

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

