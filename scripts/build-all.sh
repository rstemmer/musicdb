#!/usr/bin/env bash

rm -f ../dist/musicdb-8.0.0-src.tar.zst && ./src-build.sh
rm -f ../dist/musicdb-8.0.0-1-any.pkg.tar.zst && ./pkg-build.sh

