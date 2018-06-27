#!/usr/bin/env bash

# _ExpectingTool command
#
# Checks if software exists.
# When it does not exist, then the script gets abort by calling exit 1
function _ExpectingTool {
    local tool="$1"

    if ! type "$tool" 2> /dev/null > /dev/null ; then
        echo -e "\e[1;31mThe mandatory tool \e[1;35m$tool\e[1;31m missing!\e[0m"
        exit 1
    fi
}

# _ExpectingDirectory Path
#
# Checks if directory exists.
# When it does not exist, then the script gets abort by calling exit 1
#function _ExpectingDirectory {
#    local path="$1"
#
#    if [ ! -d "$path" ]; then
#        echo -e "\e[1;31mDirectory \e[0;36m$path\e[1;31m missing!\e[0m"
#        exit 1
#    fi
#}

# _CreateGroupIfNotExists GroupName
#
# Checks if the group exists. When not, it gets created
#function _CreateGroupIfNotExists {
#    local GROUPNAME="$1"
#
#    if [ -z "$(getent group $GROUPNAME)" ]; then
#        echo -e -n "\t\e[1;34mCreating \e[0;36m$GROUPNAME \e[1;31m"
#        # Creates a new unix system group
#        groupadd -r $GROUPNAME
#        usermod -a -G $MDBGROUP $USER
#        echo -e "\e[1;32mdone"
#    fi
#}

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

