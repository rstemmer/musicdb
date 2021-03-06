#!/usr/bin/env bash


# UpdateDirectoryTree Source ServerDir DataDir MusicDir MusicUser MDBUser MDBGroup
#
# Checks the directory tree and creates missing directories
#
function CreateDirectoryTree {
    local SOURCEDIR="$1"
    local SERVERDIR="$2"
    local DATADIR="$3"
    local MUSICDIR="$4"
    local MUSICUSER="$5"
    local MDBUSER="$6"
    local MDBGROUP="$7"

    _ExpectingUser  $MUSICUSER
    _ExpectingUser  $MDBUSER
    _ExpectingGroup $MDBGROUP

    echo -e "\e[1;34mCreating base directories: \e[0m"


    ###################
    # Music Directory
    ###################

    # The music directory should already exist
    # If not, just create it - better than exiting
    if [ ! -d "$MUSICDIR" ]; then
        echo -e "\e[1;33mMusic directory \e[0;36m$MUSICDIR\e[1;33m does not exist!\e[0m"
        echo -e "\e[1;30mCreating $MUSICDIR.\e[0m"
        mkdir -p $MUSICDIR
    fi

    chown -R $MUSICUSER:$MDBGROUP $MUSICDIR



    ###################
    # Server Directory
    ###################

    # Create directory if not exists
    if [ ! -d "$SERVERDIR" ] ; then
        echo -e -n "\t\e[1;34mCreating \e[0;36m$SERVERDIR \e[1;31m"
        mkdir -p $SERVERDIR
        echo -e "\e[1;32mdone"

        chown -R $MDBUSER:$MDBGROUP $SERVERDIR
    fi


    ###################
    # Data Directory
    ###################

    # Create directory if not exists
    if [ ! -d "$DATADIR" ] ; then
        echo -e -n "\t\e[1;34mCreating \e[0;36m$DARADIR \e[1;31m"
        mkdir -p $DATADIR/artwork
        chown -R $MDBUSER:$MDBGROUP $DATADIR
        echo -e "\e[1;32mdone"
        chmod g+w $DATADIR
    fi

    # Update default artwork
    install -m 664 -g $MDBGROUP -o $MDBUSER $SOURCEDIR/share/default.jpg -D $DATADIR/artwork/.
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

