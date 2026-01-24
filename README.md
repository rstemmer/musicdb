
<h1 align="center">MusicDB</h1>

---

**MusicDB 8 is dying.** And so is this repository.

MusicDB is a system application, a systemd service strongly integrated into the operating system environment.
Python became a pure prototyping language with tooling focusing on isolation, not on integration.
Python became the very wrong language and execution environment for applications like MusicDB.

In addition to the core language issues, third party frameworks break or get abandoned.
This was always a pain in the ass since the beginning of MusicDB.
While I implemented more and more things myself, getting rid of many dependencies, there are sill some left.
Some with lower quality than I would like to work with.

Beside technical reasons there are also social motivation to go a step back with this repository.
While this repo got many stars - I appreciate each single interaction with the community, thank you very much - The resonance is not worth the effort.
Writing and maintaining software for other uses than oneself is very time consuming.
I can barely keep up keeping MusicDB in a working state on my own machine.
This is not the case for many setups other then mine.

* As long as I still use MusicDB 8, there will be bug fixes pushed into this repo
* Only the Linux distribution I use will be supported (At the moment Arch Linux)
* I do no longer maintain the installation documentation

---

<p align="center"><b>Your Music. Your Cloud.</b></p>

![MusicDB WebUI Screenshot](docs/landingpage/img/WebUI-3.2.0.jpg?raw=true)

MusicDB is a music manager with focus on remote access to your local music collection using a web-based user interface.
It allows you to manage an audio stream based on a song-queue.
The WebUI is focusing on being a presentation of your music rather than being a database front-end.

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
</p>


---


## 🚀 Quick Start

<p align="center">
  [&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/">🌍 Website</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/usage/install.html">⚙️ Installation Guide</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/build/html/usage/webui.html">🎵 Usage Guide</a>&nbsp;&nbsp;&nbsp;]
</p>

| Source Code      | [📦 musicdb-8.2.0-src.tar.zst](https://github.com/rstemmer/musicdb/releases/download/v8.2.0/musicdb-8.2.0-src.tar.zst) | [⚙️ Install from Source Code](https://rstemmer.github.io/musicdb/build/html/usage/fromsource.html) |
| Documentation    | [📦 musicdb-8.2.0-doc.tar.zst](https://github.com/rstemmer/musicdb/releases/download/v8.2.0/musicdb-8.2.0-doc.tar.zst) | [⚙️ Install Documentation](https://rstemmer.github.io/musicdb/build/html/usage/installdocs.html) |

[⚙️ Install, Setup and Run MusicDB with Apache and Icecast](https://rstemmer.github.io/musicdb/build/html/usage/install.html)

## 💡 Information

With the way Python tooling evolves, MusicDB heavily relies on the package manager of the used Linux distribution.
While MusicDB is hardware independent in theory, it uses frameworks that may or may not work on specific CPU architectures.

MusicDB is only supported for the latest version of Arch Linux installed on a PC with an 13th Gen Intel® Core™ i7-13700.

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

### New in Version 8.2.0

* Bug fixes and modernization

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
* Tag albums beforehand and songs only when they are currently playing to not make it feel like annoying work.
* Set mood-flags only for the current playing song - when you feel it, click it.
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

I develop and operate MusicDB on an [Arch Linux](https://www.archlinux.org/) for x86-64. So on this system it will run most reliable :smiley:.

MusicDB is only supported for the latest version of Arch Linux installed on a PC with an 13th Gen Intel® Core™ i7-13700.

I learned that not having the exact instruction set can break MusicDB dependencies, so I only say that MusicDB runs on my specific CPU as long as I still use this specific framework.
Well, to be precise, the framework did not work on my CPU, causing an illegal instruction exception.
But at least I then know and can workaround the issue (or wait until the dependency got fixed).

![MusicDB Logo](graphics/MusicDB/mdblogo.png?raw=true)

