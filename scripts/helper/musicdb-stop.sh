#!/usr/bin/env bash

echo -e "\033[1;31mMusicDB-Stop [\033[1;34m1.0.1\033[1;31m]\033[0m"

if [ $EUID -ne 0 ] ; then
    echo -e "\e[1;31mYou need to have root permissions!\e[0m"
    exit 1
fi


SERVER_PIPE=$(awk -F "=" '/fifofile/ {print $2}' /etc/musicdb.ini  | tr -d '[:space:]')
if [ ! -p "$SERVER_PIPE" ] ; then
    echo -e "\e[1;31mCannot find \e[1;36m$SERVER_PIPE\e[1;31m! \e[0;31m(Server not running?)\e[0m"
    exit 1
fi

# stop musicdb
echo "shutdown" > $SERVER_PIPE
echo -e "\e[1;34mMusicDB server shutdown initiated\e[0m"


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

