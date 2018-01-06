#!/usr/bin/env bash

echo -e "\033[1;31mMusicDB-Start [\033[1;34m1.0.0\033[1;31m]\033[0m"

if [ $EUID -ne 0 ] ; then
    echo -e "\e[1;31mYou need to have root permissions!\e[0m"
    exit 1
fi


# Read configuration
SERVER_PIDFILE=$(awk -F "=" '/pidfile/ {print $2}' /etc/musicdb.ini)
MDBUSER="musicdb"


# check if the PID file exists. If yes, the server is already running.
if [ -f "$SERVER_PIDFILE" ] ; then
    echo -e "\e[1;31mServer already running!\e[0m"
    exit 1
fi


# start musicdb
echo -e "\e[1;37mStarting MusicDB WebSocket Server\e[0m"
su -l -c "musicdb --verbose server" $MDBUSER

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

