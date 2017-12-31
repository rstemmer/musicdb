# musicdb

MusicDB is a music manager with focus on remote access to your music using a WebUI and MPD for streaming.
It is more a presentation of your music than a database frontend.

Until now I spent more than 6 years for developing this software.
Since I finished a first test version, I use it nearly every day.
Time to share it with the world :)

For more details see the start page [rstemmer.github.io/musicdb/](https://rstemmer.github.io/musicdb/index.html)

For news, follow [@MusicDBProject](https://twitter.com/MusicDBProject)

## Breaking News

This section contains some important information on how to update to a next major version.

Lines starting with **Change:** are steps you have to do *before* updating via `install.sh` script.

### 1.x.x -> 2.x.x

* Signals got replaced by a named pipe
  * New configuration: `[server] -> fifofile=DATADIR/musicdb.fifo`
  * Communication with the server via signals (`SIGTERM`, `SIGUSR1`) is deprecated. Use the named pipe (`"shutdown"`, `"refresh"`) instead.
  * [Details and examples](https://rstemmer.github.io/musicdb/build/html/mdbapi/server.html)
  * **Change:** Add the new configuration into your ini file

## Download

You can clone the git repository or download the archive from the release-page.
The code of the releases (also tagged in the repository) is stable.

## Installation

[How to Install MusicDB](https://rstemmer.github.io/musicdb/build/html/usage/install.html)

For updating, also call the `install.sh` script.
Read the *Breaking News* for manual steps to do when updating to a new major release.


## Documentation

[MusicDB's Documentation](https://rstemmer.github.io/musicdb/build/html/index.html)

## Social

Providing and maintaining open source software comes with some downsides.
I'd like to know if anyone is using this software, and what they are doing with it.

So feel free to follow my project account [@MusicDBProject](https://twitter.com/MusicDBProject) on twitter
or e-mail me.

## Contributing

Every help is welcome. It starts by easy things like writing an Issue in the issue tracker when you find a bug.
You can also improve the documentation.
Suggesting features via Issue is also possible.

Please don't commit docs/build if it is not mandatory.
Read [Working on MusicDB's Code](https://rstemmer.github.io/musicdb/build/html/basics/workflow.html)
and [Basic Rules for MusicDB](https://rstemmer.github.io/musicdb/build/html/basics/concept.html) before
you start editing code.

## Versioning and Branches

I work on MusicDB in three sprints per year. Each sprint is about one and a half week long.
The rest of the year I only want to concentrate on fixing critical bugs.
I'm a bit struggling pressing my development workflow in suitable versioning and git management.

At least one thing can be said for sure: Major releases are not compatible with the previous version.
How to update will be described in the *Breaking News* section at the beginning of this ReadMe.


