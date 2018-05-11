#!/usr/bin/env bash


function SetupMusicDBDatabases {
    local SOURCEDIR="$1"
    local DATADIR="$2"
    local MUSICDB="$DATADIR/music.db"

    _ExpectingTool sqlite3

    # Install
    ##########

    if [ ! -f "$DATADIR/music.db" ] ; then
        echo -e -n "\e[1;34mCreate databases in \e[0;36m$DATADIR\e[1;34m: \e[1;31m"
        # if the main database is missing, create all new
        sqlite3 $DATADIR/music.db   < $SOURCEDIR/sql/music.db.sql
        sqlite3 $DATADIR/lycra.db   < $SOURCEDIR/sql/lycra.db.sql
        sqlite3 $DATADIR/tracker.db < $SOURCEDIR/sql/tracker.db.sql
        echo -e "\e[1;32mdone"
    fi

    if [ ! -f "$DATADIR/lycra.db" ] ; then
        echo -e -n "\t\e[1;33mLyCra database missing.\e[1;34m Recreating: \e[1;31m"
        sqlite3 $DATADIR/lycra.db   < $SOURCEDIR/sql/lycra.db.sql
        echo -e "\e[1;32mdone!"
    fi

    if [ ! -f "$DATADIR/tracker.db" ] ; then
        echo -e -n "\t\e[1;33mTracker database missing.\e[1;34m Recreating: \e[1;31m"
        sqlite3 $DATADIR/tracker.db < $SOURCEDIR/sql/tracker.db.sql
        echo -e "\e[1;32mdone!"
    fi

    # Make sure all permissions are correct
    chmod 664 $DATADIR/*.db
    chown $MDBUSER:$MDBGROUP $DATADIR/*.db

    # Update
    #########

    echo -e "\e[1;34mChecking databases for updates:\e[1;31m"
    # !! Order matters !!

    # checksum column
    sqlite3 "$MUSICDB" "PRAGMA table_info(\"songs\");" | grep "checksum" > /dev/null
    if [ $? -ne 0 ]; then
        echo -e -n "\t\e[1;32m + \e[1;34mAdding \e[0;36mchecksum\e[1;34m column: \e[0m"
        sqlite3 "$MUSICDB" 'ALTER TABLE songs ADD COLUMN checksum TEXT DEFAULT "";'
        if [ $? -eq 0 ]; then
            echo -e "\e[1;32mdone"
        else
            echo -e "\e[1;31mfailed! Database is broken!\e[0m"
        fi
    fi

    # lastplayed column
    sqlite3 "$MUSICDB" "PRAGMA table_info(\"songs\");" | grep "lastplayed" > /dev/null
    if [ $? -ne 0 ]; then
        echo -e -n "\t\e[1;32m + \e[1;34mAdding \e[0;36mlastplayed\e[1;34m column: \e[0m"
        sqlite3 "$MUSICDB" 'ALTER TABLE songs ADD COLUMN lastplayed INTEGER DEFAULT 0;'
        if [ $? -eq 0 ]; then
            echo -e "\e[1;32mdone"
        else
            echo -e "\e[1;31mfailed! Database is broken!\e[0m"
        fi
    fi
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

