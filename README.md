
<p align="center">
  <a href="https://github.com/rstemmer/musicdb/releases">
    <img src="https://img.shields.io/github/release/rstemmer/musicdb.svg" alt="MusicDB releases"/>
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"/>
  </a>
  <a href="https://github.com/rstemmer/musicdb/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/License-GPLv3-green.svg" alt="License"/>
  </a>
  <a href="https://twitter.com/MusicDBProject/">
    <img src="https://img.shields.io/twitter/follow/musicdbproject.svg" alt="Twitter: @MusicDBProject"/>
  </a>
</p>

![MusicDB WebUI Screenshot](graphics/Screenshots/WebUI-2021-09-17.png?raw=true)

# MusicDB

**Your Music. Your Cloud.**

MusicDB is a music manager with focus on remote access to your music collection using a web-based user interface.
It allows you to manage an audio stream based on a song-queue.
The WebUI is focusing on being a presentation of your music rather than being a database front-end.

So, when you are listening to your music, you do not work with software.
Instead you explore your music collection.

I started this project on 4th January 2014.
Since I finished a first prototype within one weekend, I use MusicDB almost every day.
Time to share it with the world. :smiley:

## Quick Install

<table>
<tr>
<td>Distrubution</td>
<td>Download</td>
<td>Quick Install</td>
</tr>
<tr>
<td>Arch Linux</td>
<td>[📦 pkg]()</td>
<td>
```bash
wget …
su
pacman -U musicdb-8.0.0-1.pkg.tar.zst
```
</td>
</tr>
<tr>
<td>Fedora 35</td>
<td>[📦 rpm]()</td>
<td>
```bash
wget …
sudo dnf install musicdb-8.0.0-1.fc35.noarch.rpm
```
</td>
</tr>
<tr>
<td>Ubuntu</td>
<td>[📦 deb]()</td>
<td>
```bash
wget …
apt …
```
</td>
</tr>
<tr>
<td>Raspbian</td>
<td>[📦 deb]()</td>
<td>
```bash
wget …
apt …
```
</td>
</tr>
</table>

[Setup ran Run]() | [Install from Source]()

## Details

* Store your music at one place (Server), and listen to it wherever you are (via Stream)
* The client is a web application running on all operating systems that have a Firefox browser
* Albums and songs are represented by their artwork, not by rows in tables and lists
* Fuzzy search allows you to have some typos when searching your music collection
* Scales with music collections of hundreds of albums
* Explicit tag system for genres and sub-genres
* Allows you to hide all albums except for those of a genre you currently want to listen to
* Flags to annotate songs with specific moods or for other user-defined purposes
* Focus on the file systems (Keeps your music directory clean)
* Simple lyrics management

**For more details and screenshots see the start page [rstemmer.github.io/musicdb/](https://rstemmer.github.io/musicdb/index.html).**

A detailed description of MusicDB and its components can be found in the documentation: [Overview of MusicDB](https://rstemmer.github.io/musicdb/build/html/basics/overview.html)

For news, follow [@MusicDBProject](https://twitter.com/MusicDBProject) on Twitter.

For ongoing work and future plans see the [GitHub Projects](https://github.com/rstemmer/musicdb/projects).


## Important News

This section contains some important information on how to update to a next major version.
Major releases have changes that are not compatible to the previous version of MusicDB.
Furthermore those changes may break scripts you wrote around MusicDB.

Lines starting with "**:wrench: Change:**" are steps you have to do *before* or *after* updating via `update.sh` script.

**28.03.2021: 6.x.x → 7.0.0+**

* Update mechanism improved, just call the `update.sh` script (remember to make a backup)
* Full rebuild of the WebUI
  * **:wrench: Change:** Reload WebUI *after* update
* Changes in the configuration file and music database (See CHANGELOG for details)
* Experimental support for Music Videos added (needs to be enabled explicitly)
  * **:wrench: Change:** Provide `videoframes` directory access for HTTPS to see its content in the WebUI
* Docker-Support removed

<details>
<summary>01.08.2020: 5.x.x → 6.0.0+ </summary>

* Changes in the configuration file and music database (See CHANGELOG for details)
  * **:wrench: Change:** Remember to call `musicdb upgrade` *after* installation when using the `update.sh` script
  * **:wrench: Change:** Reload WebUI *after* update
* MusicAI will no longer work. Everything related to MusicAI got removed. Reason: The used framework _tflearn_ is no longer under development and got not ported to TensorFlow 2.0.

</details>

<details>
<summary> 20.01.2019: 4.x.x → 5.0.0+ </summary>

* Some changes in the configuration file
  * **:wrench: Change:** Remember to call `musicdb upgrade` *after* installation when using the `update.sh` script
* Blacklists and songqueue files in the MusicDB state directory got additional columns
  * They will be automatically upgraded by MusicDB without any information loss
* Changes in the WebUI
  * **:wrench: Change:** Reload WebUI *after* update (Clear cache if necessary)

</details>



## Socialize

Providing and maintaining open source software comes with some downsides and a lot of work.
I'd like to know if anyone is using this software, and what you are doing with it. :smiley:

So feel free to use the new [GitHub Discussions](https://github.com/rstemmer/musicdb/discussions) feature to provide some feedback. Or simply ☆ the repository.

You can also follow my project account [@MusicDBProject](https://twitter.com/MusicDBProject) on Twitter
and share some screenshots :wink:

In case you find any bugs, please [create an Issue](https://github.com/rstemmer/musicdb/issues).
Feature requests are welcome as well.


# Using MusicDB

This section describes how to install, update and use MusicDB.

## Requirements

I test MusicDB only with the latest version of the requirements listed below.
If MusicDB breaks when updating dependencies, it's a bug in MusicDB.
Then please create an issue including the name and version of the dependency that causes issues.
In case MusicDB does not run on outdated operating systems, update your system :wink:

* A Linux operating system. Tested with:
  * [Arch Linux](https://www.archlinux.org/) for x86-64 (primary test and development system)
  * [Debian](https://www.debian.org/distrib/) for x86-64 (not recommended because it comes with lots of ~~old~~ "stable" software)
  * [Ubuntu Server 20.04.2 LTS](https://ubuntu.com/download/raspberry-pi) for AArch64 on a [Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
* [Python3](https://www.python.org/) (At least Python 3.5. I test with Python 3.9)
* [Icecast](https://icecast.org/) and [GStreamer](https://gstreamer.freedesktop.org/) for streaming
* Support status for web browsers to access the WebUI:
  * [Firefox](https://www.mozilla.org/en-US/) (**Recommended**)
  * [Chrome](https://www.google.com/chrome/index.html) (**Not yet supported** as long as mandatory [CSS features](https://developer.mozilla.org/en-US/docs/Web/CSS/mask) are missing)
  * [Opera](https://www.opera.com/) (Not tested - see Chrome)
  * [Edge](https://www.microsoft.com/edge/) (Not tested - see Chrome)
  * [Safari](https://www.apple.com/safari/) (Not tested)
* A Unicode capable file system (Any *modern* file system should work)
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

### Download

The latest releases can be found in the [GitHubs Releases Section](https://github.com/rstemmer/musicdb/releases).
You can also use `git clone` and install from the *master* branch.

```sh
git clone https://github.com/rstemmer/musicdb.git
```

### Installation of MusicDB

To install MusicDB, read [:notebook: How to Install MusicDB](https://rstemmer.github.io/musicdb/build/html/usage/install.html) in the documentation.

### Update to a New Version

Updating can be done by the following simple steps.
Read the *Important News* for manual steps to do before updating to a new major release.
Only execute the scripts as root, that are followed by the comment "as root"!

``` bash
git checkout master # Only install from master branch!
git pull

cd scripts
./update.sh # as root
```

## Usage

The start page of [:notebook: MusicDB's Documentation](https://rstemmer.github.io/musicdb/build/html/index.html)
should give you the help you need to start - or at least the links to the chapters that do
(like the [:notebook: CLI MODULES chapters)](https://m45ch1n3.de/musicdb/docs/build/html/index.html#musicdb-cli).
The documentation is made for developers, not only users. So there is much more information than you will need to use MusicDB.


In general, the first steps are the following, after you have done the [:notebook: First Run](https://rstemmer.github.io/musicdb/build/html/usage/install.html#first-run):
With the new WebUI, creating *Moods* and *Genres* can also be done within the web user interface.
Open the Settings via the WebUI main menu (top right).

1. [:notebook: Add Music](https://rstemmer.github.io/musicdb/build/html/usage/music.html#importing-albums-to-musicdb) to MusicDB
2. [:notebook: Create Genres](https://rstemmer.github.io/musicdb/build/html/mod/genres.html) and sub-genres you want to use to categorize your Music.
3. [:notebook: Create Moods](https://rstemmer.github.io/musicdb/build/html/mod/moods.html) you want to assign to your songs.
4. Open the WebUI in your browser and tag the albums with the genres you created. (Right click on the albums title in the Album View). Then the random song selection process can start working and stops printing warnings.


Some helpful hints:

* For security reasons, MusicDB only accepts connections from localhost by default. Change the [:notebook: WebSocket address configuration](https://rstemmer.github.io/musicdb/build/html/basics/config.html#websocket) to access your music from anywhere.
* Make sure the web browser accepts your certificates in case they are self signed (including the WebSocket port)
* Don't be to specific with the genre tags. Define only one tag per genre like *Metal*, *Pop*, *Classic*, …
* Use sub-genre tags for a more detailed classification.
* Tag albums beforehand and songs only when they are currently playing.
* Set mood-flags only for the current playing song.
* Check the [:notebook: Configuration of Randy](https://rstemmer.github.io/musicdb/build/html/basics/config.html#randy) to make sure the random song selection can work with your music collection. When you have a small music collection, decrease the blacklist sizes.
* In the Album-View panel, right click on the album title opens a panel for tagging and defining a color scheme for the album.
* Right click on a song name inside the Album-View allows detailed tagging and pre"view"ing a song.
* When defining the Album-View colors, pay attention to good contrast and follow the color scheme of the album cover.


If there are any problems setting up MusicDB, create an issue.


# Development

This section describes how to contribute to this project.


## Documentation

The [:notebook: MusicDB Documentation](https://rstemmer.github.io/musicdb/build/html/index.html) is a good point to start.
There are all concepts, interfaces and details described.

Most important will be the [:notebook: Quick Start Section](https://rstemmer.github.io/musicdb/build/html/index.html#quick-development-start) that points out some chapters to start reading.


## Contributing

Every help is welcome.
You don't need to be a hacker to contribute to open source projects.


### What you can do

* Give feedback via [GitHub Discussions](https://github.com/rstemmer/musicdb/discussions).
  * How do you use MusicDB? How many songs do you mange with it?
  * Why do you *not* use MusicDB?
  * Ask questions to anything.
* Create an [Issue](https://github.com/rstemmer/musicdb/issues).
  * Report bugs MusicDB.
  * Report issues with the documentation.
  * Request features you like to see in MusicDB.
* Improve the documentation.
  * Improve readability by fixing grammar and typos.
  * Create an issue for sections you do not understand.
* Suggesting features via *Issue* or *Discussions*.
  * What is missing that you need.
* See if there is an *Issue* you are able to fix, or to give hints on how to fix it.
  * Post your ideas to address an existing issue.
  * Provide some dirty hacks that may help addressing an issue.
* Fix bugs or add features.
  * Edit the code to solve an issue or reduce its impact.
  * Add new features.


### Before you change code

* Read [:notebook: Working on MusicDB's Code](https://rstemmer.github.io/musicdb/build/html/basics/workflow.html)
* … and [:notebook: Philosophy of MusicDB](https://rstemmer.github.io/musicdb/build/html/basics/concept.html)
* Branch from *master*.
* Please don't commit *docs/build*.


# Roadmap

*MusicDB* is under active development.
Beside maintaining this software, I also think about improving it or adding new features if necessary.
The following list contains all huge improvements I'm planning to add to MusicDB.

* [Alpha State] Integrate music videos into the MusicDB infrastructure. The UI should be switch to video-mode. Then, instead of showing artists and their albums, artists and their videos will be shown. The videos can then be put into a video-queue that get streamed.
  * This feature is currently experimental and deactivated by default.
  * Development progress can be seen on the [corresponding GitHub Project page](https://github.com/rstemmer/musicdb/projects/1).
* [Rough Idea] Next generation of *MusicAI*. I already miss the old one that was surprisingly helpful tagging songs. The next generation might base on TensorFlow 2.0 directly. I will have the same or similar architecture since it worked in the past.
* [Planning State] Usage improvements by allowing installing MusicDB via `pip` and operating it via `systemd`.
* [Planning State] More ideas can be found on the [Roadmap GitHub Project page](https://github.com/rstemmer/musicdb/projects/4)



![MusicDB Logo](graphics/MusicDB/mdblogo.png?raw=true)

