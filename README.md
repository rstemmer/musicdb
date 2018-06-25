![MusicDB Logo](https://rstemmer.github.io/musicdb/landingpage/img/logo.png)

# MusicDB

MusicDB is a music manager with focus on remote access to your music using a WebUI
an audio stream.
The WebUI is more a presentation of your music than a database frontend.

So, when you are listening to music, you do not work with software.
Instead you explore your music collection.

**For more details, a list of features and screenshots see the start page [rstemmer.github.io/musicdb/](https://rstemmer.github.io/musicdb/index.html).**

---

Until now I spent over 6 years for developing this awesome software.
Since I finished a first test version, I use it nearly every day.
Time to share it with the world. :smiley:

For news, follow [@MusicDBProject](https://twitter.com/MusicDBProject) on Twitter.


## This is MusicDB

The following image shows a complete overview of MusicDB and its connections to other software.
It shows the flow of our music and the related information (purple) from the source music collection (bottom left) to the Web Browser and Audio Player.

![MusicDB Overview](https://rstemmer.github.io/musicdb/build/html/basics/overview.html)

A detailed description of this overview image and MusicDB's components can be found in the documentation: [Description of the Image ](https://rstemmer.github.io/musicdb/build/html/basics/overview.html)


## Breaking News

This section contains some important information on how to update to a next major version.
Major releases have changes that are not compatible to the previous version of MusicDB.
Furthermore those changes may break scripts you wrote around MusicDB.

Lines starting with "**:wrench: Change:**" are steps you have to do *before* updating via `install.sh` script.

### xx.07.18: 3.x.x → 4.0.0+

* More stable CSV files by adding a header. Now updating the old CSV files is possible
  * **:wrench: Change:** Remove the old CSV-Files from the *mdbstate* directory. (You'll loose the current song queue and blacklist state)

### 06.05.18: 2.x.x → 3.0.0+

* Two new columns added to the database: `checksum` and `lastplayed`
  * **:wrench: Change:** After *installing via install.sh* execute [:notebook: repair](https://rstemmer.github.io/musicdb/build/html/mod/repair.html) with `--checksums` option (`musicdb repair --checksums`) to fill the new added checksum column.
  * The date a song was last played is currently shown in the tooltip when hovering the cursor above a song in the Album-View.
* I replaced the MPD backend with an own [Icecast](https://icecast.org/) Source Client
  * Transcoding is done by [GStreamer](https://gstreamer.freedesktop.org/)
  * **:wrench: Change:** New dependencies: gstreamer, gst-python and the good+bad GStreamer plugins
  * **:wrench: Change:** The install script creates a new directory in the MusicDB data directory called `icecast`. Make sure that such a directory does not exist before running `install.sh`. If it does, rename it, and merge your setup after the installation.
  * **:wrench: Change:** The `[mpd]` section can be removed from the MusicDB Configuration
* MusicDB's state now gets stored with the blacklists and song queue in an extra directory.
  * The directory can be configured: `[server] -> statedir`
* **:wrench: Change:** New `musicdb.ini` file will be installed as `musicdb.ini.new` - check the differences.

**:wrench: Update:**
```sh
# Backup the MusicDB Data directory!

# Download latest version of MusicDB
git checkout master
git pull

# Install latest version of MusicDB
sudo pacman -S gst-plugins-good gst-python gst-plugins-bad
sudo ./install.sh

# Read the linked documentation of the repair module

# Update old data
newgrp musicdb
musicdb repair --checksums
```

### 05.01.18: 1.x.x → 2.0.0+

* Signals got replaced by a named pipe
  * New configuration: `[server] -> fifofile=DATADIR/musicdb.fifo`
  * Communication with the server via signals (`SIGTERM`, `SIGUSR1`) is deprecated. Use the named pipe instead. (Commands: `"shutdown"`, `"refresh"`)
  * [:notebook: Details and examples](https://rstemmer.github.io/musicdb/build/html/mdbapi/server.html)
  * **:wrench: Change:** Add the new configuration (`[server] -> fifofile=DATADIR/musicdb.fifo`) into your ini file

* [:notebook: database](https://rstemmer.github.io/musicdb/build/html/mod/database.html) module updated
  * *target* parameter removed. Target gets determined by its path.
  * `update` command removed. Use the [:notebook: repair](https://rstemmer.github.io/musicdb/build/html/mod/repair.html) module for updating paths.
  * `remove` command added.


## Social

Providing and maintaining open source software comes with some downsides.
I'd like to know if anyone is using this software, and what you are doing with it. :smiley:

So feel free to follow my project account [@MusicDBProject](https://twitter.com/MusicDBProject) on Twitter
and share some screenshots :wink:

In case you find any bugs, please create an Issue.
Feature requests are welcome as well.


# Using MusicDB

This section describes how to install, update and use MusicDB.

## Requirements

I only test with the latest version of the requirements I list below.
If MusicDB breaks when updating dependencies, it's a bug in MusicDB.
In case MusicDB does not run on outdated operating systems, update your system ;)

* A Linux operating system. Tested with:
  * [Arch Linux](https://www.archlinux.org/) for x86-64 (primary test and development system)
  * [Debian](https://www.debian.org/distrib/) for x86-64 (not recommended because it comes with lots of ~~old~~ "stable" software)
  * [Arch Linux ARM](https://archlinuxarm.org/) for AArch64 with [ODROID-C2](https://wiki.odroid.com/odroid-c2/odroid-c2)
  * [Arch Linux ARM](https://archlinuxarm.org/) for ARMv7 with [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
* [Python3](https://www.python.org/) (I test with Python 3.6)
* [Icecast](https://icecast.org/) and [GStreamer](https://gstreamer.freedesktop.org/) for streaming
* A modern web browser for accessing the WebUI:
  * [Firefox](https://www.mozilla.org/en-US/) (recommended)
  * [Chrome](https://www.google.com/chrome/index.html) 
  * [Opera](https://www.opera.com/)
* An Unicode capable file system (Any *modern* file system should work)
* A terminal that supports Unicode, with an Unicode capable font configured (I use KDE's [Konsole](https://www.kde.org/applications/system/konsole/) with [Hack](https://sourcefoundry.org/hack/))

The `install.sh` script checks for tools needed to install MusicDB.
Furthermore `musicdb-check.sh` list all tools and Python modules needed by MusicDB.
You can run the check-script at any time. 

Execute `pip install -r requirements.txt` to install a basic set of Python modules needed for MusicDB.


## Download

To get the latest version of MusicDB, clone this repository.
The *master* branch can be considered stable.

```sh
git clone https://github.com/rstemmer/musicdb.git
```


## Installation and Update

To install MusicDB, read [:notebook: How to Install MusicDB](https://rstemmer.github.io/musicdb/build/html/usage/install.html) in the documentation.

For updating, you can also execute the `install.sh` script.
Read the *Breaking News* for manual steps to do before updating to a new major release.

Updating to the next minor version can be done by simply executing `git pull && ./quickupdate.sh` (Be sure you are on the master branch).


## Usage

The start page of [:notebook: MusicDB's Documentation](https://rstemmer.github.io/musicdb/build/html/index.html)
should give you the help you need to start - or at least the links to the chapters they do
(like the [:notebook: CLI MODULES chapters)](https://m45ch1n3.de/musicdb/docs/build/html/index.html#musicdb-cli).
The documentation is made for developers, not only users. So there is much more information than you will need to use MusicDB.


In general, the first steps are the following, after you have done the [:notebook: First Run](https://rstemmer.github.io/musicdb/build/html/usage/install.html#first-run):

1. [:notebook: Add Music](https://rstemmer.github.io/musicdb/build/html/usage/music.html#importing-albums-to-musicdb) to MusicDB
2. [:notebook: Create Genres](https://rstemmer.github.io/musicdb/build/html/mod/genres.html) and sub-genres you want to use to categorize your Music.
3. [:notebook: Create Moods](https://rstemmer.github.io/musicdb/build/html/mod/moods.html) you want to assign to your songs.
4. Open the WebUI in your browser and tag the albums with the genres you created. (Right click on the albums title in the Album View). Then the random song selection process can start working and stops printing warnings.


Some helpful hints:

* For security reasons, MusicDB only accepts connections from localhost by default. Change the [:notebook: WebSocket address configuration](https://rstemmer.github.io/musicdb/build/html/basics/config.html#websocket) to access your music from anywhere.
* Don't be to specific with the genre tags. Tag albums beforehand and songs only when they are currently playing.
* Set mood-flags only for the current playing song.
* Check the [:notebook: Configuration of Randy](https://rstemmer.github.io/musicdb/build/html/basics/config.html#randy) to make sure the random song selection can work with your music collection. When you have a small music collection, decrease the blacklist sizes.


If there are any problems setting up MusicDB, create an issue.


# Development

This section describes how to contribute to this project.


## Documentation

The [:notebook: MusicDB Documentation](https://rstemmer.github.io/musicdb/build/html/index.html) is a good point to start.
There are all concepts, interfaces and details described.

Most important will be the [:notebook: Quick Start Section](https://rstemmer.github.io/musicdb/build/html/index.html#quick-development-start) that points out some chapters to start reading.


## Contributing

Every help is welcome.


### What you can do

* Create an Issue when you find a bug.
* Improve the documentation.
* Suggesting features via Issue.
* See if there is an Issue you are able to fix, or to give hints on how to fix it.
* Fix bugs or add features.


### Before you change code

* Read [:notebook: Working on MusicDB's Code](https://rstemmer.github.io/musicdb/build/html/basics/workflow.html)
* … and [:notebook: Philosophy of MusicDB](https://rstemmer.github.io/musicdb/build/html/basics/concept.html)
* Branch from *master*.
* Please don't commit *docs/build*,


# Versioning and Branches

I work on MusicDB in three sprints per year. Each sprint is about one and a half week long.
The rest of the year I only want to concentrate on fixing critical bugs.

There are no classic releases. The MusicDB core has some kind of version number (see VERSION file),
but this number does not cover changes in the WebUI, for example.

A reliable change log can be generated by calling `git log --oneline`. :wink:

It is also recommended to update whenever there are changes on *master*.
You better not use any other branch than *master*. :wink:

**Best dates for updating MusicDB are end of January, end of May and end of September.**

Major "releases" are not compatible with the previous version of MusicDB.
How to update to a next major version will be described in the *Breaking News* section at the beginning of this README.

The following subsections describe the branches the MusicDB git repository contains.

## master branch

This is the main branch and contains the latest stable version of MusicDB.
This is the version you should install.
If you want to do some changes to the code, you should branch from this branch.

## develop branch

This branch is the branch I'm working on. It may contain incomplete features and untested code.
If there you have trouble with the master branch, and the git log promises a solution to that problem, 
you can try using this branch.

When there are lots of commits that are not yet merges with master, you should be very careful.
I also do not guarantee that this branch is compatible with the current master branch.
Make a backup of your MusicDB data directory before using installing MusicDB from this branch.

## mobileapp branch

I'm working on a mobile app that downloads your whole music collection via WLAN onto your smartphone.
It is still very experimental and not ready to use.
For the app, I use the [kivy](https://kivy.org/#home) framework.

Target will only be Android smartphones due to the storage limitation of iOS based devices.

## GitHub Releases

Some special old releases are tagged in the git repository.
They can be found in [GitHubs Releases Section](https://github.com/rstemmer/musicdb/releases).
These are not the latest version of MusicDB and I do not recommend to use them.

