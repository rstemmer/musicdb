#!/usr/bin/env bash

# TCP-Ports for accessing the servers
HTTP=10080
AUDIO=10666
WSS=9000    # Do not change until you changed it in the Java Script and MusicDB Configuration

echo "WebUI: http://localhost:$HTTP/musicdb/webui/moderator.html"

docker run --publish=$HTTP:80 --publish=$AUDIO:666 --publish=$WSS:9000 -it 'musicdb:0.0.1'

# TODO: Replace -it by -d when everything is done

