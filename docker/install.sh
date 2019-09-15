#!/usr/bin/env bash

SCRIPTVERSION="1.0.0"
set -e

SOURCEDIR="/src"
DATADIR="/opt/musicdb/data"
SERVERDIR="/opt/musicdb/server"
MUSICDIR="/var/music"
MDBGROUP="musicdb"
USER="user"
SSLKEY="/etc/ssl/musicdb/musicdb.key"
SSLCRT="/etc/ssl/musicdb/musicdb.cert"
MDBUSER="musicdb"

echo -e "\e[1;31mMusicDB-Image-Install [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"


echo -e "\e[1;34mLoading install scripts … \e[1;31m"
source $SOURCEDIR/scripts/install/core.sh
source $SOURCEDIR/scripts/install/mdbdirtree.sh
source $SOURCEDIR/scripts/install/mdbusers.sh
source $SOURCEDIR/scripts/install/ssl.sh
source $SOURCEDIR/scripts/install/mdbconfig.sh
source $SOURCEDIR/scripts/install/database.sh
source $SOURCEDIR/scripts/install/icecast.sh
source $SOURCEDIR/scripts/install/sysenv.sh
source $SOURCEDIR/scripts/install/mdbfiles.sh
source $SOURCEDIR/scripts/install/id3edit.sh


echo -e "\e[1;34mChecking environment … \e[1;31m"
# Check the environment this script is executed in.
# Depending on the Linux distribution some things work different.

# You need to have root permission for the installation process
if [ $EUID -ne 0 ]; then
    echo -e "\t\e[1;31mYou need to have root permissions!\e[0m"
    exit 1
fi

_ExpectingTool sed


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


echo -e "\e[1;32mdone\e[0m"

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
CreateMusicDBSSLKeys "$SSLKEY" "$SSLCRT" "$HTTPGROUP" << EOF
XX
Docker-County
Docker-City
NoOrg
Section 9
localhost
no@mail.xx
password
password
EOF
CreateDirectoryTree "$SOURCEDIR" "$SERVERDIR" "$DATADIR" "$MUSICDIR" "$USER" "$MDBUSER" "$MDBGROUP"
InstallMusicDBConfiguration "$SOURCEDIR" "$SERVERDIR" "$DATADIR" "$MUSICDIR" "$USER" "$MDBUSER" "$MDBGROUP" "$SSLKEY" "$SSLCRT"
InstallMusicDBDatabases "$SOURCEDIR" "$DATADIR" "$MDBUSER" "$MDBGROUP"
SetupIcecastEnvironment "$SOURCEDIR" "$DATADIR" "$MDBGROUP" "$SSLCRT"
#InstallLogrotateConfiguration "$SOURCEDIR" "$DATADIR" "$MDBUSER" "$MDBGROUP"
InstallShellProfile "$SOURCEDIR" "$SERVERDIR" 
#InstallID3Edit
InstallMusicDBFiles "$SOURCEDIR" "$SERVERDIR" "$MDBUSER" "$MDBGROUP"

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

