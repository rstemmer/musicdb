#!/usr/bin/env bash


function InstallMusicDBFiles {
    local SOURCEDIR="$1"
    local SERVERDIR="$2"
    local MDBUSER="$3"
    local MDBGROUP="$4"
    local WSAPIKEY="$5"

    _ExpectingTool  rsync
    _ExpectingUser  $MDBUSER
    _ExpectingGroup $MDBGROUP

    echo -e -n "\e[1;34mInstalling MusicDB files to \e[0;36m$SERVERDIR\e[1;34m: "

    WSCONFIG=$SERVERDIR/webui/config.js
    if [ -f "$WSCONFIG" ] ; then
        cp "$WSCONFIG" "/tmp/mdbwebuicfg.bak"
    fi

    rsync -uav  \
        --exclude 'tmp/' \
        --exclude 'id3edit/' \
        --exclude 'lib/crawler/' \
        --exclude 'scripts/' \
        --exclude 'docs/build/doctrees/' \
        --exclude 'Dockerfile' \
        --exclude '.git/' \
        --exclude '.gitignore' \
        --exclude '*.swp' \
        --exclude '*.swo' \
        --exclude '*.pyc' \
        --exclude '*~' \
        --delete \
        $SOURCEDIR/ $SERVERDIR/. > /dev/null

    set +f
    cp $SOURCEDIR/scripts/helper/*.sh "$SERVERDIR/."
    set -f

    if [ -f "/tmp/mdbwebuicfg.bak" ] ; then
        mv "/tmp/mdbwebuicfg.bak" "$WSCONFIG"
    else
        sed -i -e "s;WSAPIKEY;\"$WSAPIKEY\";g" $WSCONFIG
    fi
    chown -R $MDBUSER:$MDBGROUP $SERVERDIR

    echo -e "\e[1;32mdone\e[0m"
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

