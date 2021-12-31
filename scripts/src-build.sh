#!/usr/bin/env bash

# TODO: Read Version
pkgname="musicdb-8.0.0-src"

set -e
SCRIPTVERSION="1.0.0"
echo -e "\e[1;31mMusicDB Source Package Builder Script [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"

repository="$(dirname "$(pwd)")"
if [ ! -d "$repository/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the \e[1;37mscripts\e[1;31m directory inside the MusicDB repository!"
    echo -e "\t\e[1;30m($repository/.git directory missing)\e[0m"
    exit 1
fi


mkdir -p "$repository/dist"

oldwd=$(pwd)
cd $repository
echo -e "\e[1;35m - \e[1;34mCreating Source Archive…"

tmp="/tmp/${pkgname}"
mkdir -p $tmp

cp -r musicdb           $tmp
cp -r webui             $tmp
cp -r share             $tmp
cp -r sql               $tmp
cp    README.md         $tmp
cp    LICENSE           $tmp
cp    VERSION           $tmp
cp    CHANGELOG         $tmp
cp    setup.py          $tmp
cp    pyproject.toml    $tmp

tar -c --zstd --exclude="__pycache__" --exclude='*.bak' -C ${tmp}/.. -f dist/${pkgname}.tar.zst $pkgname

rm -r $tmp
echo -e "\e[1;32mdone"

cd $oldwd

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

