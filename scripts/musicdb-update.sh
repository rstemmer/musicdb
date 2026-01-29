#!/usr/bin/env bash

systemctl stop musicdb && pacman -U ../pkg/musicdb-8.2.0-1-any.pkg.tar.zst && systemctl start musicdb

