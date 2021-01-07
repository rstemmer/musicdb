#!/usr/bin/env bash

set -e

SCRIPTVERSION="2.2.0"
echo -e "\e[1;31mMusicDB-Install [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"


echo -e "\e[1;34mLoading install scripts … \e[1;31m"
source ./install/core.sh
source ./install/mdbdirtree.sh
source ./install/mdbusers.sh
source ./install/ssl.sh
source ./install/mdbconfig.sh
source ./install/database.sh
source ./install/icecast.sh
source ./install/sysenv.sh
source ./install/mdbfiles.sh
source ./install/id3edit.sh


echo -e "\e[1;34mChecking environment … \e[1;31m"
# Check the environment this script is executed in.
# Depending on the Linux distribution some things work different.

# You need to have root permission for the installation process
if [ $EUID -ne 0 ]; then
    echo -e "\t\e[1;31mYou need to have root permissions!\e[0m"
    exit 1
fi

_ExpectingTool sed
_ExpectingTool dialog


# Figure out, how the apache unix group is called
if [ ! -z "$(getent group www-data)" ]; then
    HTTPGROUP="www-data"
elif [ ! -z "$(getent group http)" ]; then
    HTTPGROUP="http"
elif [ ! -z "$(getent group apache)" ]; then
    HTTPGROUP="apache"
elif [ ! -z "$(getent group apache2)" ]; then
    HTTPGROUP="apache2"
else
    echo -e "\t\e[1;31mUnable to figure out how the HTTP unix group is called! \e[1;30m(No HTTP server installed?)\e[0m"
    exit 1
fi

# Check if pwd is the source directory
SOURCEDIR="$(dirname "$(pwd)")"
if [ ! -d "$SOURCEDIR/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the \e[1;37mscripts\e[1;31m directory inside the source directory!"
    echo -e "\t\e[1;30m($SOURCEDIR/.git directory missing)\e[0m"
    exit 1
fi


# Check if there is already an installation that only shall be updated
if [ -f "/etc/musicdb.ini" ] ; then
    echo -e "\t\e[1;37mFound a MusicDB installation to update\e[0m"
    FORMTITLE="MusicDB Update"

    # When there is already an installation, get as much as possible information from it
    DATADIR="$(dirname "$(readlink /etc/musicdb.ini)")"
    SERVERDIR="$(dirname "$(which musicdb)")"
    MUSICDIR="$(sed -nr '/\[music\]/,/\[/{/path/p}'  /etc/musicdb.ini | cut -d "=" -f 2 | tr -d '[:space:]')"
    MDBGROUP="$(sed -nr '/\[music\]/,/\[/{/group/p}' /etc/musicdb.ini | cut -d "=" -f 2 | tr -d '[:space:]')"
    USER="$(    sed -nr '/\[music\]/,/\[/{/owner/p}' /etc/musicdb.ini | cut -d "=" -f 2 | tr -d '[:space:]')" # The music owner, not the MDB user!
    SSLKEY="$(  sed -nr '/\[tls\]/,/\[/{/key/p}'     /etc/musicdb.ini | cut -d "=" -f 2 | tr -d '[:space:]')"
    SSLCRT="$(  sed -nr '/\[tls\]/,/\[/{/cert/p}'    /etc/musicdb.ini | cut -d "=" -f 2 | tr -d '[:space:]')"
    MDBUSER="musicdb"
    WSAPIKEY="$(sed -nr '/\[websocket\]/,/\[/{/apikey/p}' /etc/musicdb.ini | cut -d "=" -f 2 | tr -d '[:space:]')"

    if [ "$SERVERDIR" == "." ] ; then
        echo -e "\t\e[1;33mUnable to find the server directory! \e[1;30m(Server directory must be in \$PATH)"
        SERVERDIR="?"
    fi

    # Check if server is running - this should not be the case while updating
    SERVER_PIDFILE=$(awk -F "=" '/pidfile/ {print $2}' /etc/musicdb.ini)
    if [ -f "$SERVER_PIDFILE" ] ; then
        echo -e "\t\e[1;31mServer still running!\e[1;30m (stop musicdb and mpd before updating)\e[0m"
        exit 1
    fi
else
    FORMTITLE="MusicDB Installation"

    DATADIR="/opt/musicdb/data"
    SERVERDIR="/opt/musicdb/server"
    MUSICDIR="/var/music"
    MDBGROUP="musicdb"
    USER="$(getent passwd 1000 | cut -d ":" -f 1)"    # system user
    SSLKEY="/etc/ssl/musicdb/musicdb.key"
    SSLCRT="/etc/ssl/musicdb/musicdb.cert"
    MDBUSER="musicdb"
    WSAPIKEY="$(openssl rand -base64 32)"
fi


# Check if we are on the master branch. If not, inform the user that he installs indev software
BRANCHNAME="$(git branch | grep \* | cut -d ' ' -f2)"
if [ "$BRANCHNAME" != "master" ] ; then
    FORMTITLE="$FORMTITLE !! from develop branch !!"
fi


echo -e "\e[1;32mdone\e[0m"


FORMFILE=/tmp/form.$$
# dialog --form text height width formheight [ label y x item y x flen ilen ]
dialog --backtitle "$FORMTITLE" --title "Installation Setup" \
    --form "\nCheck and specify the MusicDB environment\n" 18 71 11 \
    "Source directory:"  1 1 "$SOURCEDIR"    1 20 45 0 \
    "Server directory:"  2 1 "$SERVERDIR"    2 20 45 0 \
    "Data directory:"    3 1 "$DATADIR"      3 20 45 0 \
    "Music directory:"   4 1 "$MUSICDIR"     4 20 45 0 \
    "MusicDB group:"     5 1 "$MDBGROUP"     5 20 45 0 \
    "MusicDB user:"      6 1 "$MDBUSER"      6 20 45 0 \
    "Music owner (you):" 7 1 "$USER"         7 20 45 0 \
    "HTTP group:"        8 1 "$HTTPGROUP"    8 20 45 0 \
    "SSL key file:"      9 1 "$SSLKEY"       9 20 45 0 \
    "SSL certificate"   10 1 "$SSLCRT"      10 20 45 0 \
    2> $FORMFILE

# the form file exists anyway, but only when pressed OK it holds the new setting
if [ -s $FORMFILE ] ; then
    SOURCEDIR="$(sed  "1q;d" $FORMFILE)"
    SERVERDIR="$(sed  "2q;d" $FORMFILE)"
    DATADIR="$(  sed  "3q;d" $FORMFILE)"
    MUSICDIR="$( sed  "4q;d" $FORMFILE)"
    MDBGROUP="$( sed  "5q;d" $FORMFILE)"
    MDBUSER="$(  sed  "6q;d" $FORMFILE)"
    USER="$(     sed  "7q;d" $FORMFILE)"
    HTTPGROUP="$(sed  "8q;d" $FORMFILE)"
    SSLKEY="$(   sed  "9q;d" $FORMFILE)"
    SSLCRT="$(   sed "10q;d" $FORMFILE)"
fi

rm $FORMFILE


clear
echo -e "\e[1;31mMusicDB-Install [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"
echo -e "\e[1;37m$FORMTITLE"
echo -e "\t\e[1;34mSource directory: \e[0;36m$SOURCEDIR"
echo -e "\t\e[1;34mServer directory: \e[0;36m$SERVERDIR"
echo -e "\t\e[1;34mData directory:   \e[0;36m$DATADIR"
echo -e "\t\e[1;34mMusic directory:  \e[0;36m$MUSICDIR"
echo -e "\t\e[1;34mMusicDB group:    \e[0;36m$MDBGROUP"
echo -e "\t\e[1;34mMusicDB user:     \e[0;36m$MDBUSER"
echo -e "\t\e[1;34mMusic owner:      \e[0;36m$USER"
echo -e "\t\e[1;34mHTTP group:       \e[0;36m$HTTPGROUP"
echo -e "\t\e[1;34mSSL key file:     \e[0;36m$SSLKEY"
echo -e "\t\e[1;34mSSL certificate:  \e[0;36m$SSLCRT"


SetupUsersAndGroups "$MDBUSER" "$MDBGROUP" "$USER"
CreateMusicDBSSLKeys "$SSLKEY" "$SSLCRT" "$HTTPGROUP"
CreateDirectoryTree "$SOURCEDIR" "$SERVERDIR" "$DATADIR" "$MUSICDIR" "$USER" "$MDBUSER" "$MDBGROUP"
InstallMusicDBConfiguration "$SOURCEDIR" "$SERVERDIR" "$DATADIR" "$MUSICDIR" "$USER" "$MDBUSER" "$MDBGROUP" "$SSLKEY" "$SSLCRT" "$WSAPIKEY"
InstallMusicDBDatabases "$SOURCEDIR" "$DATADIR" "$MDBUSER" "$MDBGROUP"
SetupIcecastEnvironment "$SOURCEDIR" "$DATADIR" "$MDBGROUP" "$SSLCRT"
InstallLogrotateConfiguration "$SOURCEDIR" "$DATADIR" "$MDBUSER" "$MDBGROUP"
InstallShellProfile "$SOURCEDIR" "$SERVERDIR" 
InstallID3Edit
InstallMusicDBFiles "$SOURCEDIR" "$SERVERDIR" "$MDBUSER" "$MDBGROUP" "$WSAPIKEY"

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

