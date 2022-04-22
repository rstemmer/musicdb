#!/usr/bin/env bash

systemctl stop musicdb && pacman -U ../pkg/musicdb-8.1.0-1-any.pkg.tar.zst && systemctl start musicdb

