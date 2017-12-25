#!/usr/bin/env bash

set -e

SCRIPTVERSION="1.0.0"
echo -e "\e[1;31mMusicDB-Uninstall [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"




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


# Check if pwd is the source directory
SOURCEDIR="$(pwd)"
if [ ! -d "$SOURCEDIR/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the source directory! \e[1;30m($SOURCEDIR/.git directory missing)\e[0m"
    exit 1
fi


# Check if there is already an installation that only shall be updated
if [ -f "/etc/musicdb.ini" ] ; then
    echo -e "\t\e[1;37mFound a MusicDB installation to update\e[0m"
    FORMTITLE="Uninstall MusicDB"

    # When there is already an installation, get as much as possible information from it
    DATADIR="$(dirname "$(readlink /etc/musicdb.ini)")"
    SERVERDIR="$(dirname "$(which musicdb)")"
    SSLKEY="$(  sed -nr '/\[tls\]/,/\[/{/key/p}'     /etc/musicdb.ini | cut -d "=" -f 2)"
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
    echo -e "\e[1;31mCannot find MusicDB installation!\e[0m"
    exit 1
fi


echo -e "\e[1;32mdone\e[0m"


# First, let the user check the detected environment data
FORMFILE=/tmp/form.$$
# dialog --form text height width formheight [ label y x item y x flen ilen ]
dialog --backtitle "$FORMTITLE" --title "Installation Setup" \
    --form "\nCheck and specify the MusicDB environment\n" 12 71 4 \
    "Server directory:" 1 1 "$SERVERDIR"    1 20 45 0 \
    "Data directory:"   2 1 "$DATADIR"      2 20 45 0 \
    "MusicDB user:"     3 1 "$MDBUSER"      3 20 45 0 \
    "SSL key file:"     4 1 "$SSLKEY"       4 20 45 0 \
    2> $FORMFILE

# the form file exists anyway, but only when pressed OK it holds the new setting
if [ -s $FORMFILE ] ; then
    SERVERDIR="$(sed  "1q;d" $FORMFILE)"
    DATADIR="$(  sed  "2q;d" $FORMFILE)"
    MDBUSER="$(  sed  "3q;d" $FORMFILE)"
    SSLKEY="$(   sed  "4q;d" $FORMFILE)"
fi

rm $FORMFILE

# Now let the user choose what shall be uninstalled
# suggest some good defaults
RMSERVERDIR="on"
RMDATADIR="off"
RMSSLKEYS="on"
RMPROFILE="on"
RMLOGROTATE="on"
RMUSER="on"
RMID3EDIT="off"
RMPRINTHEX="off"

#dialog --checklist [Text] [Höhe] [Breite] [Listenhöhe] [Tag1] [Eintrag1] [Status1] ...
dialog --backtitle "$FORMTITLE" --title "Uninstall Setup" \
    --checklist "MusicDB components to uninstall/remove" 16 50 8 \
    "serverdir" "Server directory"      "$RMSERVERDIR" \
    "datadir"   "Data directory"        "$RMDATADIR" \
    "sslkeys"   "SSL keys"              "$RMSSLKEYS" \
    "profile"   "Shell profile"         "$RMPROFILE" \
    "logrotate" "Logrotate config"      "$RMLOGROTATE" \
    "user"      "musicdb user/group"    "$RMUSER" \
    "id3edit"   "ID3Edit"               "$RMID3EDIT" \
    "printhex"  "libPrintHex"           "$RMPRINTHEX" \
    2> $FORMFILE


# assume the user selected nothing to uninstall
RMSERVERDIR="off"
RMDATADIR="off"
RMSSLKEYS="off"
RMPROFILE="off"
RMLOGROTATE="off"
RMUSER="off"
RMID3EDIT="off"
RMPRINTHEX="off"

# some optical marker for the user to check the selected components
MARKEROFF="\e[1;34m[\e[1;32m✔\e[1;34m]"
MARKERON="\e[1;34m[\e[1;31m✘\e[1;34m]"

MARKSERVERDIR=$MARKEROFF
MARKDATADIR=$MARKEROFF
MARKSSLKEYS=$MARKEROFF
MARKPROFILE=$MARKEROFF
MARKLOGROTATE=$MARKEROFF
MARKUSER=$MARKEROFF
MARKID3EDIT=$MARKEROFF
MARKPRINTHEX=$MARKEROFF

for RESULT in $(cat $FORMFILE)
do
    case $RESULT in
        'serverdir' )
            RMSERVERDIR="on"
            MARKSERVERDIR=$MARKERON
            ;;
        'datadir' )
            RMDATADIR="on"
            MARKDATADIR=$MARKERON
            ;;
        'sslkeys' )
            RMSSLKEYS="on"
            MARKSSLKEYS=$MARKERON
            ;;
        'profile' )
            RMPROFILE="on"
            MARKPROFILE=$MARKERON
            ;;
        'logrotate' )
            RMLOGROTATE="on"
            MARKLOGROTATE=$MARKERON
            ;;
        'user' )
            RMUSER="on"
            MARKUSER=$MARKERON
            ;;
        'id3edit' )
            RMID3EDIT="on"
            MARKID3EDIT=$MARKERON
            ;;
        'printhex' )
            RMPRINTHEX="on"
            MARKPRINTHEX=$MARKERON
            ;;
    esac
done

rm $FORMFILE

clear
echo -e "\e[1;31mMusicDB-Uninstall [\e[1;34m$SCRIPTVERSION\e[1;31m]\e[0m"
echo -e "\e[1;37mDetected Setup - [\e[1;31m✘\e[1;37m] -> Remove ; [\e[1;32m✔\e[1;37m] -> Keep"
echo -e "\t\e[1;34mServer directory: $MARKSERVERDIR \e[0;36m$SERVERDIR"
echo -e "\t\e[1;34mData directory:   $MARKDATADIR \e[0;36m$DATADIR \e[1;31mDo you have a backup?"
echo -e "\t\e[1;34mSSL key file:     $MARKSSLKEYS \e[0;36m${SSLKEY%.*}.\e[1;36m*"
echo -e "\t\e[1;34mShell profile:    $MARKPROFILE \e[0;36m/etc/profile.d/musicdb.sh"
echo -e "\t\e[1;34mLogrotate config: $MARKLOGROTATE \e[0;36m/etc/logrotate.d/musicdb"
echo -e "\t\e[1;34mMusicDB user:     $MARKUSER \e[0;36m$MDBUSER\e[1;34m"
echo -e "\t\e[1;34mID3Edit:          $MARKID3EDIT \e[0;36m/usr/local/bin/id3\e[1;36m*"
echo -e "\t\e[1;34mlibPrintHex:      $MARKPRINTHEX \e[0;36m/usr/local/lib/libprinthex.a"
echo
echo -e "\e[1;34mTo start the unsinstall process enter \e[1;31mremove\e[1;34m:\e[1;31m"
read STARTREMOVE

if [ "$STARTREMOVE" != "remove" ] ; then
    echo -e "\e[1;32mRemoving MusicDB canceled."
    exit 1
fi


# Start uninstalling process
if [ "$RMSERVERDIR" == "on" ] ; then
    echo -e -n "\e[1;34mRemoving $SERVERDIR "
    rm -r $SERVERDIR
    echo -e "\e[1;31m✔"
fi
if [ "$RMDATADIR" == "on" ] ; then
    echo -e -n "\e[1;34mRemoving $DATADIR "
    rm -r $DATADIR
    echo -e "\e[1;31m✔"
fi
if [ "$RMSSLKEYS" == "on" ] ; then
    echo -e -n "\e[1;34mRemoving ${SSLKEY%.*}.* "
    rm ${SSLKEY%.*}.*
    echo -e "\e[1;31m✔"
fi
if [ "$RMPROFILE" == "on" ] ; then
    echo -e -n "\e[1;34mRemoving /etc/profile.d/musicdb.sh "
    rm /etc/profile.d/musicdb.sh
    echo -e "\e[1;31m✔"
fi
if [ "$RMLOGROTATE" == "on" ] ; then
    echo -e -n "\e[1;34mRemoving /etc/logrotate.d/musicdb "
    rm /etc/logrotate.d/musicdb
    echo -e "\e[1;31m✔"
fi
if [ "$RMUSER" == "on" ] ; then
    echo -e -n "\e[1;34mRemoving user musicdb "
    userdel musicdb
    echo -e "\e[1;31m✔"
fi
if [ "$RMID3EDIT" == "on" ] ; then
    echo -e -n "\e[1;34mRemoving /usr/local/bin/id3* "
    rm /usr/local/bin/id3*
    echo -e "\e[1;31m✔"
fi
if [ "$RMPRINTHEX" == "on" ] ; then
    echo -e -n "\e[1;34mRemoving /usr/local/lib/libprinthex.a "
    rm /usr/local/lib/libprinthex.a
    rm /usr/local/include/printhex.h
    echo -e "\e[1;31m✔"
fi

echo -e "\e[1;32mdone\e[0m"


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

