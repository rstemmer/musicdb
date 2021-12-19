#!/usr/bin/env bash

# Call ./CreateDummyAlbum.sh $DestinationPath
# Creates a directory with fake album files

set -e

repository="$(dirname "$(pwd)")"
if [ ! -d "$repository/.git" ] ; then
    echo -e "\t\e[1;31mThe script must be executed from the \e[1;37mscripts\e[1;31m directory inside the MusicDB repository!"
    echo -e "\t\e[1;30m($repository/.git directory missing)\e[0m"
    exit 1
fi


albumname="MusicDB Test Album"
albumpath="$1/$albumname"
artistname="Test Artist"


function CreateEmptyMP3 {
    local path="$1"

    base64 --decode > "$path" << EOF
//uUZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAAE4ADj4+Pj
4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj4+Pj////////////////
//////////////////////////////////////////////////8AAABQTEFNRTMuMTAwBLkAAAAA
AAAAADUgJAaQjQAB4AAABOClHWotAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//vURAAAAioAXeAAAAA5
wAvMAAAAC4wteee9gQGnBW7495govjctbLXcgH1CAEATB8/E4IAg6DgIHMEMTg4CAIBjEAIO6wfD
HrD+D+CAJv/g4CAIAgGAfB8Hz//+CAIZQMfD//lwfB8H9HLb40kq8nBOD59YPg+XB8QAgciQEKwf
BDh7wfB8H/xACAIHMu/E4P//qBAMYIBj/Wa9Z/Ln8QA+H97e/M6SJuONIhFC3AZgMwmwuQ4lUdoc
RpE6A8IxOLX5rJjUFQVOwVBU6sFQVDTpUFQVBoGvBUFYKgqGuoGj0RB2oGga5UFQVBY9+IgZDXLH
vgqCuCoK/4iBk7/9W71Vv1JmlL0l1COiGmSkAhxpE6IMW0FSOEfs23NBSRLSoKgrBUFQ1BUFQ0oF
TpYGgZOqBoGmwVBUFga+oGgZBVwiBoFYieoGgaPSwdwWBoO/1gqCsqCuDLlA0DVQNB2WBoGgaBU7
/1gqCypMQU1FMy4xMDCqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
qqqqqqqqqqqqqqqq//sUZMsP8AAAaQAAAAgAAA0gAAABAAABpAAAACAAADSAAAAEqqqqqqqqqqqq
qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq
EOF

}


function CreateSong {
    # CreateSong SongNumber MaxSongs SongName [FileName]
    # example CreateSong "01" "3" "Song Name" ["Non conform file name"]
    # Hack: if MaxSongs is "no header", then there will be no ID3 header added to the mp3 song

    local number="$1"
    local maxsongs="$2"
    local track="$number/$maxsongs"
    local name="$3"
    local album="$albumname"
    local artist="$artistname"
    local release="2021"
    local cd="1/1"

    local songpath="$albumpath/$number $name.mp3"
    if [[ -n "$4" ]] ; then
        songpath="$albumpath/$4.mp3"
    fi

    echo -e -n "\e[1;37m[\e[s ]\e[1;34m Creating $songpath\e[0m"
    CreateEmptyMP3 "$songpath"

    if [[ "$2" != "no header" ]] ; then
        id3edit --create \
                --set-name "$name" \
                --set-album "$album" \
                --set-artist "$artist" \
                --set-artwork "$albumpath/artwork.jpg" \
                --set-release "$release" \
                --set-track "$track" \
                --set-cd "$cd" \
                "$songpath"
    fi

    echo -e "\e[u\e[1;32m✔"
}

# Create Directory
mkdir -p "$albumpath"

# Add Artwork
echo -e -n "\e[1;37m[\e[s ]\e[1;34m Creating $albumpath/artwork.jpg\e[0m"
cp ../share/default.jpg "$albumpath/artwork.jpg"
echo -e "\e[u\e[1;32m✔"

# Add Songs
CreateSong "01" "5" "Song Number 1"
CreateSong "02" "5" "これはテストです"
CreateSong "03" "5" "A 💩 Test Song"
CreateSong "04" "5" "Non conform file name" "Non conform file name"
CreateSong "05" "no header" "No ID3 Tag"

# Create booklet
echo -e -n "\e[1;37m[\e[s ]\e[1;34m Creating $albumpath/booklet.pdf\e[0m"
convert "$albumpath/artwork.jpg" "$albumpath/booklet.pdf"
echo -e "\e[u\e[1;32m✔"

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

