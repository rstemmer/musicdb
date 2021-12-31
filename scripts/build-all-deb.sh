#!/usr/bin/env bash

rm -f ../dist/musicdb-8.0.0-src.tar.zst && ./src-build.sh
./deb-build.sh

