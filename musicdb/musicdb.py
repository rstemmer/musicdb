#!/usr/bin/env python3

# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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

import argparse
import importlib.util
import os
import sys
import grp
import pwd
import logging
import traceback
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.logging        import MusicDBLogger

from musicdb.maintain.datadirectory   import DataDirectoryMaintainer

from musicdb.maintain.selftest  import AssertDatabases, AssertMusicDirectory, AssertCertificate, AssertUserID, AssertGroupID

VERSION = "8.1.0"

DEFAULTCONFIGFILE = "/etc/musicdb.ini"


def LoadAllModules():
    moddir = os.path.join(os.path.dirname(__file__), "mod")

    # Get a list of all modules (a tuple (name, path))
    fs = Filesystem(moddir)
    modulepaths = fs.GetFiles() # Get all files in the module path
    modulepaths = [path for path in modulepaths if fs.GetFileExtension(path) == "py"]          # Only consider Python files
    modulefiles = [(str(fs.GetFileName(path)), fs.AbsolutePath(path)) for path in modulepaths] # Identify modules

    # Load all modules
    modules = {}
    for modulename, modulepath in modulefiles:
        if modulename == "__init__":
            continue

        try:
            spec = importlib.util.spec_from_file_location(modulename, modulepath)
        except Exception as e:
            print("\033[1;33mWARNING: Loading spec for module \033[0;33m%s\033[1;33m failed with following error: \033[0;33m%s\033[1;30m (Module will not be loaded)\033[0m"%(modulename, str(e)))
            print(traceback.format_exc())
            continue

        try:
            module = importlib.util.module_from_spec(spec)
        except Exception as e:
            print("\033[1;33mWARNING: Importing module \033[0;33m%s\033[1;33m failed with following error: \033[0;33m%s\033[1;30m (Module will not be loaded)\033[0m"%(modulename, str(e)))
            print(traceback.format_exc())
            continue

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print("\033[1;33mWARNING: Initial execution of module \033[0;33m%s\033[1;33m failed with following error: \033[0;33m%s\033[1;30m (Module will not be loaded)\033[0m"%(modulename, str(e)))
            print(traceback.format_exc())
            continue

        modules[modulename] = module

    # Return a list of loaded python modules
    return modules



def main():
    print("\033[1;31mMusicDB [\033[1;34m" + VERSION + "\033[1;31m]\033[0m", file=sys.stderr)

    # Check for effective group and user. Print an error and exit when it is not as expected
    AssertUserID()
    AssertGroupID()

    # Generate argument parser
    argparser = argparse.ArgumentParser(description="MusicDB command line interface")
    argparser.add_argument("-v", "--version", action="store_true", help="show version and exit")
    argparser.add_argument("--config"       # allows using non-default configuration files
        , action="store"
        , type=str
        , metavar="path"
        , default=DEFAULTCONFIGFILE
        , help="Path to a nondefault config file. This will also influence the database file.")

    parserset = argparser.add_subparsers(title="Modules", metavar="module", help="module help")

    log = MusicDBLogger()   # The MusicDBConfig module needs a set up logger. The setting for logging will be applied later on.


    # Get all modules and extend the argument parser
    modules = LoadAllModules()
    for modulename in modules:
        modclass = getattr(modules[modulename], modulename)
        modclass.MDBM_CreateArgumentParser(parserset, modulename)

    # Parse command line arguments
    args = argparser.parse_args()

    if args.version:
        # was already printed
        exit(0)

    # open the configuration file
    fs = Filesystem("/")
    configpath = fs.AbsolutePath(args.config)
    if not fs.IsFile(configpath):
        print("\033[1;31mFATAL ERROR: Configuration file does not exist!\033[0m (" + args.config + ")", file=sys.stderr)
        exit(1)
    configpath = fs.ToString(configpath)

    try:
        config = MusicDBConfig(args.config)
    except Exception as e:
        print("\033[1;31mFATAL ERROR: Opening configuration file failed!\033[0m (" + args.config + ")", file=sys.stderr)
        print(traceback.format_exc())
        exit(1)


    # reconfigure logger
    debugfile = config.log.debugfile
    logfile   = config.log.logfile
    loglevel  = config.log.loglevel
    try:
        log.Reconfigure(logfile, loglevel, debugfile, config)
    except Exception as e:
        print("\033[1;31mFATAL ERROR: Opening debug log file failed!\033[0m (" + debugfile + ")", file=sys.stderr)
        print(traceback.format_exc())
        exit(1)
    logging.info("\033[1;31mMusicDB [\033[1;34m" + VERSION + "\033[1;31m]\033[0m")


    # Get module name that shall be executed
    try:
        modulename = args.module
    except:
        argparser.print_help()
        exit(1)


    # Check if everything is as expected with the music directory
    AssertMusicDirectory(config.directories.music)


    # get, check and open the database from path
    databasepath = config.files.musicdatabase


    # The server requires a bit more attention if everything is secure
    # If something is wrong, MusicDB exits with error code 1
    datadirmaintainer = DataDirectoryMaintainer(config)
    if modulename == "server":
        AssertUserID("musicdb") # only musicdb is allowed to run the websocket server
        datadirmaintainer.Validate()
        AssertCertificate(config.websocket.key, config.websocket.cert)
        AssertDatabases(databasepath, config.files.trackerdatabase, validate=True)
    else:
        success = datadirmaintainer.Check()
        if not success:
            logging.critical("Data directory structure invalid!")
            logging.critical("\tRun MusicDB at least once via \033[1;37msystemctl start musicdb")
            exit(1)
        AssertDatabases(databasepath, config.files.trackerdatabase, validate=False)


    try:
        database = MusicDatabase(databasepath)
    except Exception as e:
        logging.exception("Opening database (%s) failed!", databasepath)
        exit(1)


    # execute module
    modclass = getattr(modules[modulename], modulename)
    modobj   = modclass(config, database)
    exitcode = modobj.MDBM_Main(args)
    exit(exitcode)



if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

