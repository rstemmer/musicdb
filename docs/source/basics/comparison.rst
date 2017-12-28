Comparison to Other Tools
=========================

This chapter provides a rough comparison between tools I discovered while I'm working on MusicDB.
They all have some features in common and some other features an concepts are totally different.
I extracted the features from their documentation and demo websites, so I cannot guarantee that the
information are complete.
It should just give you an overview of other tools existing.
Of cause they are all open source, too.

Introducing other tools
-----------------------

   * `Beets <http://beets.io/>`_ 
   * `CherryMusic <http://www.fomori.org/cherrymusic/index.html>`_
   * `Ampache <http://ampache.org/index.html>`_
   * `Sonerezh <https://www.sonerezh.bzh/>`_
   * `Music Playing Daemon <https://musicpd.org/>`_
   * `Modipy <https://www.mopidy.com/>`_

Some tools use `MusicBrainz <https://musicbrainz.org/>`_.
This project collects music meta data and provides them to the world.
In general this is a good idea.
Sadly the information quality is too bad for my claims.
So using MusicBrainz is both, a feature and an anti feature.

Metrics
-------

   Focus:
      What is the focus of the tool.
      Streaming, file management, tag management, …

   Information sources:
      What are the sources for the information the tool handles.
      For example file meta data, filename, external databases, …

   External sources:
      Does the tool access external sources for information collecting.

   File management:
      Does the tool manages the files in the file system (renaming, moving, *audio*-editing)

   File meta data:
      Does the tool changes the meta data of files? And when?
      
   Artwork management:
      Does the tool manage the artwork of albums.
      It should at least be possible to assign an artwork to each album.
      So inside the environment of the tool, all albums must have artworks to fulfill this metric

   Lyrics management:
      Does the tool manages the lyrics of a song.
      Similar to artworks, the assignment of lyrics to a song are important for this metric.

   Export:
      What are the possibilities to export the information inside the tool environment.
      The focus of this metric is to determine if it is possible to use the Music outside the tool.

   Streaming:
      Does the tool stream the music into the internet, and how does it do that.
      With streaming, a broadcast is meant. Not only accessing a file from the web browser.
      Using Music Playing Daemon (MPD) for streaming is OK.

   User Interface:
      What user interfaces does the tool provide.

   Playlist:
      Organization of the playlist.

   Multiuser:
      Does it support multiple user


Comparison
----------


+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Metric            | MusicDB     | beets       | CherryMusic | Ampache     | Sonerezh    | Modipy      | mpd         |
+===================+=============+=============+=============+=============+=============+=============+=============+
| Focus             | Presenting  | File and    | Web audio   | Remote music| Web audio   | Streaming   | Streaming   |
|                   | music,      | meta data   | player      | managing via| player      | server, web | server and  |
|                   | Music queue | management  |             | WebUI       |             | player (1)  | clients (2) |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Information Source| Filesystem, | Tags,       | Tags        | Tags,       |             | Tags        | Tags        |
|                   | Analysis,   | MusicBrainz |             | MusicBrainz |             |             |             |
|                   | AI          |             |             |             |             |             |             |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| External Sources  | ffmpeg      | MusicBrainz |             | MusicBrainz |             |             | None        |
|                   |             |             |             |             |             |             |             |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| File management   | By user only| Renameing / | None        |             | None        | None        | None        |
|                   |             | Moving      |             |             |             |             |             |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| File meta data    | None        | Read/Write  | Read        | Read?       | Read?       | Read        | Read        |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Artwork managing  | Yes         |             |             |             |             |             | No          |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Lyrics managing   | Yes         |             |             | No          | No          |             | No          |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Export            | Yes         | Yes         | No          | No          | No          | No          | No          |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Streaming         | Yes         | Yes         | No          | Yes         | No          | Yes         | Yes         |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| UI                | CLI/WebUI   | CLI         | WebUI       | CLI/WebUI   | WebUI       | CLI/(1)     | CLI/(2)     |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Playlist          | Queue,      |             | Playlist,   | Playlist,   | Playlist,   | Playlist    | Queue,      |
|                   | Random      |             | Queue,      | Random      | Queue,      |             | Playlist,   |
|                   |             |             | Random      |             | Random      |             | Random      |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Multiuser         | No          |             | Yes         | Yes         | Yes         | No          | Yes         |
+-------------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+

(1):
   There are extensions to access the server from the `web <https://docs.mopidy.com/en/latest/ext/web/#ext-web>`_.
   *Modipy* also supports `MPD Clients<https://docs.mopidy.com/en/latest/clients/mpd/>`_.

(2):
   There exist also `Music Playing Daemon Clients <https://www.musicpd.org/clients/>`_

Conclusion
----------

If you are looking for something like Spotify you should try `Ampache <http://ampache.org/index.html>`_.
In case you only want to access your music from your web browser, 
then `Sonerezh <https://www.sonerezh.bzh/>`_ 
and `CherryMusic <http://www.fomori.org/cherrymusic/index.html>`_ are a good choice.
When you have a totally messed up collection of files you want to organize, the `Beets <http://beets.io/>`_ is the tool you need and you should start with.
**MusicDB** is for those who manage their files by himself and want to have music centric WebUI and streaming solution.
If you cannot live with any of those tools and you want to develop your own solution, 
`Music Playing Daemon <https://musicpd.org/>`_ is the streaming backend you want to use.
If *MPD* is a level to low, try `Modipy <https://www.mopidy.com/>`_. It provides the possibility for extensions on server side as well as on client side.
In fact *Modipy* is very similar to *MusicDB*.
It just follows the common concepts of audio file management and audio players while *MusicDB* introduces different concepts and approaches.

