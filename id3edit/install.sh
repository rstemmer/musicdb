#!/bin/bash

INSTALLPATH=/usr/local/bin

for SOURCE in id3edit id3show id3frames id3dump ; do
    install -m 755 -v -g root -o root $SOURCE $INSTALLPATH
done

strip $INSTALLPATH/id3edit


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

