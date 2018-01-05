# MusicDB

MusicDB is a music manager with focus on remote access to your music using a WebUI
and [Music Player Daemon (MPD)](https://musicpd.org/) for streaming.
The WebUI is more a presentation of your music than a database frontend.

Until now I spent more than 6 years for developing this software.
Since I finished a first test version, I use it nearly every day.
Time to share it with the world :)

For more details see the start page [rstemmer.github.io/musicdb/](https://rstemmer.github.io/musicdb/index.html)

For news, follow [@MusicDBProject](https://twitter.com/MusicDBProject)


## Breaking News

This section contains some important information on how to update to a next major version.
Further more those changes may break scripts you wrote around MusicDB.

Lines starting with **:wrench: Change:** are steps you have to do *before* updating via `install.sh` script.

### 1.x.x -> 2.0.0+

* Signals got replaced by a named pipe
  * New configuration: `[server] -> fifofile=DATADIR/musicdb.fifo`
  * Communication with the server via signals (`SIGTERM`, `SIGUSR1`) is deprecated. Use the named pipe instead. (Commands: `"shutdown"`, `"refresh"`)
  * [:notebook: Details and examples](https://rstemmer.github.io/musicdb/build/html/mdbapi/server.html)
  * **:wrench: Change:** Add the new configuration into your ini file

* [:notebook: database](https://rstemmer.github.io/musicdb/build/html/mod/database.html) module updated
  * *target* parameter removed. Target gets determined by its path.
  * `update` command removed. Use the [:notebook: repair](https://rstemmer.github.io/musicdb/build/html/mod/repair.html) module for updating paths.
  * `remove` command added.


## Social

Providing and maintaining open source software comes with some downsides.
I'd like to know if anyone is using this software, and what they are doing with it. :smiley:

So feel free to follow my project account [@MusicDBProject](https://twitter.com/MusicDBProject) on twitter
or e-mail me.

In case you find any bugs, please create an Issue.


# Using MusicDB

This section describes how to install, update and use MusicDB.

## Requirements

* A Linux operating system (I develop and test with latest version of [Arch Linux](https://www.archlinux.org/) x86-64, sometimes I test with the latest [Debian](https://www.debian.org/distrib/))
* [Python3](https://www.python.org/) (I only test with the latest version of Python)
* [Music Player Daemon (MPD)](https://musicpd.org/) (You should consider [Icecast](https://icecast.org/) for encrypting the stream)
* [Firefox](https://www.mozilla.org/en-US/) (recommended), [Chrome](https://www.google.com/chrome/index.html) or [Opera](http://www.opera.com/de) (I only test the WebUI with the latest version of those browsers)
* An Unicode capable file system (Any *modern* file system should work)
* A terminal that supports Unicode, with an Unicode capable font configured (I use KDE's [Konsole](https://www.kde.org/applications/system/konsole/) with [Hack](http://sourcefoundry.org/hack/))


## Download

You can clone the git repository or download the archive from the release-page.

```
git clone https://github.com/rstemmer/musicdb.git
```


## Installation and Update

[:notebook: How to Install MusicDB](https://rstemmer.github.io/musicdb/build/html/usage/install.html)

For updating, also call the `install.sh` script.
Read the *Breaking News* for manual steps to do when updating to a new major release.

## Usage

The start page of [:notebook: MusicDB's Documentation](https://rstemmer.github.io/musicdb/build/html/index.html)
should give you the help you need to start - or at least the links to the chapters they do
(The [:notebook: CLI MODULES chapters)](https://m45ch1n3.de/musicdb/docs/build/html/index.html#musicdb-cli).

# Development

This section describes how to contribute to this project.

## Documentation

The [:notebook: MusicDB Documentation](https://rstemmer.github.io/musicdb/build/html/index.html) is a good point to start.
Here are all concepts, interfaces and details described.


## Contributing

Every help is welcome.


### What you can do

* Create an Issue when you find a bug.
* Improve the documentation.
* Suggesting features via Issue.
* See if there is an Issue you are able to fix, or to give hints on how to fix it.


### Before you change code

* Read [:notebook: Working on MusicDB's Code](https://rstemmer.github.io/musicdb/build/html/basics/workflow.html)
* … and [:notebook: Basic Rules for MusicDB](https://rstemmer.github.io/musicdb/build/html/basics/concept.html)
* Please don't commit *docs/build*.


## Versioning and Branches

I work on MusicDB in three sprints per year. Each sprint is about one and a half week long.
The rest of the year I only want to concentrate on fixing critical bugs.
So you better not use any other branch than *master*.
It is also recommended to update whenever there are changes on *master*, even when there is no new release.

At least one thing can be said for sure: Major releases are not compatible with the previous version.
How to update will be described in the *Breaking News* section at the beginning of this README.


