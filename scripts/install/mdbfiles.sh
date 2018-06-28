#!/usr/bin/env bash


function InstallMusicDBFiles {
    local SOURCEDIR="$1"
    local SERVERDIR="$2"
    local MDBUSER="$3"
    local MDBGROUP="$4"

    _ExpectingUser  rsync
    _ExpectingUser  $MDBUSER
    _ExpectingGroup $MDBGROUP

    echo -e -n "\e[1;34mInstalling MusicDB files to \e[0;36m$SERVERDIR\e[1;34m: "

    WSCONFIG=$SERVERDIR/webui/config.js
    cp "$WSCONFIG" "/tmp/mdbwebuicfg.bak"

    rsync -uav  \
        --exclude 'tmp/' \
        --exclude 'id3edit/' \
        --exclude 'lib/crawler/' \
        --exclude 'docs/build/doctrees/' \
        --exclude '.git/' \
        --exclude '.gitignore' \
        --exclude '*.swp' \
        --exclude '*.swo' \
        --exclude '*.pyc' \
        --exclude '*~' \
        --delete \
        $SOURCEDIR/ $SERVERDIR/. > /dev/null

    mv "/tmp/mdbwebuicfg.bak" "$WSCONFIG"
    chown -R $MDBUSER:$MDBGROUP $SERVERDIR

    echo -e "\e[1;32mdone\e[0m"
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

