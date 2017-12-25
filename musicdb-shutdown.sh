#!/usr/bin/env bash

echo -e "\033[1;31mMusicDB-Shutdown [\033[1;34m1.0.0\033[1;31m]\033[0m"

if [ $EUID -ne 0 ] ; then
    echo "\e[1;31mYou need to have root permissions!\e[0m"
    exit 1
fi


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


# stop mpd
echo -e -n "\e[1;34mStop MPD \e[0m"
$MPD --kill > /dev/null 2>&1
echo -e "\e[1;32mdone\e[0m"


# stop icecast if it exists
if [ ! -z "$ICECAST" ] ; then
    echo -e -n "\e[1;34mStop icecast \e[0m"
    killall $ICECAST > /dev/null 2>&1
    echo -e "\e[1;32mdone\e[0m"
fi

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

