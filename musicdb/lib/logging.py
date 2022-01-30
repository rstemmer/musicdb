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
This library provides the excessive logging system of MusicDB.

For details about the file and directory structure for logging information into files see :doc:`/basics/data`.
"""

import logging
import sys
import os
import stat
from systemd import journal

class MDBLogFormatter(logging.Formatter):
    """
    This class handles log messages.
    The class is derived from `logging.Formatter <https://docs.python.org/3/library/logging.html#formatter-objects>`_.

    It sets the *loglevel* of the modules listed in configuration under ``[log]->ignore`` to WARNING.

    Furthermore this class defines how the log entries will look like.

    Args:
        ignorelist: List of module names that shall not appear in the logs
    """

    start_fmt= "\033[1;34m LOG[\033[0;34m%(asctime)s\033[1;34m|"
    file_fmt = "\033[0;35m%(filename)s\033[0;34m:\033[0;35m%(funcName)s\033[0;34m.\033[0;31m%(lineno)d\033[1;34m: "
    short    = "\033[0;35m%(filename)s\033[1;34m: "

    #debug_format    = "\033[1;34m LOG[\033[0;35mDEBUG\033[1;34m] " + file_format + "\033[1;30m%(message)s [%(module)s]"
    debug_format    = start_fmt + "\033[0;35mDEBUG\033[1;34m] " + file_fmt + "\033[1;30m%(message)s\033[0m"
    info_format     = start_fmt + "\033[0;36mINFO \033[1;34m] " + short    + "\033[1;34m%(message)s\033[0m"
    warning_format  = start_fmt + "\033[0;33mWARN \033[1;34m] " + file_fmt + "\033[1;33m%(message)s\033[0m"
    error_format    = start_fmt + "\033[0;31mERROR\033[1;34m] " + file_fmt + "\033[1;31m%(message)s\033[0m"
    critical_format = start_fmt + "\033[1;31mFATAL\033[1;34m] " + file_fmt + "\033[1;31m%(message)s\033[0m"
    # %(asctime)s


    def __init__(self, ignorelist):
        logging.Formatter.__init__(self, datefmt="%Y-%m-%d %H:%M:%S")
        # reduce spam from third party libraries
        for entry in ignorelist:
            logging.getLogger(entry).setLevel(logging.WARNING)
        logging.root.setLevel(logging.DEBUG)


    def format(self, record):
        """
        Overloads the `format method of logging.Formatter <https://docs.python.org/3/library/logging.html#logging.Formatter.format>`_
        to apply coloring and add additional information to the messages.
    
            Source: http://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level
        """
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = MDBLogFormatter.debug_format
        elif record.levelno == logging.INFO:
            self._style._fmt = MDBLogFormatter.info_format
        elif record.levelno == logging.WARNING:
            self._style._fmt = MDBLogFormatter.warning_format
        elif record.levelno == logging.ERROR:
            self._style._fmt = MDBLogFormatter.error_format
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = MDBLogFormatter.critical_format

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


class MusicDBLogger():
    """
    This class provides the logging management itself and handles the logging configuration.
    """
    loglevelmap = {}
    loglevelmap["DEBUG"]    = logging.DEBUG
    loglevelmap["INFO"]     = logging.INFO
    loglevelmap["WARNING"]  = logging.WARNING
    loglevelmap["ERROR"]    = logging.ERROR
    loglevelmap["CRITICAL"] = logging.CRITICAL

    def __init__(self):
        # create default output handler setup
        self.handler = []   # list of handler. At least one: stderr. Maybe a file for more details
        self.Reconfigure()



    def SetFilePermissions(self, path):
        """
        This method set the access permission of a file to "rw-rw----".
        If the file in *path* cannot be accessed, an error gets printed to ``stderr``
        and MusicDB gets exited with error code ``1``.

        Args:
            path (str): Absolute path to a log file

        Returns:
            ``True`` on success. On Error MusicDB gets terminated.
        """
        try:
            with open(path, "a"):
                pass
        except Exception as e:
            print("\033[1;31mFATAL ERROR: Opening log file failed with error: %s\033[0m (%s)"%(str(e), str(path)), file=sys.stderr)
            exit(1)

        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP) # rw-rw----
        except Exception as e:
            pass
        #print("\033[1;33mWARNING: Setting permissions of log file failed with error: %s\033[0m (%s)"%(str(e), str(path)), file=sys.stderr)
        return True



    def Reconfigure(self, logpath="stderr", loglevelname="DEBUG", debugpath=None, config=None):
        """
        This method allows to reconfigure the setting for the MusicDB logger.

        Args:
            path (str): A "path" where the logs will be written. Use ``"stdout"`` or ``"stderr"`` to show them on the screen. Use ``"journal"`` to write to SystemDs journal.
            loglevelname (str): Name of the lowest log level that shall be shown: ``"DEBUG"``, ``"INFO"``, ``"WARNING"``, ``"ERROR"`` or ``"CRITICAL"``.
            debugpath (str): Path to a file where everything (DEBUG) shall be logged in. ``None`` for not such a file.
            config: A MusicDB Configuration object that hold the ignore list. If ``None`` the configuration will not be appied.

        Returns:
            *nothing*
        """
        loglevelname = loglevelname.upper()
        loglevel     = MusicDBLogger.loglevelmap[loglevelname]

        # remove old handlers
        for h in self.handler:
            logging.root.removeHandler(h)
            h.flush()
            h.close()
        self.handler = []

        # primary handler
        if logpath != None and logpath != "/dev/null":
            if logpath == "stdout":
                phandler = logging.StreamHandler(sys.stdout)
            elif logpath == "stderr":
                phandler = logging.StreamHandler(sys.stderr)
            elif logpath == "journal":
                phandler = journal.JournalHandler(SYSLOG_IDENTIFIER="musicdb")
            else:
                self.SetFilePermissions(logpath)
                phandler = logging.FileHandler(logpath)

            phandler.setLevel(loglevel)
            self.handler.append(phandler)

        # secondary handler
        if debugpath != None and debugpath != "/dev/null":
            self.SetFilePermissions(debugpath)
            shandler = logging.FileHandler(debugpath)
            shandler.setLevel(logging.DEBUG)
            self.handler.append(shandler)

        # configure formatter
        if config:
            self.formatter = MDBLogFormatter(config.log.ignore)
        else:
            self.formatter = MDBLogFormatter([])

        for h in self.handler:
            if h:
                h.setFormatter(self.formatter)

        # Add handler
        for h in self.handler:
            if h:
                logging.root.addHandler(h)

        # Show the user where to find the debugging infos
        if debugpath != None and debugpath != "/dev/null":
            logging.debug("logging debugging info in %s", debugpath)
        logging.debug("setting display-loglevel to \033[1;36m%s", loglevelname)

        return


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

