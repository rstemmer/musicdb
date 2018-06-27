#!/usr/bin/env bash

set -e

SCRIPTVERSION="1.3.3"
echo -e "\e[1;31mMusicDB-Install [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"


# mdbdirtree.sh
# mdbusers.sh
# ssl.sh
# mdbconfig.sh
# database.sh
# icecast.sh


function InstallLogrotateConfiguration {
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
    echo -e -n "\e[1;34mSetup shell profile in \e[0;36m/etc/profile.d/musicdb.sh\e[1;34m: \e[1;31m"
    if [ ! -f "/etc/profile.d/musicdb.sh" ] ; then
        cp $SOURCEDIR/share/profile.sh /etc/profile.d/musicdb.sh
        sed -i -e "s;SERVERDIR;$SERVERDIR;g"   /etc/profile.d/musicdb.sh
        echo -e "\e[1;32mdone"
    else
        echo -e "\e[1;37malready done!"
    fi
}



function InstallMusicDBFiles {
    echo -e -n "\e[1;34mInstalling MusicDB files to \e[0;36m$SERVERDIR\e[1;34m: "
    if ! type rsync 2> /dev/null > /dev/null ; then
        echo -e "\e[1;31mThe mandatory tool \e[1;35mrsync\e[1;31m is missing! \e[1;30m(No rsync installed?)\e[0m"
        exit 1
    fi

    WSCLIENTFILE=$SERVERDIR/webui/js/musicdb.js
    if [ -f "$WSCLIENTFILE" ] ; then
        # this is an update, so save the websocket and watchdog configuration before overwriting this file
        WATCHDOG_RUN="$(     grep "var.WATCHDOG_RUN"      $WSCLIENTFILE)"
        WATCHDOG_INTERVAL="$(grep "var.WATCHDOG_INTERVAL" $WSCLIENTFILE)"
        WEBSOCKET_URL="$(    grep "var.WEBSOCKET_URL"     $WSCLIENTFILE)"
    fi

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

    chown -R $MDBUSER:$MDBGROUP $SERVERDIR

    # on update, reset the settings from the old version of the musicdb.js file
    if [ ! -z "$WATCHDOG_RUN" ] ; then
        sed -i -e "s\\var.WATCHDOG_RUN.*\\$WATCHDOG_RUN\\g"           $WSCLIENTFILE
        sed -i -e "s\\var.WATCHDOG_INTERVAL.*\\$WATCHDOG_INTERVAL\\g" $WSCLIENTFILE
        sed -i -e "s\\var.WEBSOCKET_URL.*\\$WEBSOCKET_URL\\g"         $WSCLIENTFILE
    fi

    echo -e "\e[1;32mdone\e[0m"
}



function InstallID3Edit {
    if ! type git 2> /dev/null > /dev/null ; then
        echo -e "\e[1;31mThe mandatory tool \e[1;35mgit\e[1;31m is missing! \e[1;30m(No git installed?)\e[0m"
        exit 1
    fi

    HERE=$(pwd)

    # install libprinthex
    echo -e -n "\e[1;34mInstalling \e[0;36mlibprinthex\e[1;34m: "
    if [ ! -f /usr/local/lib/libprinthex.a ] ; then
        if ! type gcc 2> /dev/null > /dev/null ; then
            echo -e "\e[1;31mThe mandatory tool \e[1;35mgcc\e[1;31m missing! \e[1;30m(No gcc/binutils installed?)\e[0m"
            exit 1
        fi
        cd /tmp
        echo -e "\e[1;30m"
        git clone https://github.com/rstemmer/libprinthex.git
        cd libprinthex
        ./build.sh
        ./install.sh
        cd /tmp
        rm -r libprinthex
        echo -e "\e[1;32mdone"
    else
        echo -e "\e[1;37malready done!"
    fi

    cd $HERE

    # install id3edit
    echo -e -n "\e[1;34mInstalling \e[0;36mid3edit\e[1;34m: \e[1;31m"
    local INSTALLID3EDIT="False"
    if ! type id3edit 2> /dev/null > /dev/null ; then
        INSTALLID3EDIT="True"
    else
        # check if the already installed version is up to date
        local BIN_MAJOR=$(id3edit --version | cut -d "." -f 1)
        local BIN_MINOR=$(id3edit --version | cut -d "." -f 2)
        local BIN_PATCH=$(id3edit --version | cut -d "." -f 3)

        local SRC_MAJOR=$(grep "#define VERSION" ./id3edit/main.c | cut -d " " -f 3 | tr -d \" | cut -d "." -f 1)
        local SRC_MINOR=$(grep "#define VERSION" ./id3edit/main.c | cut -d " " -f 3 | tr -d \" | cut -d "." -f 2)
        local SRC_PATCH=$(grep "#define VERSION" ./id3edit/main.c | cut -d " " -f 3 | tr -d \" | cut -d "." -f 3)

        if [ $SRC_MAJOR -gt $BIN_MAJOR ] ; then
            INSTALLID3EDIT="True"
        elif [ $SRC_MAJOR -eq $BIN_MAJOR ] ; then
            if [ $SRC_MINOR -gt $BIN_MINOR ] ; then
                INSTALLID3EDIT="True"
            elif [ $SRC_MINOR -eq $BIN_MINOR ] ; then
                if [ $SRC_PATCH -gt $BIN_PATCH ] ; then
                    INSTALLID3EDIT="True"
                fi
            fi
        fi
    fi


    if [ "$INSTALLID3EDIT" == "True" ] ; then
        if ! type clang 2> /dev/null > /dev/null ; then
            echo -e "\e[1;31mThe mandatory tool \e[1;35mclang\e[1;31m missing! \e[1;30m(No clang installed?)\e[0m"
            exit 1
        fi
        cd id3edit
        ./build.sh
        ./install.sh
        echo -e "\e[1;32mdone"
    else
        echo -e "\e[1;37malready done!"
    fi

    cd $HERE
}


echo -e "\e[1;34mChecking environment: "
# Check the environment this script is executed in.
# Depending on the Linux distribution some things work different.

# You need to have root permission for the installation process
if [ $EUID -ne 0 ]; then
    echo -e "\t\e[1;31mYou need to have root permissions!\e[0m"
    exit 1
fi
if ! type sed 2> /dev/null > /dev/null ; then
    echo -e "\e[1;31mThe mandatory tool \e[1;35msed\e[1;31m is missing!\e[0m"
    exit 1
fi
if ! type dialog 2> /dev/null > /dev/null ; then
    echo -e "\e[1;31mThe mandatory tool \e[1;35mdialog\e[1;31m is missing!\e[0m"
    exit 1
fi


# Figure out, how the apache unix group is called
if [ ! -z "$(getent group www-data)" ]; then
    HTTPGROUP="www-data"
elif [ ! -z "$(getent group http)" ]; then
    HTTPGROUP="http"
elif [ ! -z "$(getent group apache)" ]; then
    HTTPGROUP="apache"
elif [ ! -z "$(getent group apache2)" ]; then
    HTTPGROUP="apache2"
else
    echo -e "\t\e[1;31mUnable to figure out how the HTTP unix group is called! \e[1;30m(No HTTP server installed?)\e[0m"
    exit 1
fi

# Check if pwd is the source directory
SOURCEDIR="$(pwd)"
if [ ! -d "$SOURCEDIR/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the source directory! \e[1;30m($SOURCEDIR/.git directory missing)\e[0m"
    exit 1
fi


# Check if there is already an installation that only shall be updated
if [ -f "/etc/musicdb.ini" ] ; then
    echo -e "\t\e[1;37mFound a MusicDB installation to update\e[0m"
    FORMTITLE="MusicDB Update"

    # When there is already an installation, get as much as possible information from it
    DATADIR="$(dirname "$(readlink /etc/musicdb.ini)")"
    SERVERDIR="$(dirname "$(which musicdb)")"
    MUSICDIR="$(sed -nr '/\[music\]/,/\[/{/path/p}'  /etc/musicdb.ini | cut -d "=" -f 2)"
    MDBGROUP="$(sed -nr '/\[music\]/,/\[/{/group/p}' /etc/musicdb.ini | cut -d "=" -f 2)"
    USER="$(    sed -nr '/\[music\]/,/\[/{/owner/p}' /etc/musicdb.ini | cut -d "=" -f 2)" # The music owner, not the MDB user!
    SSLKEY="$(  sed -nr '/\[tls\]/,/\[/{/key/p}'     /etc/musicdb.ini | cut -d "=" -f 2)"
    SSLCRT="$(  sed -nr '/\[tls\]/,/\[/{/cert/p}'    /etc/musicdb.ini | cut -d "=" -f 2)"
    MDBUSER="musicdb"

    if [ "$SERVERDIR" == "." ] ; then
        echo -e "\t\e[1;33mUnable to find the server directory! \e[1;30m(Server directory must be in \$PATH)"
        SERVERDIR="?"
    fi

    # Check if server is running - this should not be the case while updating
    SERVER_PIDFILE=$(awk -F "=" '/pidfile/ {print $2}' /etc/musicdb.ini)
    if [ -f "$SERVER_PIDFILE" ] ; then
        echo -e "\t\e[1;31mServer still running!\e[1;30m (stop musicdb and mpd before updating)\e[0m"
        exit 1
    fi
else
    FORMTITLE="MusicDB Installation"

    DATADIR="/opt/musicdb/data"
    SERVERDIR="/opt/musicdb/server"
    MUSICDIR="/var/music"
    MDBGROUP="musicdb"
    USER="$(getent passwd 1000 | cut -d ":" -f 1)"    # system user
    SSLKEY="/etc/ssl/musicdb/musicdb.key"
    SSLCRT="/etc/ssl/musicdb/musicdb.cert"
    MDBUSER="musicdb"
fi


# Check if we are on the master branch. If not, inform the user that he installs indev software
BRANCHNAME="$(git branch | grep \* | cut -d ' ' -f2)"
if [ "$BRANCHNAME" != "master" ] ; then
    FORMTITLE="$FORMTITLE !! from develop branch !!"
fi


echo -e "\e[1;32mdone\e[0m"


FORMFILE=/tmp/form.$$
# dialog --form text height width formheight [ label y x item y x flen ilen ]
dialog --backtitle "$FORMTITLE" --title "Installation Setup" \
    --form "\nCheck and specify the MusicDB environment\n" 18 71 10 \
    "Source directory:" 1 1 "$SOURCEDIR"    1 20 45 0 \
    "Server directory:" 2 1 "$SERVERDIR"    2 20 45 0 \
    "Data directory:"   3 1 "$DATADIR"      3 20 45 0 \
    "Music directory:"  4 1 "$MUSICDIR"     4 20 45 0 \
    "MusicDB group:"    5 1 "$MDBGROUP"     5 20 45 0 \
    "MusicDB user:"     6 1 "$MDBUSER"      6 20 45 0 \
    "HTTP group:"       7 1 "$HTTPGROUP"    7 20 45 0 \
    "SSL key file:"     8 1 "$SSLKEY"       8 20 45 0 \
    "SSL certificate"   9 1 "$SSLCRT"       9 20 45 0 \
    2> $FORMFILE

# the form file exists anyway, but only when pressed OK it holds the new setting
if [ -s $FORMFILE ] ; then
    SOURCEDIR="$(sed  "1q;d" $FORMFILE)"
    SERVERDIR="$(sed  "2q;d" $FORMFILE)"
    DATADIR="$(  sed  "3q;d" $FORMFILE)"
    MUSICDIR="$( sed  "4q;d" $FORMFILE)"
    MDBGROUP="$( sed  "5q;d" $FORMFILE)"
    MDBUSER="$(  sed  "6q;d" $FORMFILE)"
    HTTPGROUP="$(sed  "7q;d" $FORMFILE)"
    SSLKEY="$(   sed  "8q;d" $FORMFILE)"
    SSLCRT="$(   sed  "9q;d" $FORMFILE)"
fi

rm $FORMFILE


clear
echo -e "\e[1;31mMusicDB-Install [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"
echo -e "\e[1;37m$FORMTITLE"
echo -e "\t\e[1;34mSource directory: \e[0;36m$SOURCEDIR"
echo -e "\t\e[1;34mServer directory: \e[0;36m$SERVERDIR"
echo -e "\t\e[1;34mData directory:   \e[0;36m$DATADIR"
echo -e "\t\e[1;34mMusic directory:  \e[0;36m$MUSICDIR"
echo -e "\t\e[1;34mMusicDB group:    \e[0;36m$MDBGROUP"
echo -e "\t\e[1;34mMusicDB user:     \e[0;36m$MDBUSER"
echo -e "\t\e[1;34mHTTP group:       \e[0;36m$HTTPGROUP"
echo -e "\t\e[1;34mSSL key file:     \e[0;36m$SSLKEY"
echo -e "\t\e[1;34mSSL certificate:  \e[0;36m$SSLCRT"



# Start installing process
CreateMusicDBGroup
CreateMusicDBUser
CreateMusicDBSSLKeys
CreateBaseDirectories

InstallMusicDBConfiguration
InstallMusicDBDatabases
UpdateMusicDBDatabases      # Check if things must be updated
InstallArtwork
InstallMusicAI

InstallIcecastEnvironment
InstallLogrotateConfiguration
InstallShellProfile

# TODO: Setup apache - debians apache installation is inacceptable messed up. No script for this.
InstallID3Edit
InstallMusicDBFiles


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

