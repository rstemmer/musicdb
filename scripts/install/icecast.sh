#!/usr/bin/env bash


function SetupIcecastEnvironment {
    local SOURCEDIR="$1"
    local DATADIR="$2"
    local MDBGROUP="$3"
    local SSLCRT="$4"

    echo -e "\e[1;34mSetup Icecast environment in \e[0;36m$DATADIR/icecast\e[1;31m"

    _ExpectingTool openssl

    # Find correct icecast binary
    #local ICECAST=""

    #if type "icecast" 2> /dev/null > /dev/null ; then
    #    ICECAST=icecast
    #elif type "icecast2" 2> /dev/null > /dev/null ; then
    #    # Debian based distributions have a different name for the icecast binary
    #    ICECAST=icecast2
    #else
    #    echo -e    "\t\e[1;33micecast binary missing! \e[1;30m(icecast not yet installed?)"
    #    echo -e -n "\t\e[1;34mInstalling configuration anyway: \e[1;31m"
    #fi


    # Check group
    if [ -z "$(getent group icecast)" ]; then
        groupadd -r icecast
        echo -e "\t\e[1;34micecast group created\e[1;31m "
    fi
    # Check user
    if [ -z "$(getent passwd icecast)" ]; then
        useradd -d "$DATADIR/icecast" -s /usr/bin/false -g icecast -r -N -M icecast
        echo -e -n "\t\e[1;34micecast user created\e[1;31m "
    fi

    # Install icecast directories
    if [ ! -d "$DATADIR/icecast" ] ; then
        echo -e -n "\t\e[1;34mCreating \e[0;36m$DARADIR/icecast/* \e[1;31m"
        mkdir -p "$DATADIR/icecast/log"
        touch    "$DATADIR/icecast/users"
        chown -R icecast:$MDBGROUP "$DATADIR/icecast"
        chmod o-r "$DATADIR/icecast/users"

        echo -e "\e[1;32mdone"
    fi

    # Install SSL certificate
    if [ ! -d "$DATADIR/icecast/certificate.pem" ] ; then
        install -m 400 -g $MDBGROUP -o icecast "$SSLCRT" -D "$DATADIR/icecast/certificate.pem"
    fi

    # Install configuration
    if [ ! -d "$DATADIR/icecast/config.xml" ] ; then
        install -m 664 -g $MDBGROUP -o icecast "$SOURCEDIR/share/config.xml" -D "$DATADIR/icecast/."

        # Create some secure default passwords
        local SOURCEPW="$(openssl rand -base64 32)"
        local ADMINPW="$( openssl rand -base64 32)"
        
        sed -i -e "s;DATADIR;$DATADIR;g"                $DATADIR/icecast/config.xml
        sed -i -e "s;MDBGROUP;$MDBGROUP;g"              $DATADIR/icecast/config.xml
        sed -i -e "s;ICECASTSOURCEPASSWORD;$SOURCEPW;g" $DATADIR/icecast/config.xml
        sed -i -e "s;ICECASTADMINPASSWORD;$ADMINPW;g"   $DATADIR/icecast/config.xml
        sed -i -e "s;ICECASTSOURCEPASSWORD;$SOURCEPW;g" $DATADIR/musicdb.ini
        # also update a possible new MusicDB Configuration
        if [ -f "$DATADIR/musicdb.ini.new" ] ; then
            sed -i -e "s;ICECASTSOURCEPASSWORD;$SOURCEPW;g" $DATADIR/musicdb.ini.new
        fi

        echo -e "\e[1;32mdone"
    fi
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

