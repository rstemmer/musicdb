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
This library provides the excessive logging system of MusicDB.
"""

import logging
import sys
import os
import stat

class MBDLogFormatter(logging.Formatter):
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
            self._style._fmt = MBDLogFormatter.debug_format
        elif record.levelno == logging.INFO:
            self._style._fmt = MBDLogFormatter.info_format
        elif record.levelno == logging.WARNING:
            self._style._fmt = MBDLogFormatter.warning_format
        elif record.levelno == logging.ERROR:
            self._style._fmt = MBDLogFormatter.error_format
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = MBDLogFormatter.critical_format

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


class MusicDBLogger():
    """
    This class provides the logging management itself and handles the logging configuration.

    Args:
        path (str): A "path" where the logs will be written. Use ``"stdout"`` or ``"stderr"`` to show them on the screen.
        loglevelname (str): Name of the lowest log level that shall be shown: ``"DEBUG"``, ``"INFO"``, ``"WARNING"``, ``"ERROR"`` or ``"CRITICAL"``.
        debugpath (str): Path to a file where everything (DEBUG) shall be logged in. ``None`` for not such a file.
        config: A MusicDB Configuration object that hold the ignore list. If ``None`` the configuration will not be appied.
    """
    def __init__(self, logpath="stderr", loglevelname="INFO", debugpath=None, config=None):
        # configure loglevel
        loglevelname = loglevelname.upper()
        loglevelmap = {}
        loglevelmap["DEBUG"]    = logging.DEBUG
        loglevelmap["INFO"]     = logging.INFO
        loglevelmap["WARNING"]  = logging.WARNING
        loglevelmap["ERROR"]    = logging.ERROR
        loglevelmap["CRITICAL"] = logging.CRITICAL
        loglevel = loglevelmap[loglevelname]

        # create output handler
        self.handler = []   # list of handler, at least one: stderr. maybe a file for more details

        # primary handler
        if logpath == "stdout":
            phandler = logging.StreamHandler(sys.stdout)
        elif logpath == "stderr":
            phandler = logging.StreamHandler(sys.stderr)
        else:
            phandler = logging.FileHandler(logpath)

        phandler.setLevel(loglevel)
        self.handler.append(phandler)


        # secondary handler
        if debugpath:
            shandler = logging.FileHandler(debugpath)
            shandler.setLevel(logging.DEBUG)
            self.handler.append(shandler)


        # configure formatter
        if config:
            self.formatter = MBDLogFormatter(config.log.ignore)
        else:
            self.formatter = MBDLogFormatter([])

        for h in self.handler:
            h.setFormatter(self.formatter)


        # Add handler
        for h in self.handler:
            logging.root.addHandler(h)


        # Show the user where to find the debugging infos
        if debugpath:
            logging.debug("logging debugging info in %s", debugpath)
        logging.debug("setting display-loglevel to \033[1;36m%s", loglevelname)



    def SetFilePermissions(self, path):
        try:
            with open(path, 'a'):
                pass

            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH) # 664
        except PermissionError:
            return False
        return True



    def Reconfigure(self, logpath="stderr", loglevelname="DEBUG", debugpath=None, config=None):
        logging.debug("Reconfiguring logging behaviour")
        # configure loglevel
        loglevelname = loglevelname.upper()
        loglevelmap = {}
        loglevelmap["DEBUG"]    = logging.DEBUG
        loglevelmap["INFO"]     = logging.INFO
        loglevelmap["WARNING"]  = logging.WARNING
        loglevelmap["ERROR"]    = logging.ERROR
        loglevelmap["CRITICAL"] = logging.CRITICAL
        loglevel = loglevelmap[loglevelname]

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
            else:
                phandler = logging.FileHandler(logpath)
                self.SetFilePermissions(logpath) # Set file permission to rw-rw-r-- !

            phandler.setLevel(loglevel)
            self.handler.append(phandler)

        # secondary handler
        if debugpath != None and debugpath != "/dev/null":
            shandler = logging.FileHandler(debugpath)
            self.SetFilePermissions(debugpath)
            shandler.setLevel(logging.DEBUG)
            self.handler.append(shandler)


        # configure formatter
        if config:
            self.formatter = MBDLogFormatter(config.log.ignore)
        else:
            self.formatter = MBDLogFormatter([])

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

        return self


    def GetLogger(self, name):
        logger = logging.getLogger(name)
        return logger


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

