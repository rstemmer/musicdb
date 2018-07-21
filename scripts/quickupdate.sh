#!/usr/bin/env bash

set -e

SCRIPTVERSION="2.0.0"
echo -e "\e[1;31mMusicDB-QuickUpdate [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"

source ./install/core.sh
source ./install/mdbfiles.sh



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

SOURCEDIR="$(dirname "$(pwd)")"
if [ ! -d "$SOURCEDIR/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the \e[1;37mscripts\e[1;31m directory inside the source directory!"
    echo -e "\t\e[1;30m($SOURCEDIR/.git directory missing)\e[0m"
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



InstallMusicDBFiles "$SOURCEDIR" "$SERVERDIR" "$MDBUSER" "$MDBGROUP"

# Last step: upgrading internal files
su -l -c "musicdb upgrade" $MDBUSER


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

