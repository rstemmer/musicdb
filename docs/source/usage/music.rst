
Music Naming Scheme
===================

This chapter explains how to handle music files for and with MusicDB.

In some sections, music videos are mentioned.
Managing videos is an experimental feature of MusicDB and is not yet available.
This feature will come in future (maybe around 2025).


Overview of the Naming Scheme
-----------------------------

The names of files and directories managed my MusicDB must follow certain rules.
MusicDB takes care that these rules are applied.
The reason behind this concept is, that when the user decides to switch to a different music management system,
the music collection is in a good shape.

The path to a song follows the scheme ``artist directory/album directory/song file``.
The names of the artist and album director and the song files must follow a specific scheme.

The path to a video follows the scheme ``artist directory/video file``.
The names of the artist director and the video files must follow a specific scheme.

All characters of the `Unicode <https://home.unicode.org/>`_ are allowed for the names.
Obviously, the file system that contains your music collection must be Unicode compatible.
On Linux this is usually the case. If your music is stored on an external device make sure to use a modern file system.
The file systems *exFAT* and *NTFS* have some restrictions that are not considered by MusicDB.

Names containing a slash (/) will be problematic due to the fact that this character is reserved for separating
directories inside a path.
Therefore the character DIVISION SLASH (U+2215 - ∕ ) must be used.
Do *not* use FRACTION SLASH because it influences how numbers around that character are displayed.

MusicDB guides you by naming the files during the Import process.


Artist Directory Name
---------------------

The name of the artist directory is the name of the artist.

Album Directory Name
--------------------

The album directory name consists of the release date of the album and the album name itself, separated by a space surrounded dash: ``$Release - $Albumname``.
The release date is the year using 4 digits.
For example: ``2016 - Ærdenbrand``

Song File Name
--------------

For song files two slightly different schemes exists, depending if the album is split into multiple CDs or not.
For single CD albums the file name is constructed out of the song number and the song name separated by a space: ``$Songnumber $Songname.$Fileextension``.
In case the album has multiple dist, the disk number is set in front of the song number separated by a dash: ``$CDNumber-$Songnumber $Songname.$Fileextension``.

A complete path to a song file would be: ``$Artistname/$Release - $Albumname/$Songnumber $Songname.$Fileextension``. For example: ``Rammstein/2005 - Rosenrot/01 Benzin.flac``

Music Video File Name
---------------------

The music video files are placed in the artists directory beneath the album directories.
They also follow a similar naming scheme: ``$Release - $Videoname.$Fileextension``.
Where ``$Release`` is the year the video was released.
This may be a different year than a corresponding album or song was released.
Separated by a space surrounded dash, the name of song or music video is required.
Then, separated by a dot, the file extension.
A complete path to the music video *Sonne* by *Rammstein* would be: ``Rammstein/2001 - Sonne.m4v``

