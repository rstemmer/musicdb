![MusicDB Logo](graphics/MusicDB/mdblogo.png?raw=true)

# MusicDB

MusicDB is a music manager with focus on remote access to your music collection using a WebUI.
It allows you to manage an audio stream based on a song-queue.
The WebUI is focusing on being a presentation of your music rather than being a database frontend.

So, when you are listening to your music, you do not work with software.
Instead you explore your music collection.

I started this project on 4th January 2014.
Since I finished a first test version, I use it nearly every day.
Time to share it with the world. :smiley:

**For more details, a list of features and screenshots see the start page [rstemmer.github.io/musicdb/](https://rstemmer.github.io/musicdb/index.html).**

A detailed description of MusicDB and its components can be found in the documentation: [Overview of MusicDB](https://rstemmer.github.io/musicdb/build/html/basics/overview.html)

For news, follow [@MusicDBProject](https://twitter.com/MusicDBProject) on Twitter.

## Table of Contents

* [MusicDB](#musicdb)
  * [Table of Contents](#table-of-contents)
  * [Important News](#important-news)
  * [Social](#social)
* [Using MusicDB](#using-musicdb)
  * [Requirements](#requirements)
  * [Download](#download)
  * [Installation and Update](#installation-and-update)
  * [Usage](#usage)
* [Development](#development)
  * [Documentation](#documentation)
  * [Contributing](#contributing)
* [Roadmap](#roadmap)
  * [Branches](#branches)
  * [Releases](#releases)


## Important News

This section contains some important information on how to update to a next major version.
Major releases have changes that are not compatible to the previous version of MusicDB.
Furthermore those changes may break scripts you wrote around MusicDB.

Lines starting with "**:wrench: Change:**" are steps you have to do *before* or *after* updating via `install.sh` script.

**01.08.2020: 5.x.x → 6.0.0+**

* Changes in the configuration file and music database (See CHANGELOG for details)
  * **:wrench: Change:** Remember to call `musicdb upgrade` *after* installation when using the `update.sh` script
  * **:wrench: Change:** Reload WebUI *after* update
* MusicAI will no longer work. Everything related to MusicAI got removed. Reason: The used framework _tflearn_ is no longer under development and got not ported to TensorFlow 2.0.

<details>
<summary> 20.01.2019: 4.x.x → 5.0.0+ </summary>

* Some changes in the configuration file
  * **:wrench: Change:** Remember to call `musicdb upgrade` *after* installation when using the `update.sh` script
* Blacklists and songqueue files in the MusicDB state directory got additional columns
  * They will be automatically upgraded by MusicDB without any information loss
* Changes in the WebUI
  * **:wrench: Change:** Reload WebUI *after* update (Clear cache if necessary)

</details>

<details>
<summary> 28.07.2018: 3.x.x → 4.0.0+ </summary>

* Rebuild of the installation process.
  * **:wrench: Change:** Make a backup of the MusicDB data directory!
  * Do not use the update script to update to this version (4.0.0). Use the `install.sh` script!
* More stable CSV files by adding a header. Now updating the old CSV files is possible
  * **:wrench: Change:** Remove the old CSV-Files from the `mdbstate` directory. (You'll loose the current song queue and blacklist state)
* WebSocket configuration for WebUI is now in separate `webui/config.js`
  * **:wrench: Change:** You may want to backup the settings `from webui/js/musicdb.js`
* The server now only accepts request from clients with a valid API Key
* Databases now have a version number to allow easy updated.
  * **:wrench: Change:** This is the last time you have to touch the databases by yourself. For each database:
    * ``sqlite $DATABASE.db`` (With DATABASE = ``music``, ``lycra``, ``tracker``)
    * ``CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, VALUE TEXT DEFAULT '');``
    * ``INSERT INTO meta (key, value) VALUES ("version", 2);``
    * ``.quit``
* **:wrench: Change:** Restore your configuration
  * Update the icecast passwort (`musicdb.ini` ↔ `icecast/config.xml`)
  * Update the WebSocket API Key (`musicdb.ini` ↔ `../server/webui/config.js`)

</details>


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
In case MusicDB does not run on outdated operating systems, update your system :wink:

* A Linux operating system. Tested with:
  * [Arch Linux](https://www.archlinux.org/) for x86-64 (primary test and development system)
  * [Debian](https://www.debian.org/distrib/) for x86-64 (not recommended because it comes with lots of ~~old~~ "stable" software)
  * [Arch Linux ARM](https://archlinuxarm.org/) for AArch64 with [ODROID-C2](https://wiki.odroid.com/odroid-c2/odroid-c2)
  * [Arch Linux ARM](https://archlinuxarm.org/) for ARMv7 with [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
* [Python3](https://www.python.org/) (At least Python 3.5. I test with Python 3.8)
* [Icecast](https://icecast.org/) and [GStreamer](https://gstreamer.freedesktop.org/) for streaming
* A modern web browser for accessing the WebUI:
  * [Firefox](https://www.mozilla.org/en-US/) (recommended)
  * [Chrome](https://www.google.com/chrome/index.html) 
  * [Opera](https://www.opera.com/)
* An Unicode capable file system (Any *modern* file system should work)
* A terminal that supports Unicode, with an Unicode capable font configured (I use KDE's [Konsole](https://www.kde.org/applications/system/konsole/) with [Hack](https://sourcefoundry.org/hack/))

The `install.sh` script checks for tools needed to install MusicDB.
Furthermore `check.sh` list all tools and Python modules needed by MusicDB.
You can run the check-script at any time. 

A detailed list can be found on [:notebook: How to Install MusicDB](https://rstemmer.github.io/musicdb/build/html/usage/install.html) in the documentation.


Execute `pip install -r requirements.txt` to install a basic set of Python modules needed for MusicDB.
I recommend to try to get the modules from the distributions package manager.

You should use the latest versions of these dependencies and update them regularly.
When MusicDB breaks because of an updated dependency create a ticket.
I then will fix MusicDB as soon as possible.


## Installation and Update

### Installation of MusicDB

To install MusicDB, read [:notebook: How to Install MusicDB](https://rstemmer.github.io/musicdb/build/html/usage/install.html) in the documentation.

### Update to a New Version

For updating, you can do following steps.
Read the *Important News* for manual steps to do before updating to a new major release.
Only execute the scripts as root, that are followed by the comment "as root"!

``` bash
git checkout master # Only install from master branch!
git pull

cd scripts
./update.sh # as root
```


## Download

To get the latest version of MusicDB, clone this repository.
The *master* branch can be considered stable.

```sh
git clone https://github.com/rstemmer/musicdb.git
```

## Usage

The start page of [:notebook: MusicDB's Documentation](https://rstemmer.github.io/musicdb/build/html/index.html)
should give you the help you need to start - or at least the links to the chapters that do
(like the [:notebook: CLI MODULES chapters)](https://m45ch1n3.de/musicdb/docs/build/html/index.html#musicdb-cli).
The documentation is made for developers, not only users. So there is much more information than you will need to use MusicDB.


In general, the first steps are the following, after you have done the [:notebook: First Run](https://rstemmer.github.io/musicdb/build/html/usage/install.html#first-run):

1. [:notebook: Add Music](https://rstemmer.github.io/musicdb/build/html/usage/music.html#importing-albums-to-musicdb) to MusicDB
2. [:notebook: Create Genres](https://rstemmer.github.io/musicdb/build/html/mod/genres.html) and sub-genres you want to use to categorize your Music.
3. [:notebook: Create Moods](https://rstemmer.github.io/musicdb/build/html/mod/moods.html) you want to assign to your songs.
4. Open the WebUI in your browser and tag the albums with the genres you created. (Right click on the albums title in the Album View). Then the random song selection process can start working and stops printing warnings.


Some helpful hints:

* For security reasons, MusicDB only accepts connections from localhost by default. Change the [:notebook: WebSocket address configuration](https://rstemmer.github.io/musicdb/build/html/basics/config.html#websocket) to access your music from anywhere.
* Don't be to specific with the genre tags. Define only one tag per genre like *Metal*, *Pop*, *Classic*, …
* Use sub-genre tags for a more detailed classification.
* Tag albums beforehand and songs only when they are currently playing.
* Set mood-flags only for the current playing song.
* Check the [:notebook: Configuration of Randy](https://rstemmer.github.io/musicdb/build/html/basics/config.html#randy) to make sure the random song selection can work with your music collection. When you have a small music collection, decrease the blacklist sizes.
* In the Album-View panel, right click on the album title opens a panel for tagging and defining a color scheme for the album.
* Right click on a song name inside the Album-View allows detailed tagging and pre"view"ing a song.
* When defining the Album-View colors, pay attention to good contrast and follow the color scheme of the album cover.


If there are any problems setting up MusicDB, create an issue.


## Docker-Based Demo

It is possible to run a *Demo* installation via Docker container.
Just clone this repository and execute the scripts in the docker sub-directory.

```sh
git clone https://github.com/rstemmer/musicdb.git
cd musicdb
./docker/build.sh
./docker/run.sh
```

**Important:** I do not longer support docker and will no longer update or test the files in the docker directory.
I let the scripts untouched as they were for version 5.2.2.
In case they do not work with later versions of MusicDB please create an Issue.


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


# Roadmap

*MusicDB* is under active development.
Beside maintaining this software, I also think about improving it or adding new features if necessary.
The following list contains all huge improvements I'm planning to add to MusicDB.

* Integrate music videos into the MusicDB infrastructure. The UI should be switch to video-mode. Then, instead of showing artists and their albums, artists and their videos will be shown. The videos can then be put into a video-queue that get streamed.
  * A first prototype exists in the *feature-video* branch.
  * Development progress can be seen on the [corresponding GitHub Project page](https://github.com/rstemmer/musicdb/projects/1).


* Next generation of *MusicAI*. I already miss the old one that was surprisingly helpful tagging songs. The next generation might base on TensorFlow 2.0 directly. I will have the same or similar architecture since it worked in the past.

* New Frontend. Early ideas are around WebAssembly based technology or a native client. Even with a native client the WebUI still needs to be updated. The code base is very ugly and the used coding strategy does not fit to the complexity of the application and abilities of JavaScript.

The following subsections cover more information regarding releases and branches.

## Branches


The following branches exist in the MusicDB git repository contains.

<details>
<summary> master - Ready to Use </summary>

This is the main branch and contains the latest stable version of MusicDB.
This is the version you should install.
If you want to do some changes to the code, you should branch from this branch.

</details>

<details>
<summary> develop - Work in Progress </summary>

This branch is the branch I'm working on. It may contain incomplete features and untested code.
If there you have trouble with the master branch, and the git log promises a solution to that problem, 
you can try using this branch.

When there are lots of commits that are not yet merges with master, you should be very careful.
I also do not guarantee that this branch is compatible with the current master branch.
Make a backup of your MusicDB data directory before using installing MusicDB from this branch.

</details>

<details>
<summary>feature-???</summary>

These branches are for adding *game-changing* features into MusicDB.
They are not strictly bound to a release.
It is not even clear if the features will be finished at all.

Do never use code from this branch in production!

</details>

<details>
<summary> mobileapp - The mobile app is dead </summary>

I started to build a tiny mobile app that downloads your whole music collection via WLAN onto your smartphone.
For the app, I use the [kivy](https://kivy.org/#home) framework.

There were so many problems with the framework and the build environment that I canceled the development.
For example, I had to use Python 2 because there was no SSL support for Python 3 included.
The build environment used proprietary 32bit executables and may more problems like that.

</details>


## Releases

With version 5.0.0 I started to use the Releases feature of GitHub.
They can be found in [GitHubs Releases Section](https://github.com/rstemmer/musicdb/releases).
Some special old releases are tagged in the git repository as well.


