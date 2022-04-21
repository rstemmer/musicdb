#!/usr/bin/env bash

find . -type f -name "*.js" -exec sed -i 's/MusicDB_Broadcast/MusicDB\.Broadcast/g' {} \;

