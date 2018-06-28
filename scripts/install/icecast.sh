#!/usr/bin/env bash


function SetupIcecastEnvironment {
    local SOURCEDIR="$1"
    local DATADIR="$2"
    local MDBGROUP="$3"
    local SSLCRT="$4"

    echo -e "\e[1;34mSetup Icecast environment in \e[0;36m$DATADIR/icecast\e[1;31m"

    _ExpectingTool  openssl
    _ExpectingGroup $MDBGROUP
    _ExpectingFile  $SSLCRT


    # Check group
    if [ -z "$(getent group icecast)" ]; then
        groupadd -r icecast
        echo -e "\t\e[1;34micecast group created\e[1;31m "
    fi
    # Check user
    if [ -z "$(getent passwd icecast)" ]; then
        useradd -d "$DATADIR/icecast" -s /usr/bin/false -g icecast -r -N -M icecast
        echo -e "\t\e[1;34micecast user created\e[1;31m "
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
    if [ ! -f "$DATADIR/icecast/certificate.pem" ] ; then
        install -m 400 -g $MDBGROUP -o icecast "$SSLCRT" -D "$DATADIR/icecast/certificate.pem"
    fi

    # Install configuration
    if [ ! -f "$DATADIR/icecast/config.xml" ] ; then
        install -m 664 -g $MDBGROUP -o icecast "$SOURCEDIR/share/config.xml" -D "$DATADIR/icecast/."

        # Create some secure default passwords
        local SOURCEPW="$(openssl rand -base64 32)"
        local ADMINPW="$( openssl rand -base64 32)"
        
        sed -i -e "s;DATADIR;$DATADIR;g"                $DATADIR/icecast/config.xml
        sed -i -e "s;MDBGROUP;$MDBGROUP;g"              $DATADIR/icecast/config.xml
        sed -i -e "s;ICECASTSOURCEPASSWORD;$SOURCEPW;g" $DATADIR/icecast/config.xml
        sed -i -e "s;ICECASTADMINPASSWORD;$ADMINPW;g"   $DATADIR/icecast/config.xml
        sed -i -e "s;ICECASTSOURCEPASSWORD;$SOURCEPW;g" $DATADIR/musicdb.ini

        echo -e "\t\e[1;34mNew icecast source password: \e[1;36m$SOURCEPW"
        echo -e "\t\e[1;34mNew icecast admin  password: \e[1;36m$ADMINPW"
    fi
    echo -e "\t\e[1;32mdone"
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

