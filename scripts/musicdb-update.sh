#!/usr/bin/env bash

systemctl stop musicdb && pacman -U ../dist/musicdb-8.0.0-1-any.pkg.tar.zst && systemctl start musicdb

