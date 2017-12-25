#!/bin/bash

SOURCE=$(find . -type f -name "*.c")
#HEADER="-I. -I./libid3v2/include -I./libid3v2/include/id3v2lib"
HEADER="-I."
LIBS="-lprinthex"

for c in $SOURCE ;
do    
    echo -e "\e[1;34mCompiling $c …\e[0m"
    clang -DxDEBUG -g -Wno-multichar --std=gnu99 $HEADER -O2 -g -c -o "${c%.*}.o" $c
    #if [[ $? -ne 0 ]] ; then
    #    echo -e "\e[1;31mfailed\e[0m"
    #else
    #    echo -e "\e[1;32mdone\e[0m"
    #fi
done


OBJECTS=$(find . -type f -name "*.o")

clang -o id3edit $OBJECTS $LIBS

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

