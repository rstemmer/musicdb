#!/usr/bin/env bash

#
# Creates a new SSL key and certificate for MusicDBs WebSocket connection (will also be used for icecast)
#
function CreateMusicDBSSLKeys {
    local SSLKEY="$1"
    local SSLCRT="$2"
    local HTTPGROUP="$3"
    local SSLDIR="$(dirname $SSLKEY)"


    _ExpectingTool  openssl
    _ExpectingGroup $HTTPGROUP


    # Create directory if not exists
    if [ ! -d "$SSLDIR" ] ; then
        mkdir -p "$SSLDIR"
    fi

    if [ ! -f "$SSLKEY" ] ; then
        echo -e "\e[1;34mCreating SSL Keys in \e[0;36m$SSLDIR\e[0m: "
        openssl req -new -x509 -days 3650 -sha512 -newkey rsa:2048 -nodes \
            -keyout "$SSLKEY" -out "$SSLCRT"

        # create a shareable cert
        openssl pkcs12 -export \
            -out   "${SSLCRT%.*}.pfx" \
            -in    "$SSLCRT" \
            -inkey "$SSLKEY" -name "$(hostname)"
         
        # create a pem-file (needed by some apps)
        cat "$SSLKEY" >  "${SSLCRT%.*}.pem"
        cat "$SSLCRT" >> "${SSLCRT%.*}.pem"
         
        # Prevent "file not found" error
        sync

        # give good permissions:
        chown root:$HTTPGROUP "$SSLDIR"/*
        chmod ug=r,o-r        "$SSLDIR"/*
        echo -e "\t\e[1;32mdone"
    fi
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

