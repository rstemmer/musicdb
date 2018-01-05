
Music
=====

This chapter explains how to handle music files for and with MusicDB.

Naming
------

The path to a song follows the scheme ``artist directory/album directory/song file``.
The names of the artist and album director and the song files must follow a specific scheme.

All characters are allowed for the names.
Obviously, the file system that contains your music collection must be Unicode compatible.
Name containing a slash (/) will be problematic due to the fact that this character is reserved for separating
directories inside a path.
Therefore the character DIVISION SLASH (U+2215 - ∕ ) must be used.
Do *not* use FRACTION SLASH because it influences how numbers around that character are displayed.

When using the ``musicdb database add`` command, you have to rename the files and directories before.
When using ``musicdb add`` MusicDB provides a user interface that supports you by renaming the files
and checks if the names are following the scheme.

Artist Directory Name
^^^^^^^^^^^^^^^^^^^^^

The name of the artist directory is the name of the artist.

Album Directory Name
^^^^^^^^^^^^^^^^^^^^

The album directory name consists of the release date of the album and the album name itself, separated by a space surrounded dash: ``$Release - $Albumname``.
The release date is the year using 4 digits.
For example: ``2016 - Ærdenbrand``

Song File Name
^^^^^^^^^^^^^^

For song files two slightly different schemes exists, depending if the album is split into multiple CDs or not.
For single CD albums the file name is constructed out of the song number and the song name separated by a space: ``$Songnumber $Songname.$Fileextension``.
In case the album has multiple dist, the disk number is set in front of the song number separated by a dash: ``$CDNumber-$Songnumber $Songname.$Fileextension``.

A complete path to a song file would be: ``$Artistname/$Release - $Albumname/$Songnumber $Songname.$Fileextension``. For example: ``Rammstein/2005 - Rosenrot/01 Benzin.flac``


Importing Albums to MusicDB
---------------------------

There are three ways to import music:

   * The ``musicdb add`` command: :doc:`/mod/add` (the semi-automatic way)
   * The ``musicdb database`` command: :doc:`/mod/database` (the hard way)
   * The ``musicdb repair`` command: :doc:`/mod/repair` (not recommended - it was not made for importing)

After adding the music via ``musicdb database`` or ``musicdb repair``,
the artwork must be imported using ``musicdb artwork`` (:doc:`/mod/artwork`).
It can happen that the automatic import of the artwork does not work.
This is usually the case when there is no artwork embedded in the audio files.
In this case the artwork file path must be given to ``musicdb artwork`` explicitly.
See the :doc:`/mod/artwork` documentation where this step is described.

Usually the import methods trigger the server to update its caches, when the server is running.
Sometimes this fails.
If you do not see the new added album in the WebUI, trigger the server again by writing ``refresh`` into the servers FIFO file:

.. code-block:: bash

   echo "refresh" > $DATADIR/musicdb.fifo


Using the database module
^^^^^^^^^^^^^^^^^^^^^^^^^

The following example shows how to add artists and albums using the ``database`` module.
For details see :doc:`/mod/database`.

.. code-block:: bash

   # add an artist (and all albums and songs)
   musicdb database add artist $MusicPath/$ArtistName
   musicdb artwork -u

   # add an album (and all songs)
   musicdb database add album $MusicPath/$ArtistName/$Release\ -\ $AlbumName
   musicdb artwork -u

   # oprional you can run the AI to predict the genre tags for the new songs
   musicdb musicai -f -p store $MusicPath/$ArtistName

Using the repair module
^^^^^^^^^^^^^^^^^^^^^^^

The following example shows how to add artists and albums using the ``repair`` module.
For details see :doc:`/mod/repair`.

.. code-block:: bash

   musicdb repair
   # select the "Orphan Album/Artist"
   # and press ``a`` to add it to the album.

   musicdb artwork -u

   # oprional you can run the AI to predict the genre tags for the new songs
   musicdb musicai -f -p store $MusicPath/$ArtistName

Using the add module
^^^^^^^^^^^^^^^^^^^^

The following example shows how to add artists and albums using the ``add`` module.
For details see :doc:`/mod/add`.

.. code-block:: bash

   musicdb add
   # select the Album to add
   # repair the names


   
Updating Songs
--------------

When updating a song file, or when renaming it, MusicDB won't find it anymore because of the changed path.
Call the ``musicdb repair`` module to repair the connection between file and database entry.
Select the "Orphan File" in the left list, press ``tab`` to switch to the right list and select the "Orphan DB Entry".
Then press ``u`` to update the database entry with the new file.
For further details see :doc:`/mod/repair`.


