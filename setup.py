#!/usr/bin/env python3
# The line above is necessary so that debmake can identify setup.py packages python 3 software

import setuptools
import os
import sys

#SOURCEDIR=setuptools.convert_path(".")
SOURCEDIR=os.path.dirname(__file__)
if not SOURCEDIR:
    SOURCEDIR = "."

def ReadVersion():
    versionpath = SOURCEDIR + "/VERSION"
    with open(versionpath, "r") as versionfile:
        firstline = versionfile.readline()

    version = firstline.split("-")[0].strip()
    return version


def ReadReadme():
    path = os.path.join(SOURCEDIR, "README.md")
    with open(path, "r") as fh:
        readme = fh.read()

    return readme


setuptools.setup(
        name            = "musicdb",
        version         = ReadVersion(),
        #version         = "8.0.0",
        author          = "Ralf Stemmer",
        author_email    = "ralf.stemmer@gmx.net",
        description     = "A music manager with web-bases UI that focus on music",
        long_description= ReadReadme(),
        long_description_content_type   = "text/markdown",
        url             = "https://github.com/rstemmer/musicdb",
        project_urls    = {
            "Documentation": "https://rstemmer.github.io/musicdb/build/html/index.html",
                "Source":  "https://github.com/rstemmer/musicdb",
                "Tracker": "https://github.com/rstemmer/musicdb/issues",
            },
        packages        = setuptools.find_packages(),
        entry_points={
                "console_scripts": [
                    "musicdb=musicdb.musicdb:main",
                    ],
                },
        package_data={
            },
        install_requires= [
            "autobahn",
            "mutagen",
            "python-Levenshtein",
            "fuzzywuzzy",
            "pillow",
            "tqdm"
            ],
        python_requires = ">=3.8",
        keywords        = "music streaming cloud music-player music-library music-collection music-streaming music-manager streaming-audio musicdb",
        license         = "GPL",
        classifiers     = [
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: POSIX :: Linux",
            "Environment :: Console",
            "Environment :: Web Environment",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Intended Audience :: Information Technology",
            "Topic :: Communications",
            "Topic :: Database",
            "Topic :: Internet",
            "Topic :: Multimedia",
            "Topic :: Multimedia :: Sound/Audio",
            "Topic :: Scientific/Engineering",
            "Topic :: Utilities",
            ],
        )

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

