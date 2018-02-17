#!/usr/bin/env bash

if [ $EUID -eq 0 ]; then
    echo -e "\t\e[1;31mYou should not to have root permissions!\e[0m"
    exit 1
fi

if ! type buildozer 2> /dev/null > /dev/null ; then
    echo -e "\e[1;31mThe mandatory tool \e[1;35mbuildozer\e[1;31m is missing!\e[0m"
    exit 1
fi

buildozer android debug deploy run

