#!/usr/bin/env bash

WebUICSS="WebUI.css"
WebUIJS="WebUI.js"
IndexHTML="debug.html"
VersionFile="../VERSION"
MusicDBVersion=$(grep MusicDB $VersionFile | cut -d ":" -f 2 | tr -d " ")
WebUIVersion=$(grep WebUI $VersionFile | cut -d ":" -f 2 | tr -d " ")


function RepairPaths
{
     sed -i 's,url("\.\.,url("\.,g' "$1"    # url("..   -> url(".
     sed -i 's,url(\.\.,url(\.,g' "$1"      # url(..    -> url(.
     sed -i 's,url("\./\.\.,url("\.,g' "$1" # url("./.. -> url(".
     sed -i 's,url(\./\.\.,url(\.,g' "$1"   # url(./..  -> url(.
}

function BuildCSS
{
     local CSSFiles=$(grep "stylesheet" "$IndexHTML" | cut -d "\"" -f 4)

     echo -e "/* Merged CSS File of WebUI $WebUIVersion */\n" > $WebUICSS

     for CSSFile in $CSSFiles
     do
         echo -e "\e[1;35m + \e[1;34m$CSSFile\e[0m"
         echo "/* Source File: $CSSFile */" >> "$WebUICSS"
         cat "$CSSFile" >> "$WebUICSS"
     done

     RepairPaths "$WebUICSS"
}



function BuildJS
{
     local JSFiles=$(grep "script src" "$IndexHTML" | grep -v "webdata" | cut -d "\"" -f 2)

     echo -e "/* Merged CSS File of WebUI $WebUIVersion */\n" > $WebUIJS

     for JSFile in $JSFiles
     do
         echo -e "\e[1;35m + \e[1;34m$JSFile\e[0m"
         echo "/* Source File: $JSFile */" >> "$WebUIJS"
         cat "$JSFile" >> "$WebUIJS"
     done

     RepairPaths "$WebUIJS"
}


BuildCSS
BuildJS

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 

