#!/usr/bin/env bash

set -e

VersionFile="../VERSION"

# 1. Read versions
MusicDBVersion=$(grep MusicDB $VersionFile | cut -d ":" -f 2 | tr -d " ")
WebUIVersion=$(grep WebUI $VersionFile | cut -d ":" -f 2 | tr -d " ")

echo -e "\e[1;34mUpdateing version numbers"
echo -e "\e[1;34m\tMusicDB: \e[0;35m\"\e[1;35m${MusicDBVersion}\e[0;35m\""
echo -e "\e[1;34m\tWebUI:   \e[0;35m\"\e[1;35m${WebUIVersion}\e[0;35m\""


echo -e "\e[1;34mUpdateing\e[0;36m musicdb.py\e[0m"
sed -i "/VERSION = \"*\"/cVERSION = \"${MusicDBVersion}\"" ../musicdb/musicdb.py

echo -e "\e[1;34mUpdateing\e[0;36m AboutMusicDB.js\e[0m"
sed -i "/const MUSICDB_VERSION/cconst MUSICDB_VERSION = \"${MusicDBVersion}\";" ../webui/js/views/AboutMusicDB.js
sed -i "/const WEBUI_VERSION/cconst WEBUI_VERSION = \"${WebUIVersion}\";" ../webui/js/views/AboutMusicDB.js

echo -e "\e[1;34mUpdateing\e[0;36m conf.py\e[0m"
sed -i "/release = /crelease = \'${MusicDBVersion}\'" ../docs/source/conf.py
sed -i "/version = /cversion = \'${MusicDBVersion:0:3}\'" ../docs/source/conf.py

echo -e "\e[1;34mUpdateing\e[0;36m PKGBUILD\e[0m"
sed -i "/pkgver=/cpkgver=${MusicDBVersion}" ../dist/PKGBUILD

echo -e "\e[1;34mUpdateing\e[0;36m musicdb.spec\e[0m"
sed -i "/Version: /cVersion:    ${MusicDBVersion}" ../dist/musicdb.spec

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

