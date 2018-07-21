#!/usr/bin/env bash

function InstallID3Edit {

    _ExpectingTool git

    HERE=$(pwd)

    # install libprinthex
    echo -e -n "\e[1;34mInstalling \e[0;36mlibprinthex\e[1;34m: "
    if [ ! -f /usr/local/lib/libprinthex.a ] ; then
        _ExpectingTool gcc

        cd /tmp
        echo -e "\e[1;30m"
        git clone https://github.com/rstemmer/libprinthex.git
        cd libprinthex
        ./build.sh
        ./install.sh
        cd /tmp
        rm -r libprinthex
        echo -e "\e[1;32mdone"
    else
        echo -e "\e[1;37malready done!"
    fi

    cd $HERE

    # install id3edit
    echo -e -n "\e[1;34mInstalling \e[0;36mid3edit\e[1;34m: \e[1;31m"
    local INSTALLID3EDIT="False"
    if ! type id3edit 2> /dev/null > /dev/null ; then
        INSTALLID3EDIT="True"
    else
        # check if the already installed version is up to date
        local BIN_MAJOR=$(id3edit --version | cut -d "." -f 1)
        local BIN_MINOR=$(id3edit --version | cut -d "." -f 2)
        local BIN_PATCH=$(id3edit --version | cut -d "." -f 3)

        local SRC_MAJOR=$(grep "#define VERSION" ./../id3edit/main.c | cut -d " " -f 3 | tr -d \" | cut -d "." -f 1)
        local SRC_MINOR=$(grep "#define VERSION" ./../id3edit/main.c | cut -d " " -f 3 | tr -d \" | cut -d "." -f 2)
        local SRC_PATCH=$(grep "#define VERSION" ./../id3edit/main.c | cut -d " " -f 3 | tr -d \" | cut -d "." -f 3)

        if [ $SRC_MAJOR -gt $BIN_MAJOR ] ; then
            INSTALLID3EDIT="True"
        elif [ $SRC_MAJOR -eq $BIN_MAJOR ] ; then
            if [ $SRC_MINOR -gt $BIN_MINOR ] ; then
                INSTALLID3EDIT="True"
            elif [ $SRC_MINOR -eq $BIN_MINOR ] ; then
                if [ $SRC_PATCH -gt $BIN_PATCH ] ; then
                    INSTALLID3EDIT="True"
                fi
            fi
        fi
    fi


    if [ "$INSTALLID3EDIT" == "True" ] ; then
        _ExpectingTool clang

        cd id3edit
        ./build.sh
        ./install.sh
        echo -e "\e[1;32mdone"
    else
        echo -e "\e[1;37malready done!"
    fi

    cd $HERE
}



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

