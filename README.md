
<h1 align="center">MusicDB</h1>

<p align="center"><b>Your Music. Your Cloud.</b></p>

![MusicDB WebUI Screenshot](docs/landingpage/img/WebUI-3.2.0.jpg?raw=true)


<p align="center">
  <a href="https://github.com/rstemmer/musicdb/releases">
    <img src="https://img.shields.io/github/release/rstemmer/musicdb.svg" alt="MusicDB releases"/>
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"/>
  </a>
  <a href="https://github.com/rstemmer/musicdb/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/License-GPLv3-green.svg" alt="License"/>
  </a>
  <a href="https://twitter.com/MusicDBProject/">
    <img src="https://img.shields.io/twitter/follow/musicdbproject.svg" alt="Twitter: @MusicDBProject"/>
  </a>
</p>


---


## 🚀 Quick Start

<p align="center">
  [&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/">🌍 Website</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/usage/install.html">⚙️ Installation Guide</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/usage/webui.html">🎵 Usage Guide</a>&nbsp;&nbsp;&nbsp;]
</p>

| Distribution | Download | Quick Installation |
| --- | --- | --- |
| **Arch Linux**   | [📦 musicdb-8.1.0-1-any.pkg.tar.zst](https://github.com/rstemmer/musicdb/releases/download/v8.1.0/musicdb-8.1.0-1-any.pkg.tar.zst) | `pacman -U ./musicdb-8.0.0-1-any.pkg.tar.zst` |
| **Fedora** 36    | [📦 musicdb-8.1.0-1.fc36.noarch.rpm](https://github.com/rstemmer/musicdb/releases/download/v8.1.0/musicdb-8.1.0-1.fc36.noarch.rpm) | `dnf install ./musicdb-8.0.0-1.fc36.noarch.rpm` |
| **Ubuntu** 22.04 | [📦 musicdb-8.1.0-1_all.deb](        https://github.com/rstemmer/musicdb/releases/download/v8.1.0/musicdb-8.1.0-1_all.deb        ) | `apt install ./musicdb-8.0.0-1_all.deb` |
| Source Code      | [📦 musicdb-8.1.0-src.tar.zst](      https://github.com/rstemmer/musicdb/releases/download/v8.1.0/musicdb-8.1.0-src.tar.zst      ) | [⚙️ Install from Source Code](https://rstemmer.github.io/musicdb/build/html/usage/fromsource.html) |
| Documentation    | [📦 musicdb-8.1.0-doc.tar.zst](      https://github.com/rstemmer/musicdb/releases/download/v8.1.0/musicdb-8.1.0-doc.tar.zst      ) | [⚙️ Install Documentation](https://rstemmer.github.io/musicdb/build/html/usage/installdocs.html) |

[⚙️ Install, Setup and Run MusicDB with Apache and Icecast](https://rstemmer.github.io/musicdb/build/html/usage/install.html)

MusicDB requires Python 3 version 3.9.0 or later.
The WebUI requires Firefox.

## 💡 Information

MusicDB is hardware independent. It works with any Linux distribution installed on PC, ARM (like [Raspberry Pi](https://www.raspberrypi.com/)) or Mac.

**Important:** See [Transition from 7.2.0 to 8.0.0](https://rstemmer.github.io/musicdb/build/html/basics/data.html#transition-from-7-2-0-to-8-0-0) in case you already have MusicDB 7.2.0 installed.

**Important:** After updating MusicDB from 8.0.0 to 8.1.0 check if configuration file (/etc/musicdb.ini) has been updated as well.
Some new album cover scales (200 and 1000) need to be configured.
Then restart musicdb (`systemctl restart musicdb`).
Otherwise artworks are missing in the web front-end on high resolution screens.

---

## 🔍 Details

<p align="center">
  [&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/usage/install.html">⚙️ Installation Guide</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/usage/webui.html">🎵 Usage Guide</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/basics/overview.html">⚙️ Architecture</a>&nbsp;&nbsp;&nbsp;]
</p>

MusicDB is a music manager with focus on remote access to your music collection using a web-based user interface.
It allows you to manage an audio stream based on a song-queue.
The WebUI is focusing on being a presentation of your music rather than being a database front-end.

So, when you are listening to your music, you do not work with software.
Instead you explore your music collection.

I started this project on 4th January 2014.
Since I finished a first prototype within one weekend, I use MusicDB almost every day.
Time to share it with the world. :smiley:

<<<<<<< HEAD
### New in Version 8.0.0

* Upload and Import of Music via Web Front-End
* Integrated audio player in the Web Front-End 
* Better integrating into the Linux system using default system paths and systemd
=======
### New in Version 8.1.0

* Improved album filter for genres and sub genres
* Some annoying bugs fixed (Most important: Uploading albums can be continued after connection error)
>>>>>>> b43d903 (Updated for 8.1.0)

### Features

* **Artwork Oriented:** Albums and songs are represented by their artwork.
* **Clean Presentation:** No meta data overloaded list-based UI.
* **Fuzzy search:** The search allows you to have  typos and issues with foreign languages.
* **Focus on a Genre:** Hide all music not tagged with the genres you currently like to listen to.
* **Annotate your Mood:** Use flags to annotate songs with specific moods or themes.
* **Queue Based:** No playlist management distracts you from your music. Put a songs into the queue, then it will be played.
* **Private:** Your music is stored on your private server.
* **Everywhere:** Control via Web Application. Listen via Audio Stream.
* **Single User:** MusicDB is a Single-User Multi-Client application. Connect all your computers to MusicDB without messing around with user management.
* **No Limits:** Scales with music collections of hundreds of albums.
* **Independence:** Keeps your music directory clean to use it with other tools as well. The file system is ground truth, not the database.


---

## 💬 Socialize

<p align="center">
  [&nbsp;&nbsp;
  <a href="https://github.com/rstemmer/musicdb/discussions">💬 GitHub Discussions</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://twitter.com/MusicDBProject">🐦 Twitter</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://github.com/rstemmer/musicdb/issues">🐞 GitHub Issues</a>&nbsp;&nbsp;&nbsp;]
</p>

Providing and maintaining open source software comes with some downsides and a lot of work.
I'd like to know if anyone is using this software, and what you are doing with it. :smiley:

* **Star:** Hit the ☆ to make this repository a bit more relevant.
* **Feedback:** Provide some feedback [on GitHub Discussions](https://github.com/rstemmer/musicdb/discussions). Why do you *like*, *don't like* or *don't care* about MusicDB.
* **Experience:** Share some experience or screenshots [on GitHub Discussions](https://github.com/rstemmer/musicdb/discussions) or [Twitter](https://twitter.com/MusicDBProject).
* **Bug Reports:** [Create an Issue](https://github.com/rstemmer/musicdb/issues) if something does not work as you expect.
* **Feature Request:** [Create an Issue](https://github.com/rstemmer/musicdb/issues) if you like to see some feature in MusicDB.
* **Contact Me:** Write me an e-mail if you don't like to write something on the public channels.


---

## 🎵 Using MusicDB

<p align="center">
  [&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/usage/install.html">⚙️ Installation Guide</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/usage/webui.html">🎵 Usage Guide</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/index.html">📚 Code Documentation</a>&nbsp;&nbsp;&nbsp;]
</p>

The start page of [:notebook: MusicDB's Documentation](https://rstemmer.github.io/musicdb/build/html/index.html)
should give you the help you need to start.
The documentation is also made for developers, not only users. So there is much more information than you will need to use MusicDB.
For the beginning, focus on the following chapters:

1. [:notebook: Installation and Setup Manual](https://rstemmer.github.io/musicdb/build/html/usage/install.html)
2. [:notebook: Check the MusicDB Configuration](https://rstemmer.github.io/musicdb/build/html/basics/config.html)
3. [:notebook: Upload and Import Music](https://rstemmer.github.io/musicdb/build/html/usage/import.html) to MusicDB
4. [:notebook: WebUI Documentation](https://rstemmer.github.io/musicdb/build/html/usage/webui.html)

Some helpful hints:

* Don't be to specific with the genre tags. Define only one tag per genre like *Metal*, *Pop*, *Classic*, …
* Use sub-genre tags for a more detailed classification.
* Tag albums beforehand and songs only when they are currently playing.
* Set mood-flags only for the current playing song.
* Check the [:notebook: Configuration of Randy](https://rstemmer.github.io/musicdb/build/html/basics/config.html#randy) to make sure the random song selection can work with your music collection. When you have a small music collection, decrease the blacklist sizes.
* When defining the Album-View colors, pay attention to good contrast and follow the color scheme of the album cover.

If there are any problems setting up MusicDB, create an issue.


---

## 🔩 Technical Details

<p align="center">
  [&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/basics/overview.html">⚙️ Architecture</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/index.html">📚 Code Documentation</a>&nbsp;&nbsp;&nbsp;]
</p>

This section gives you a rough overview of some technical details you may want to know before installing MusicDB.

### Requirements

I test MusicDB only with the latest version of the requirements listed below.
If MusicDB breaks when updating dependencies, it's a bug in MusicDB.
Then please create an issue including the name and version of the dependency that causes issues.
In case MusicDB does not run on outdated operating systems, update your system :wink:

* A Linux operating system (Obviously :smiley: )
* [Python3 >= 3.9](https://www.python.org/) for the back-end
* [Icecast](https://icecast.org/) and [GStreamer](https://gstreamer.freedesktop.org/) for streaming
* [Apache](https://httpd.apache.org/) for serving the Web User Interface
* A detailed list of all dependencies can be found in the [Install from Source](https://rstemmer.github.io/musicdb/build/html/usage/fromsource.html) documentation

MusicDB is hardware independent. It works with any Linux distribution installed on PC, ARM (like [Raspberry Pi](https://www.raspberrypi.com/)) or Mac.

I develop and operate MusicDB on an [Arch Linux](https://www.archlinux.org/) for x86-64. So on this system it will run most reliable :smiley:.

### Note on Debian/Ubuntu

I do not support Debian/Ubuntu distributions for lots of reasons.

Anyway, periodically I test MusicDB also on an [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
 with [Ubuntu](https://ubuntu.com/download/raspberry-pi)
 or [Raspberry PI OS](https://www.raspberrypi.com/software/) which is Debian based.
So, in principle it works.
There may be a .deb package for the latest Ubuntu system, but again, expect some difficulties using MusicDB on Debian/Ubuntu.
Some quirks with Debian/Ubuntu are documented in the installation documentation.

Sometime it happens that MusicDB does not run on certain distributions like Debian or Ubuntu LTS because the packages provided by those distributions are too old.
I consider this as an issue of those distributions, not of MusicDB.

For best experience I recommend Arch Linux or Fedora to run MusicDB.

### Tested Distributions and Browsers

🟢 Test succeeded, 🔴 Test failed, 🟡 Not tested


The following list shows on which Linux distribution installing and running the MusicDB back-end succeeded:

* 🟢 [Arch Linux](https://archlinux.org/)
* 🟢 [Fedora 35](https://getfedora.org)
* 🔴 [Ubuntu 20.04 LTS](https://ubuntu.com/)<sup>1</sup>
* 🟢 [Ubuntu 21.10](https://ubuntu.com/)
* 🔴 [openSUSE Tumbleweed](https://get.opensuse.org/tumbleweed)<sup>1</sup>
* 🟡 [Raspberry PI OS](https://www.raspberrypi.com/software/)


The following list shows on which web browser running the MusicDB front-end succeeded:

* 🟢 [Firefox](https://www.mozilla.org/en-US/)
* 🔴 [Chrome](https://www.google.com/chrome/index.html)<sup>2</sup>
* 🟡 [Safari](https://www.apple.com/safari/)

<sup>**1: Python too Old** - Python 3.9+ is required; </sup>
<sup>**2: Not yet supported** as long as mandatory [CSS features](https://developer.mozilla.org/en-US/docs/Web/CSS/mask) are missing</sup>


---

## 🏗 Roadmap

MusicDB is under active development since 2014.
Because I use this software every day, it will remain under active development for a long time.
Beside maintaining this software, I also think about improving it or adding new features if necessary.

The following list contains all huge improvements I'm planning to add to MusicDB.
The links are pointing to the corresponding GitHub Project page.

**[Integration of Music Videos](https://github.com/rstemmer/musicdb/projects/1)** (Alpha Stage)<br/>
Integrate music videos into the MusicDB infrastructure.
The UI should be switch to video-mode.
Then, instead of showing artists and their albums, artists and their videos will be shown.
The videos can then be put into a video-queue that get streamed.

**[Virtual Albums](https://github.com/rstemmer/musicdb/projects/8)** (Planning Phase)<br/>
Virtual albums are a collection of single songs that are not related to an album, or a collection of sym-links to (for example) remixes.

**MusicAIv2** (Idea)<br/>
Next generation of MusicAI. I already miss the old one that was surprisingly helpful tagging songs. The next generation might base on TensorFlow 2.0 directly. I will have the same or similar architecture since it worked in the past.

More ideas in "brain-storming-phase" can be found on the [Roadmap GitHub Project page](https://github.com/rstemmer/musicdb/projects/4)


![MusicDB Logo](graphics/MusicDB/mdblogo.png?raw=true)

