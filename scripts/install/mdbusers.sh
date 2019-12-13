#!/usr/bin/env bash

# SetupUsersAndGroups MDBUser MDBGroup User
#
# 1.: Creates a new group for MusicDB if it does not exist
#     The music owner ("User") gets added to the MusicDB group
# 2.: Adds a new user for MusicDB if it does not exist
#
function SetupUsersAndGroups {
    local MDBUSER="$1"
    local MDBGROUP="$2"
    local USER="$3"

    _ExpectingUser $USER

    # Create MusicDB group
    if [ -z "$(getent group $MDBGROUP)" ]; then
        echo -e -n "\e[1;34mCreating musicdb group \e[0;36m$MDBGROUP\e[1;34m: \e[1;31m"
        # Creates a new unix system group
        groupadd -r $MDBGROUP
        usermod -a -G $MDBGROUP $USER
        echo -e "\e[1;32mdone"
    fi

    # Create MusicDB user
    if [ -z "$(getent passwd $MDBUSER)" ]; then
        echo -e -n "\e[1;34mCreating musicdb user \e[0;36m$MDBUSER\e[1;34m: \e[1;31m"
        # Select first bash-entry from /etc/shells as user shell.
        # There may be multiple bash entries (/bin/bash, /usr/bin/bash), so "-m 1" is required
        useradd -d $DATADIR -s "$(grep -m 1 -w bash /etc/shells)" -g $MDBGROUP -r -M $MDBUSER
        usermod -a -G $HTTPGROUP $MDBUSER
        echo -e "\e[1;32mdone"
    fi
}


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

