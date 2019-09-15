#!/usr/bin/env bash

# TCP-Ports for accessing the servers
HTTP=10080
AUDIO=10666
DEMOMUSICDIR=/tmp/mdbmusic
WSS=9000    # Do not change until you changed it in the Java Script and MusicDB Configuration

echo -e ""
echo -e "\t\e[1;33m !! Important !! "
echo -e ""
echo -e "\e[1;35m1.:\e[1;36m Start MusicDB WebSocket server and dependencies:"
echo -e "\t\e[1;36mExecute the script \e[1;34m container-boot.sh \e[1;36m"
echo -e "\t\e[1;30mA log file can be read via  less -R /opt/musicdb/data/debuglog.ansi"
echo -e ""
echo -e "\e[1;35m2.:\e[1;36m Allow secured WebSocket connection in Firefox:"
echo -e "\t\e[1;36mAccess \e[1;37mhttps://localhost:9000/"
echo -e "\t\e[1;36mClick on \e[1;34m Advanced ... \e[0m"
echo -e "\t\e[1;36mClick on \e[1;34m Accept the Risk and Continue \e[0m"
echo -e "\t\e[1;30mNow, the AutobahnPython version number should be displayed on blue background."
echo -e ""
echo -e "\e[1;35m3.:\e[1;36m You can now open the WebUI:"
echo -e "\t\e[1;37mhttp://localhost:$HTTP/musicdb/webui/moderator.html\e[0m"
echo -e ""
echo -e "\e[1;35m4.:\e[1;36m Import Music"
echo -e "\t\e[1;36mThe music directory the Docker container will access is at \e[1;34m $DEMOMUSICDIR"
echo -e "\t\e[1;36mIt is important that the directory structure follows the following scheme:"
echo -e "\t\t\e[1;34mArtist-Name\e[1;37m/\e[1;34mAlbum-Name\e[1;37m/\e[1;34mSong-Name\e[1;37m.extension"
echo -e "\t\e[1;36mTo add all albums run  \e[1;34m musicdb add    \e[1;30m (see https://rstemmer.github.io/musicdb/build/html/mod/add.html )"
echo -e "\t\e[1;30mTo edit genres execute \e[1;30m musicdb genres \e[1;30m (see https://rstemmer.github.io/musicdb/build/html/mod/genres.html )"
echo -e "\e[0m"

mkdir -p $DEMOMUSICDIR
docker run --publish=$HTTP:80 --publish=$AUDIO:666 --publish=$WSS:9000 --mount type=bind,source=$DEMOMUSICDIR,target=/var/music -it 'musicdb:0.0.1'
echo -e -n "\e[1;33m"
rmdir $DEMOMUSICDIR
echo -e -n "\e[0m"

