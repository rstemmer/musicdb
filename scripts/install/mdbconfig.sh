#!/usr/bin/env bash

# InstallMusicDBConfiguration SourceDir ServerDir DataDir MusicDir MDBUser MDBGroup

# Before: existing musicdb.ini or no configuration at all
# After: Valid musicdb.ini for the latest version

function InstallMusicDBConfiguration {
    local SOURCEDIR="$1"
    local SERVERDIR="$2"
    local DATADIR="$3"
    local MUSICDIR="$4"
    local MDBUSER="$5"
    local MDBGROUP="$6"
    local CONFIGFILE="$DATADIR/musicdb.ini"

    if [ ! -f "$DATADIR/musicdb.ini" ] ; then
        echo -e -n "\e[1;34mInstalling \e[0;36mmusicdb.ini\e[1;34m: \e[1;31m"
    else
        cp "$DATADIR/musicdb.ini" "$DATADIR/musicdb.ini.bak"
        echo -e -n "\e[1;34mOld configuration copied to \e[0;36mmusicdb.ini\e[1;33m.bak\e[1;34m: \e[1;31m"
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

    # Create a link in /etc because this is the default path to look for the configuration
    ln -sf $DATADIR/musicdb.ini /etc/musicdb.ini
    echo -e "\e[1;32mdone"

    echo -e -n "\e[1;34mInstalling \e[0;36mmdbstate.ini\e[1;34m: \e[1;31m"
    if [ ! -f "$DATADIR/mdbstate/state.ini" ] ; then
        # Install the MusicDB state file
        install -m 664 -g $MDBGROUP -o $MDBUSER $SOURCEDIR/share/mdbstate.ini  -D $DATADIR/mdbstate/state.ini
        chown $MDBUSER:$MDBGROUP $DATADIR/mdbstate

        if [ -f "$DATADIR/mdbstate.ini" ] ; then # REMOVE IN NEXT VERSION (v4)
            mv "$DATADIR/mdbstate.ini" "$DATADIR/mdbstate/state.ini"
            echo -e -n "\e[1;33m(moving old state file to new directory)"
        fi
        echo -e "\e[1;32mdone"
    else
        echo -e "\e[1;37malready done!"
    fi

}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

