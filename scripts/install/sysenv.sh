#!/usr/bin/env bash




function InstallLogrotateConfiguration {

    local SOURCEDIR="$1"
    local DATADIR="$2"
    local MDBUSER="$3"
    local MDBGROUP="$4"

    _ExpectingUser  $MDBUSER
    _ExpectingGroup $MDBGROUP

    echo -e -n "\e[1;34mSetup logrotate configuration \e[0;36m/etc/logrotatet.d/musicdb\e[1;34m: \e[1;31m"
    if ! type logrotate 2> /dev/null > /dev/null ; then
        echo -e "\e[1;33mThe optional tool \e[1;37mlogrotate\e[1;33m is missing! \e[1;30m(No logrotate installed?)\e[0m"
        return 0
    fi

    if [ -d /etc/logrotate.d ] ; then
        if [ ! -f "/etc/logrotate.d/musicdb" ] ; then
            cp $SOURCEDIR/share/logrotate.conf /etc/logrotate.d/musicdb
            sed -i -e "s;DATADIR;$DATADIR;g"   /etc/logrotate.d/musicdb
            sed -i -e "s;MDBUSER;$MDBUSER;g"   /etc/logrotate.d/musicdb
            sed -i -e "s;MDBGROUP;$MDBGROUP;g" /etc/logrotate.d/musicdb
            echo -e "\e[1;32mdone"
        else
            echo -e "\e[1;37malready done!"
        fi
    else
        echo -e "\e[1;31mLogrotate directory \e[1;35m/etc/logrotate.d\e[1;31m missing! \e[1;30m(No logrotate installed?)\e[0m"
        exit 1
    fi
}



function InstallShellProfile {

    local SOURCEDIR="$1"
    local SERVERDIR="$2"

    echo -e -n "\e[1;34mSetup shell profile in \e[0;36m/etc/profile.d/musicdb.sh\e[1;34m: \e[1;31m"
    if [ ! -f "/etc/profile.d/musicdb.sh" ] ; then
        cp $SOURCEDIR/share/profile.sh /etc/profile.d/musicdb.sh
        sed -i -e "s;SERVERDIR;$SERVERDIR;g"   /etc/profile.d/musicdb.sh
        echo -e "\e[1;32mdone"
    else
        echo -e "\e[1;37malready done!"
    fi
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

