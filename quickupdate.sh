#!/usr/bin/env bash

set -e

SCRIPTVERSION="1.0.0"
echo -e "\e[1;31mMusicDB-QuickUpdate [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"

function UpdateMusicDBFiles {
    echo -e -n "\e[1;34mUpdating MusicDB files to \e[0;36m$SERVERDIR\e[1;34m: "

    WSCLIENTFILE=$SERVERDIR/webui/js/musicdb.js
    if [ -f "$WSCLIENTFILE" ] ; then
        # this is an update, so save the websocket and watchdog configuration before overwriting this file
        WATCHDOG_RUN="$(     grep "var.WATCHDOG_RUN"      $WSCLIENTFILE)"
        WATCHDOG_INTERVAL="$(grep "var.WATCHDOG_INTERVAL" $WSCLIENTFILE)"
        WEBSOCKET_URL="$(    grep "var.WEBSOCKET_URL"     $WSCLIENTFILE)"
    fi

    rsync -uav  \
        --exclude 'tmp/' \
        --exclude 'id3edit/' \
        --exclude 'lib/crawler/' \
        --exclude 'docs/build/doctrees/' \
        --exclude '.git/' \
        --exclude '.gitignore' \
        --exclude '*.swp' \
        --exclude '*.swo' \
        --exclude '*.pyc' \
        --exclude '*~' \
        --delete \
        $SOURCEDIR/ $SERVERDIR/. > /dev/null

    chown -R $MDBUSER:$MDBGROUP $SERVERDIR

    # on update, reset the settings from the old version of the musicdb.js file
    if [ ! -z "$WATCHDOG_RUN" ] ; then
        sed -i -e "s\\var.WATCHDOG_RUN.*\\$WATCHDOG_RUN\\g"           $WSCLIENTFILE
        sed -i -e "s\\var.WATCHDOG_INTERVAL.*\\$WATCHDOG_INTERVAL\\g" $WSCLIENTFILE
        sed -i -e "s\\var.WEBSOCKET_URL.*\\$WEBSOCKET_URL\\g"         $WSCLIENTFILE
    fi

    echo -e "\e[1;32mdone\e[0m"
}



if [ $EUID -ne 0 ]; then
    echo -e "\t\e[1;31mYou need to have root permissions!\e[0m"
    exit 1
fi

if ! type sed 2> /dev/null > /dev/null ; then
    echo -e "\e[1;31mThe mandatory tool \e[1;35msed\e[1;31m is missing!\e[0m"
    exit 1
fi

if [ ! -f "/etc/musicdb.ini" ] ; then
    echo -e "\e[1;31mNo MusicDB installation found!\e[0m"
    exit 1
fi



SERVERDIR="$(dirname "$(which musicdb)")"
MDBGROUP="$(sed -nr '/\[music\]/,/\[/{/group/p}' /etc/musicdb.ini | cut -d "=" -f 2)"
MDBUSER="musicdb"

SOURCEDIR="$(pwd)"
if [ ! -d "$SOURCEDIR/.git" ] ; then
    echo -e "\e[1;31mThe script must be executed from the source directory! \e[1;30m($SOURCEDIR/.git directory missing)\e[0m"
    exit 1
fi


echo -e "\t\e[1;34mSource directory: \e[0;36m$SOURCEDIR"
echo -e "\t\e[1;34mServer directory: \e[0;36m$SERVERDIR"
echo -e "\t\e[1;34mMusicDB group:    \e[0;36m$MDBGROUP"
echo -e "\t\e[1;34mMusicDB user:     \e[0;36m$MDBUSER"

if [ "$SERVERDIR" == "." ] ; then
    echo -e "\e[1;33mUnable to find the server directory! \e[1;30m(Server directory must be in \$PATH)"
    exit 1
fi



UpdateMusicDBFiles 


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

