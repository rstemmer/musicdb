#!/usr/bin/env bash

echo -e "\033[1;31mMusicDB-Boot [\033[1;34m1.0.1\033[1;31m]\033[0m"

if [ $EUID -ne 0 ] ; then
    echo -e "\e[1;31mYou need to have root permissions!\e[0m"
    exit 1
fi


# Determin configuration directory
CONFIGDIR="$(dirname "$(readlink /etc/musicdb.ini)")"


# Define some settings
CONFIG_MPD="$CONFIGDIR/mpd/mpd.conf"
CONFIG_ICECAST="$CONFIGDIR/icecast/config.xml"


# Define the binaries to execute
if type "mpd" 2> /dev/null > /dev/null ; then
    MPD=mpd
else
    echo -e "\e[1;31mCannot find \e[1;36mMPD\e[1;31m!\e[0m"
    exit 1
fi

if type "icecast" 2> /dev/null > /dev/null ; then
    ICECAST=icecast
elif type "icecast2" 2> /dev/null > /dev/null ; then
    ICECAST=icecast2
fi


# Inform user about configurations used
echo -e "\e[1;34mMPD-Config:     \e[1;36m$CONFIG_MPD\e[0m"
if [ ! -z "$ICECAST" ] ; then
    echo -e "\e[1;34mIcecast-Config: \e[1;36m$CONFIG_ICECAST\e[0m"
fi


# start mpd
echo -e -n "\e[1;34mStarting MPD \e[0m"
$MPD --kill > /dev/null 2>&1
$MPD $CONFIG_MPD
if [ $? -ne 0 ] ; then
    echo -e "\e[1;31mfailed!\e[0m"
    exit 3
fi
echo -e "\e[1;32mdone\e[0m"


# start icecast if it is installed
if [ ! -z "$ICECAST" ] ; then
    echo -e -n "\e[1;34mStart icecast \e[0m"
    killall $ICECAST > /dev/null 2>&1
    $ICECAST -b -c $CONFIG_ICECAST > /dev/null
    if [ $? -ne 0 ] ; then
        echo -e "\e[1;31mfailed!\e[0m"
        exit 4
    fi
    echo -e "\e[1;32mdone\e[0m"
fi


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

