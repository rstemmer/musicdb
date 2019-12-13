#!/usr/bin/env bash

set -e

httpd
/opt/musicdb/server/musicdb-boot.sh
/opt/musicdb/server/musicdb-start.sh &

