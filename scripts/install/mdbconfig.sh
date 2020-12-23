#!/usr/bin/env bash

# InstallMusicDBConfiguration SourceDir ServerDir DataDir MusicDir MDBUser MDBGroup

# Before: existing musicdb.ini or no configuration at all
# After: Valid musicdb.ini for the latest version

function InstallMusicDBConfiguration {
    local SOURCEDIR="$1"
    local SERVERDIR="$2"
    local DATADIR="$3"
    local MUSICDIR="$4"
    local USER="$5"
    local MDBUSER="$6"
    local MDBGROUP="$7"
    local SSLKEY="$8"
    local SSLCRT="$9"
    local CONFIGFILE="$DATADIR/musicdb.ini"
    local WSAPIKEY="${10}"

    _ExpectingUser  $USER
    _ExpectingUser  $MDBUSER
    _ExpectingGroup $MDBGROUP
    _ExpectingFile  $SSLKEY
    _ExpectingFile  $SSLCRT

    if [ ! -f "$DATADIR/musicdb.ini" ] ; then
        echo -e -n "\e[1;34mInstalling \e[0;36mmusicdb.ini\e[1;34m: \e[1;31m"
    else
        mv "$DATADIR/musicdb.ini" "$DATADIR/musicdb.ini.bak"
        echo -e    "\e[1;34mOld configuration moved to \e[0;36mmusicdb.ini\e[1;33m.bak\e[1;34m: \e[1;31m"
        echo -e -n "\e[1;34mInstalling \e[0;36mmusicdb.ini\e[1;34m: \e[1;31m"
    fi

    # Install file new configuration file
    install -m 664 -g $MDBGROUP -o $MDBUSER $SOURCEDIR/share/musicdb.ini -D $CONFIGFILE

    # Update configuration to the real setup
    sed -i -e "s;DATADIR;$DATADIR;g"       $CONFIGFILE
    sed -i -e "s;SERVERDIR;$SERVERDIR;g"   $CONFIGFILE
    sed -i -e "s;MUSICDIR;$MUSICDIR;g"     $CONFIGFILE
    sed -i -e "s;MUSICDBGROUP;$MDBGROUP;g" $CONFIGFILE
    sed -i -e "s;USER;$USER;g"             $CONFIGFILE
    sed -i -e "s;SSLKEY;$SSLKEY;g"         $CONFIGFILE
    sed -i -e "s;SSLCRT;$SSLCRT;g"         $CONFIGFILE
    sed -i -e "s;WSAPIKEY;$WSAPIKEY;g"     $CONFIGFILE

    # Create a link in /etc because this is the default path to look for the configuration
    ln -sf $DATADIR/musicdb.ini /etc/musicdb.ini
    echo -e "\e[1;32mdone"
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

