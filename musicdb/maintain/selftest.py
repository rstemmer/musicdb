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

import os
import sys
import grp
import pwd
import logging
from musicdb.lib.filesystem             import Filesystem
from musicdb.maintain.musicdatabase     import MusicDatabaseMaintainer
from musicdb.maintain.trackerdatabase   import TrackerDatabaseMaintainer
from musicdb.maintain.sslcert           import CertificateTools

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
        if user == "musicdb":
            # Usually the music directory should just belong to the MusicDB group.
            # The owner should be the User itself. But as long as MusicDB has R/W access.
            logging.debug("Music directory %s is owned by MusicDB.", path)
        else:
            logging.warning("Music directory %s does not belong to the UNIX group \"musicdb\". MusicDB needs to have permission to manage the music directory", path)

    perm = fs.CheckAccessPermissions(path)
    if perm[0] != "r" or perm[2] != "x":
        logging.critical("Music directory %s is not accessible by MusicDB (No read and execute permissions). MusicDB needs to have permission to access the music directory", path)
        exit(1)
    if perm[1] != "w":
        logging.critical("MusicDB has no write access to the Music directory %s. \033[1;30m(MusicDB execution continues, but some features will not work)", path);
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
    gid   = os.getegid()
    group = grp.getgrgid(gid)
    gname = group.gr_name
    if gname != "musicdb":
        print("\033[1;31mMusicDB runs in UNIX group \033[1;33m%s\033[1;31m but expects group \033[1;32m%s\033[1;33m."%(gname, "musicdb"), file=sys.stderr)
        print("\033[1;30m\tTo change the group, run \033[0;32mnewgrp %s\033[1;30m before executing MusicDB\033[0m"%("musicdb"), file=sys.stderr)
        exit(1)
    return



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

