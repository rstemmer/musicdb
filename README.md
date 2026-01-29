
<h1 align="center">MusicDB</h1>

---

**MusicDB 8 is dying.** And so is this repository.

MusicDB is a system application, a systemd service strongly integrated into the operating system environment.
Python became a pure prototyping language with tooling focusing on isolation, not on integration.
Python is a very wrong language and execution environment for applications like MusicDB.
The installation process became pure pain.

In addition to the tooling issues, third party frameworks break or get abandoned.
This was always a pain in the ass since the beginning of MusicDB.
While I implemented more and more things myself, getting rid of many dependencies, there are sill some left.
Some with lower quality than I would like to work with.
It happens far to often that MusicDB breaks after updating third party modules.

Beside technical reasons there are also social motivation to go a step back with this repository.
While this repo got many stars - I appreciate each single interaction with the community, thank you very much - The resonance is not worth the effort.
Writing and maintaining software for other uses than oneself is very time consuming.
I can barely keep up keeping MusicDB in a working state on my own machine.
This is not the case for many setups other then mine.

Even though MusicDB gets maintained to keep it alive for private use,
there will be no longer commits pushed to this repository.
The repository got moved to a self-hosted git repo management tool to be independent from GitHub.

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

## 🔍 Details

<p align="center">
  [&nbsp;&nbsp;
  <a href="https://rstemmer.github.io/musicdb/">🌍 Website</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;
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


![MusicDB Logo](graphics/MusicDB/mdblogo.png?raw=true)

