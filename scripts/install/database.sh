#!/usr/bin/env bash


function InstallMusicDBDatabases {
    local SOURCEDIR="$1"
    local DATADIR="$2"
    local MDBUSER="$3"
    local MDBGROUP="$4"
    local MUSICDB="$DATADIR/music.db"
    local LYCRADB="$DATADIR/lycra.db"
    local TRACKERDB="$DATADIR/tracker.db"

    _ExpectingTool  sqlite3
    _ExpectingUser  $MDBUSER
    _ExpectingGroup $MDBGROUP

    # Install
    ##########

    if [ ! -f "$MUSICDB" ] ; then
        echo -e -n "\e[1;34mCreating databases in \e[0;36m$DATADIR\e[1;34m: \e[1;31m"
        # if the main database is missing, create all new
        sqlite3 $MUSICDB   < $SOURCEDIR/sql/music.db.sql
        sqlite3 $LYCRADB   < $SOURCEDIR/sql/lycra.db.sql
        sqlite3 $TRACKERDB < $SOURCEDIR/sql/tracker.db.sql
        echo -e "\e[1;32mdone"
    fi

    if [ ! -f "$LYCRADB" ] ; then
        echo -e -n "\t\e[1;33mLyCra database missing.\e[1;34m Recreating: \e[1;31m"
        sqlite3 $LYCRADB < $SOURCEDIR/sql/lycra.db.sql
        echo -e "\e[1;32mdone!"
    fi

    if [ ! -f "$TRACKERDB" ] ; then
        echo -e -n "\t\e[1;33mTracker database missing.\e[1;34m Recreating: \e[1;31m"
        sqlite3 $TRACKERDB < $SOURCEDIR/sql/tracker.db.sql
        echo -e "\e[1;32mdone!"
    fi

    # Make sure all permissions are correct
    chmod 664 $DATADIR/*.db
    chown $MDBUSER:$MDBGROUP $DATADIR/*.db
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

