#!/usr/bin/env bash

set -e
SCRIPTVERSION="1.0.0"
echo -e "\e[1;31mMusicDB RPM Builder Script [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"

repository="$(dirname "$(pwd)")"
if [ ! -d "$repository/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the \e[1;37mscripts\e[1;31m directory inside the MusicDB repository!"
    echo -e "\t\e[1;30m($repository/.git directory missing)\e[0m"
    exit 1
fi

oldwd=$(pwd)
cd $repository/dist

cp ../pkg/*src.tar.zst ~/rpmbuild/SOURCES/.
cp ../share/sysusers.conf ~/rpmbuild/SOURCES/musicdb.sysusers
rpmbuild -bb musicdb.spec
cp ~/rpmbuild/RPMS/noarch/musicdb* ../pkg/.

echo -e "\e[1;32mdone"

cd $oldwd

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

