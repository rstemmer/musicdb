#!/usr/bin/env bash

echo -e "\e[1;31mMusicDB-Check [\e[1;34m2.2.0\e[1;31m]\e[0m"

if [ $EUID -eq 0 ]; then
    echo -e "\e[1;33mYou shoud NOT have root permissions. MusicDB will not have them, too"
    exit 1
fi

function CheckBinaryExistence
{
    if ! type "$1" 2> /dev/null > /dev/null ; then
        if [ "$2" == "opt" ] ; then
            echo -e "\e[1;33m [✗] \033[0;33mProgram \e[0;36m$1\e[0;33m does not exist (optional)\e[0m"
        elif [ "$2" == "inc" ] ; then
            echo -e "\e[1;33m [✗] \033[0;33mProgram \e[0;36m$1\e[0;33m does not exist \e[0;32m(Will be automatically installed)\e[0m"
        else
            echo -e "\e[1;31m [✗] \033[0;31mProgram \e[0;33m$1\e[0;31m does not exist\e[0m"
        fi
        return 1
    else
        echo -e "\e[1;32m [✓] \033[0;32mProgram \e[0;36m$1\e[0;32m exists\e[0m"
        return 0
    fi
}

function CheckPythonModuleExistence
{
    if ! $(python3 -c "import $1" &> /dev/null) ; then
        if [ "$2" == "opt" ] ; then
            echo -e "\e[1;33m [✗] \033[0;33mPython module \e[0;36m$1\e[0;33m does not exist (optional)\e[0m"
        elif [ "$2" == "req" ] ; then
            echo -e "\e[1;33m [✗] \033[0;33mPython module \e[0;36m$1\e[0;33m does not exist \e[0;32m(included in requirements.txt)\e[0m"
        else
            echo -e "\e[1;31m [✗] \033[0;31mPython module \e[0;33m$1\e[0;31m does not exist\e[0m"
        fi
        return 1
    else
        echo -e "\e[1;32m [✓] \033[0;32mPython module \e[0;36m$1\e[0;32m exists\e[0m"
        return 0
    fi
}

echo -e "\e[1;34mChecking programs …"
CheckBinaryExistence "python"
CheckBinaryExistence "icecast"
echo -e "\e[1;37m [!] \033[0;33mPlease check if the latest \e[0;36mlibshout\e[0;33m is installed.\e[0m"
CheckBinaryExistence "gst-inspect-1.0" opt
echo -e "\e[1;37m [!] \033[0;33mPlease check if all latest \e[0;36mGStreamer Plugins\e[0;33m are installed.\e[0m"
echo -e "\e[1;37m [!] \033[0;33mPlease check if the latest \e[0;36mpython-gst\e[0;33m module is installed.\e[0m"
CheckBinaryExistence "id3edit"   opt
CheckBinaryExistence "clang"     opt    # To compile id3edit
CheckBinaryExistence "ffmpeg"
CheckBinaryExistence "apachectl" opt    # other servers are also possible
CheckBinaryExistence "openssl"
CheckBinaryExistence "sqlite3"
CheckBinaryExistence "rsync"        # for source update
CheckBinaryExistence "latex" opt    # for documentation
CheckBinaryExistence "jsdoc" opt    # for documentation
CheckBinaryExistence "dialog"       # for installation script

echo -e "\e[1;34mChecking python modules …"
CheckPythonModuleExistence "gi"
CheckPythonModuleExistence "sqlite3"
CheckPythonModuleExistence "gzip"
CheckPythonModuleExistence "configparser"
CheckPythonModuleExistence "json"
CheckPythonModuleExistence "csv"
CheckPythonModuleExistence "pyquery" opt    # useful for lyrics crawler
CheckPythonModuleExistence "hashlib"
CheckPythonModuleExistence "mutagenx"    req
CheckPythonModuleExistence "Levenshtein" req
CheckPythonModuleExistence "fuzzywuzzy"  req
CheckPythonModuleExistence "unicodedata"
CheckPythonModuleExistence "asyncio"
CheckPythonModuleExistence "autobahn.asyncio.websocket" req
CheckPythonModuleExistence "PIL"         req # aka pillow
CheckPythonModuleExistence "tqdm"        req
CheckPythonModuleExistence "sphinx" opt     # for documentation
CheckPythonModuleExistence "sphinx-js" opt  # for documentation


# for documentation
# sphinx
# sphinxcontrib-autojs
# sphinxcontrib-autoprogram

exit 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

