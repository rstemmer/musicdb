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

import os
import stat
import errno
import logging


class NamedPipe(object):
    """
    This module provides a class for getting command from a named pipe (FIFO).

    Args:
        path (str): absolute path where the FIFO is, or shall be created

    Raises:
        TypeError: when ``path`` is not of type ``str``
    """
    def __init__(self, path):
        if type(path) != str:
            raise TypeError("FIFO path must be of type string!")

        self.path = path



    def Create(self):
        """
        Creates the FIFO file if if does not exist.

        The access permissions are Read/Write for all (``0666``)

        Returns:
            *Nothing*

        Raises:
            OSError: Except when the FIFO already exists.
        """

        try:
            os.mkfifo(self.path, mode=0o666)
            os.chmod(self.path, 0o666)          # mkfifos mode-argument seems to be ignored.
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise



    def ReadLine(self):
        r"""
        This method reads a line from the FIFO, if there is a line.
        If nothing got written to the FIFO, ``None`` gets returned.
        The line does not have a trailing ``\n``.

        This method is non-blocking

        Example:

            .. code-block:: python

                pipe = NamedPipe("/tmp/test.fifo")
                
                while True:
                    line = pipe.ReadLine()
                    if line == "refresh":
                        UpdateCaches()

                    time.sleep(1)

        The file gets opened with ``O_NONBLOCK`` flag (non blocking read) and line buffering strategy.

        Returns:
            A line from the pipe or ``None``
        """

        def opener(path, flags):
            return os.open(path, os.O_RDONLY | os.O_NONBLOCK)

        with open(self.path, buffering=1, opener=opener) as fifo:
            try:
                line = fifo.read()
            except OSError as e:
                if e.errno != errno.EAGAIN or e.errno != errno.EWOULDBLOCK:
                    logging.error("Reading from FIFO failed with error \"%s\"!", str(e))
                line = None
            except Exception as e:
                logging.error("Reading from FIFO failed with exception \"%s\"!", str(e))
                line = None

        if line:
            line = line.rstrip()    # remove trailing \n
        return line



    def WriteLine(self, line):
        r"""
        Write a line into the named pipe.
        This method checks if the FIFO exists and rejects the line if not.
        If line is ``None`` or an empty string, nothing will be done.

        This method is blocking!

        Example:

            .. code-block:: python

                pipe = NamedPipe("/tmp/test.fifo")
                pipe.WriteLine("refresh")

        Args:
            line (str): Line to write into the named pipe (Without ``\n``!)

        Returns:
            *Nothing*
        """
        if not line:
            return
        
        if not self.Exists():
            logging.warning("FIFO \033[0;33m%s\033[1;33m does not exist! \033[1;30m(Command \"%s\" will not be send)", self.path, line)
            return

        line += "\n"

        try:
            fd = os.open(self.path, os.O_WRONLY)
        except OSError as e:
            logging.error("Open FIFO failed with error \"%s\"!", str(e))
            return

        try:
            os.write(fd, line.encode())
        except Exception as e:
            logging.error("Writing to FIFO failed with exception \"%s\"!", str(e))
        finally:
            os.close(fd)



    def Exists(self):
        """
        This method checks if the FIFO file for the named pipe exists.
        It not only checks the existence of the file but also if the file is a FIFO.

        Returns:
            ``True`` When the FIFO exists (and is a valid FIFO), otherwise ``False``
        """
        try:
            if stat.S_ISFIFO(os.stat(self.path).st_mode):
                return True
        except OSError:
            return False

        return False



    def Delete(self):
        """
        This function removes the named FIFO.

        Args:
            pidfile (str): Absolute path of a file to remove

        Returns:
            *Nothing*
        """
        if self.Exists():
            logging.debug("Removing FIFO %s", self.path)
            os.remove(self.path)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

