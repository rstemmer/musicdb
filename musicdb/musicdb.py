#!/usr/bin/env python3

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

from musicdb.maintain.musicdatabase   import MusicDatabaseMaintainer
from musicdb.maintain.trackerdatabase import TrackerDatabaseMaintainer
from musicdb.maintain.sslcert         import CertificateTools
from musicdb.maintain.datadirectory   import DataDirectoryMaintainer

VERSION = "8.0.0"

DEFAULTCONFIGFILE = "/etc/musicdb.ini"


def LoadAllModules():
    moddir = os.path.join(os.path.dirname(__file__), "mod")

    # Get a list of all modules (a tuple (name, path))
    fs = Filesystem(moddir)
    modulepaths = fs.GetFiles()
    modulefiles = [(fs.GetFileName(path), path) for path in modulepaths if fs.GetFileExtension(path) == "py"]

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



def AssertDatabases(musicdbpath, trackerdbpath, validate=False):
    logging.info("Checking \033[0;36mDatabases")
    # 2nd argument is the expected version number
    musicdbmaintainer   = MusicDatabaseMaintainer(  musicdbpath,   5)
    trackerdbmaintainer = TrackerDatabaseMaintainer(trackerdbpath, 3)

    # Validate Databases - Create them if they do not exist
    if validate:
        logging.info("Validating database file for \033[0;36m%s", musicdbpath)
        try:
            musicdbmaintainer.Validate()
        except Exception as e:
            logging.exception("Validating database %s failed with error %s!", musicdbpath, str(e))
            exit(1)

        logging.info("Validating database file for \033[0;36m%s", trackerdbpath)
        try:
            trackerdbmaintainer.Validate()
        except Exception as e:
            logging.exception("Validating database %s failed with error %s!", trackerdbpath, str(e))
            exit(1)

    # Make sure the databases exist
    fs = Filesystem()
    if not fs.IsFile(musicdbpath):
        logging.critical("Database %s missing!", musicdbpath)
        logging.critical("\tRun MusicDB at least once via \033[1;37msystemctl start musicdb")
        exit(1)

    if not fs.IsFile(trackerdbpath):
        logging.critical("Database %s missing!", trackerdbpath)
        logging.critical("\tRun MusicDB at least once via \033[1;37msystemctl start musicdb")
        exit(1)

    # Check if Upgrades are required
    logging.info("Checking database version of \033[0;36m%s", musicdbpath)
    if not musicdbmaintainer.CheckVersion():
        logging.warning("%s is too old!\033[1;34m Upgrading …", musicdbpath)
        try:
            musicdbmaintainer.Upgrade()
        except Exception as e:
            logging.exception("Upgrading %s to its latest version failed with error: %s \033[1;30m(Luckily the database has been updated before)", musicdbpath, str(e))
            exit(1)

    logging.info("Checking database version of \033[0;36m%s", trackerdbpath)
    if not trackerdbmaintainer.CheckVersion():
        logging.warning("%s is too old!\033[1;34m Upgrading …", trackerdbpath)
        try:
            trackerdbmaintainer.Upgrade()
        except Exception as e:
            logging.exception("Upgrading %s to its latest version failed with error: %s \033[1;30m(Luckily the database has been updated before)", musicdbpath, str(e))
            exit(1)
    return True


def AssertMusicDirectory(path):
    """
    - Check if directory exists
    - Check if there is R/W access to the music directory (group permission)
    """
    fs = Filesystem("/")
    if not fs.IsDirectory(path):
        logging.critical("Music directory %s does not exist! Update path in configuration or create new music directory.", path)
        exit(1)

    user, group = fs.GetOwner(path)
    if group != "musicdb":
        logging.critical("Music directory %s does not belong to the UNIX group \"musicdb\". MusicDB needs to have permission to manage the music directory")
        exit(1)
    return


def AssertCertificate(keypath, certpath):
    logging.info("Checking \033[0;36mWebSocket TLS Certificates")
    certtool = CertificateTools(keypath, certpath)

    # Check if they exist. Create new if not.
    if not certtool.CheckExistence():
        logging.warning("Certificate (%s or %s) missing! - New certificate will be created …", keypath, certpath)
        if not certtool.Create():
            logging.critical("Creating new certificates failed! \033[1;30m(Read the documentation for creating a certificate manually)")
            print("Creating new certificates failed! \033[1;30m(Read the documentation for creating a certificate manually)", file=sys.stderr)
            exit(1)
        return True

    # Check permissions
    if not certtool.CheckPermissions():
        logging.warning("Invalid permissions detected. Trying to fix them …")
        if not certtool.UpdatePermissions():
            logging.critical("Unable to update the permissions. The current file permissions are not secure! Please update them to \"musicdb:musicdb r--r-----\"")
            print("Unable to update the permissions. The current file permissions are not secure! Please update them to \"musicdb:musicdb r--r-----\"", file=sys.stderr)
            exit(1)
        return True

    return True



def AssertUserID(expecteduser=None):
    """
    Check if MusicDB runs as the right user.
    If expecteduser is a string, the user as which MusicDB was started must be that user.
    Otherwise it is just checked that MusicDB does not run as root.

    If something is not correct, a meaningful error message gets printed to stderr.
    Then the whole application gets exited with exit code 1.

    Returns:
        *Nothing*
    """
    userid   = os.geteuid()
    pwdentry = pwd.getpwuid(userid)
    username = pwdentry.pw_name
    if username == "root":
        print("\033[1;31mMusicDB got executed as \033[1;33mroot\033[1;31m! \033[1;30m(Please run MusicDB as user)", file=sys.stderr)
        exit(1)
    if expecteduser != None and expecteduser != username:
        print("\033[1;31mMusicDB got executed as user \033[1;33m%s\033[1;31m but should have been executed as user \033[1;32m%s\033[1;31m! \033[1;30m(Please run MusicDB as %s)"%(username, expecteduser, expecteduser), file=sys.stderr)
        exit(1)
    return



def AssertGroupID():
    """
    If MusicDB was not executed with the group ``musicdb`` this group will be set as effective group.
    If it fails, MusicDB gets exit with error code 1 and a meaningful error message

    Returns:
        *Nothing*
    """
    logging.debug("Checking if effective group is musicdb")
    gid   = os.getegid()
    group = grp.getgrgid(gid)
    gname = group.gr_name
    if gname != "musicdb":
        print("\033[1;31mMusicDB runs in UNIX group \033[1;33m%s\033[1;31m but expects group \033[1;32m%s\033[1;33m."%(gname, "musicdb"), file=sys.stderr)
        print("\033[1;30m\tTo change the group, run \033[0;32mnewgrp %s\033[1;30m before executing MusicDB\033[0m"%("musicdb"), file=sys.stderr)
        exit(1)
    return



def main():
    print("\033[1;31mMusicDB [\033[1;34m" + VERSION + "\033[1;31m]\033[0m")

    AssertUserID()

    # Generate argument parser
    argparser = argparse.ArgumentParser(description="Universal MusicDB command line tool")
    argparser.add_argument("-v", "--version", action="store_true", help="show version and exit")
    argparser.add_argument("-q", "--quiet",   action="store_true", help="be quiet - do not write into debug file")
    argparser.add_argument(      "--verbose", action="store_true", help="be verbose - write into log file (usually stdout)")
    argparser.add_argument("--config"       # allows using nondefault config file
        , action="store"
        , type=str
        , metavar="path"
        , default=DEFAULTCONFIGFILE
        , help="Path to a nondefault config file. This will also influence the database file.")
    argparser.add_argument("--logfile"
        , action="store"
        , type=str
        , metavar="dest"
        , help="Override log-setting. dest can be a path to a file or \"stdout\" or \"stderr\".")
    argparser.add_argument("--loglevel"
        , action="store"
        , choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        , type=str
        , metavar="level"
        , help="Override log-setting for the loglevel that shall be logged.")

    parserset = argparser.add_subparsers(title="Modules", metavar="module", help="module help")

    log = MusicDBLogger()   # The MusicDBConfig moduel needs a set up logger. The setting for logging will be applied later on.


    # Get all modules and extend the argument parser
    print("\033[1;34mLoading modules …\033[0m")
    modules = LoadAllModules()

    print("\033[1;34mInitializing …\033[0m")
    for modulename in modules:
        modclass = getattr(modules[modulename], modulename)
        modclass.MDBM_CreateArgumentParser(parserset, modulename)

    args = argparser.parse_args()

    if args.version:
        # was already printed
        exit(0)

    fs = Filesystem("/")


    # open the configuration file
    args.config = os.path.abspath(args.config)
    if not fs.IsFile(args.config):
        print("\033[1;31mFATAL ERROR: Config-file does not exist!\033[0m (" + args.config + ")")
        exit(1)

    try:
        config = MusicDBConfig(args.config)
    except Exception as e:
        print("\033[1;31mFATAL ERROR: Opening config-file failed!\033[0m (" + args.config + ")")
        print(e)
        exit(1)


    # reconfigure logger
    if args.quiet:
        debugfile = None
    else:
        debugfile = config.log.debugfile

    if args.logfile:
        args.logfile= os.path.abspath(args.logfile)
        logfile = args.logfile
    elif args.verbose:
        logfile = config.log.logfile
    else:
        logfile = None
        
    if args.loglevel:
        loglevel = args.loglevel
    else:
        loglevel = config.log.loglevel
    log.Reconfigure(logfile, loglevel, debugfile, config)


    # Get module name that shall be executed
    try:
        modulename = args.module
    except:
        argparser.print_help()
        exit(1)


    # Check for effective group and print a warning when it is not MusicDB
    AssertGroupID()
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
        print("\033[1;31mFATAL ERROR: Opening database failed!\033[0m (" + databasepath + ")")
        print(e)
        exit(1)


    # execute module
    modclass = getattr(modules[modulename], modulename)
    modobj   = modclass(config, database)
    exitcode = modobj.MDBM_Main(args)
    exit(exitcode)



if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

