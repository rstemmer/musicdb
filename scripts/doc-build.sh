#!/usr/bin/env bash

# TODO: Read Version
pkgname="musicdb-8.0.0-doc"

set -e
SCRIPTVERSION="1.0.0"
echo -e "\e[1;31mMusicDB Document Package Builder Script [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"

repository="$(dirname "$(pwd)")"
if [ ! -d "$repository/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the \e[1;37mscripts\e[1;31m directory inside the MusicDB repository!"
    echo -e "\t\e[1;30m($repository/.git directory missing)\e[0m"
    exit 1
fi


mkdir -p "$repository/dist"

tmp="/tmp/${pkgname}"
mkdir -p "$tmp/musicdb"

oldwd=$(pwd)
cd $repository/docs/

echo -e "\e[1;35m - \e[1;34mCompiling Documentation…"
make html BUILDDIR=$tmp 2>&1

echo -e "\e[1;35m - \e[1;34mCreating Source Archive…"
mv ${tmp}/html ${tmp}/${pkgname}
tar -c --zstd -C ${tmp} -f ${repository}/dist/${pkgname}.tar.zst $pkgname

rm -r "$tmp"
echo -e "\e[1;32mdone"

cd $oldwd
