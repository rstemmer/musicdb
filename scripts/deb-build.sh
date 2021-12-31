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

# Prepare build directory
builddir="${HOME}/debbuild/musicdb"
version="8.0.0"
echo -e "\e[1;34mCreating build directory \e[0;36m${builddir} \e[1;34m…"
rm -rf ${builddir}
mkdir -p ${builddir}
cd ${builddir}

# Prepare sources
sourcename="musicdb-${version}-src"
echo -e "\e[1;34mPreparing source files …"
cp ${repository}/dist/musicdb-${version}-src.tar.zst .
unzstd ${sourcename}.tar.zst
gzip   ${sourcename}.tar
mv ${sourcename}.tar.gz musicdb-${version}.tar.gz
ln -s musicdb-${version}.tar.gz musicdb_${version}.orig.tar.gz

echo -e "\e[1;34mExtracting source files …"
tar xf musicdb-${version}.tar.gz
mv ${sourcename} musicdb-${version}

# Prepare deb build environment
echo -e "\e[1;34mPreparing deb build environment …"
cd musicdb-${version}
cp -r ${repository}/debian .
cp    ${repository}/share/musicdb.service ./debian/musicdb.service
cp    ${repository}/share/tmpfiles.conf   ./debian/musicdb.tmpfile

# Build deb package
echo -e "\e[1;34mBuilding deb package …\e[0m"
debuild -uc -us --lintian-opts --profile debian
# -uc -us: Do not sign source and changes
# --profile debian: See: https://bugs.launchpad.net/ubuntu/+source/lintian/+bug/1303603

cp ${builddir}/musicdb*.deb ${repository}/dist/.
echo -e "\e[1;32mdone"

cd $oldwd

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

