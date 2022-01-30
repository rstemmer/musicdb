#!/usr/bin/env bash


set -e
SCRIPTVERSION="2.0.0"
echo -e "\e[1;31mMusicDB Package Builder Script [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"

repository="$(dirname "$(pwd)")"
if [ ! -d "$repository/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the \e[1;37mscripts\e[1;31m directory inside the MusicDB repository!"
    echo -e "\t\e[1;30m($repository/.git directory missing)\e[0m"
    exit 1
fi

VersionFile="../VERSION"
version=$(grep MusicDB $VersionFile | cut -d ":" -f 2 | tr -d " ")

mkdir -p "$repository/pkg"



function PrintHelp {
    echo "./build.sh [--help] [src] [pkg] [rpm] [deb] [doc]"
}



function BuildSource {
    pkgname="musicdb-${version}-src"
    oldwd=$(pwd)
    cd $repository
    echo -e "\e[1;35m - \e[1;34mCreating Source Archive…"

    tmp="/tmp/${pkgname}"
    mkdir -p $tmp
    rm -f "../pkg/${pkgname}.tar.zst"

    cp -r musicdb              $tmp
    cp -r webui                $tmp
    cp -r share                $tmp
    cp -r sql                  $tmp
    cp    README.md            $tmp
    cp    LICENSE              $tmp
    cp    VERSION              $tmp
    cp    CHANGELOG            $tmp
    cp    dist/setup.py        $tmp
    cp    dist/pyproject.toml  $tmp

    tar -c --zstd --exclude='*.bak' --exclude="share/musicdb.ini.7.x.x" --exclude="__pycache__" -C "${tmp}/.." -f "pkg/${pkgname}.tar.zst" "$pkgname"

    rm -r "$tmp"
    echo -e "\e[1;32mdone"

    cd $oldwd
}



function BuildPKG {
    oldwd=$(pwd)
    cd $repository/dist

    tmp=/tmp/mkpkg
    if [[ -d $tmp ]] ; then
        rm -r $tmp
    fi
    rm -f "../pkg/musicdb-${version}-1-any.pkg.tar.zst"

    SRCDEST=$tmp BUILDDIR=$tmp PKGDEST=../pkg makepkg
    rm -r $tmp

    echo -e "\e[1;32mdone"

    cd $oldwd
}



function BuildRPM {
    oldwd=$(pwd)
    cd $repository/dist

    rm -f "../pkg/musicdb-${version}-1.fc35.noarch.rpm"
    cp ../pkg/*src.tar.zst ~/rpmbuild/SOURCES/.
    cp ../share/sysusers.conf ~/rpmbuild/SOURCES/musicdb.sysusers
    rpmbuild -bb musicdb.spec
    cp ~/rpmbuild/RPMS/noarch/musicdb* ../pkg/.

    echo -e "\e[1;32mdone"

    cd $oldwd
}



function BuildDEB {
    oldwd=$(pwd)
    cd $repository/dist

    rm -f "../pkg/musicdb-${version}-1_all.deb"

    local builddir="${HOME}/debbuild/musicdb"
    echo -e "\e[1;34mCreating build directory \e[0;36m${builddir} \e[1;34m…"
    rm -rf ${builddir}
    mkdir -p ${builddir}
    cd ${builddir}

    # Prepare sources
    local sourcename="musicdb-${version}-src"
    echo -e "\e[1;34mPreparing source files …"
    cp ${repository}/pkg/musicdb-${version}-src.tar.zst .
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
    cp -r ${repository}/dist/debian .
    cp    ${repository}/share/musicdb.service ./debian/musicdb.service
    cp    ${repository}/share/tmpfiles.conf   ./debian/musicdb.tmpfiles
    cp    ${repository}/share/sysusers.conf   ./debian/musicdb.sysusers

    # Build deb package
    echo -e "\e[1;34mBuilding deb package …\e[0m"
    debuild -uc -us --lintian-opts --profile debian
    # -uc -us: Do not sign source and changes
    # --profile debian: See: https://bugs.launchpad.net/ubuntu/+source/lintian/+bug/1303603

    cp ${builddir}/musicdb*.deb ${repository}/pkg/.

    echo -e "\e[1;32mdone"

    cd $oldwd
}



function BuildDocumentation {
    pkgname="musicdb-${version}-doc"
    tmp="/tmp/${pkgname}"
    mkdir -p "$tmp/musicdb"

    oldwd=$(pwd)
    cd $repository/docs/

    echo -e "\e[1;35m - \e[1;34mCompiling Documentation…"
    make html BUILDDIR=$tmp 2>&1

    echo -e "\e[1;35m - \e[1;34mCreating Source Archive…"
    mv ${tmp}/html ${tmp}/${pkgname}
    tar -c --zstd -C ${tmp} -f ${repository}/pkg/${pkgname}.tar.zst $pkgname

    rm -r "$tmp"
    echo -e "\e[1;32mdone"

    cd $oldwd
}



if [[ $# -eq 0 ]] ; then
    PrintHelp
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            PrintHelp
            exit 0
            ;;
        src)
            BuildSource
            ;;
        rpm)
            BuildRPM
            ;;
        pkg)
            BuildPKG
            ;;
        deb)
            BuildDEB
            ;;
        doc)
            BuildDocumentation
            ;;
        *)
            echo -e "\e[1;31mUnknown parameter $1!\e[0m"
            PrintHelp
            exit 1
            ;;
    esac

    shift
done
