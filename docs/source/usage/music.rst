
Music
=====

This chapter explains how to handle music for MusicDB.

Naming
------

The path to a song follows the scheme "artist directory/album directory/song file".
The names of the artist and album director and the song files must follow a specific scheme.
All characters are allowed.
Obviously, the file system that contains your music collection must be Unicode compatible.

Artist Directory
^^^^^^^^^^^^^^^^

The name of the artist directory is the name of the artist.

Album Directory
^^^^^^^^^^^^^^^

The album directory name consists of the release date of the album and the album name itself, separated by a space surrounded dash: ``$Release - $Albumname``.

Song File
^^^^^^^^^

For song files two slightly different schemes exists, depending if the album is split into multiple disks or not.
For single disk albums the filename is constructed out of the song number and the song name separated by a space: ``$Songnumber $Songname.$Fileextension``.
In case the album has multiple dist, the disk number is set in front of the song number separated by a dash: ``$CDNumber-$Songnumber $Songname.$Fileextension``.

A complete path to a song file would be: ``$Artistname/$Release - $Albumname/$Songnumber $Songname.$Fileextension``. For example: "Rammstein/2005 - Rosenrot/01 Benzin.flac"

Importing Albums to the Collection
----------------------------------

This section also describes the manual import of songs.
If you do not use the semi-automatic method (``musicdb add``) you have to rename the your files manually,
so that they fit to MusicDB's naming scheme.


iTunes
^^^^^^

   #. Copy music to the collection
   #. Rename album directory from ``$Albumname`` to ``$Release - $Albumname``
   #. Check Unicodes and names of all copied files and directories

Bandcamp
^^^^^^^^

   #. Create directories for artist and album
   #. Download the album and the albumcover from the shop (flac format recommended).
   #. Unzip download in album directory and rename files

.. code-block:: bash

   # Install User-Artwork because they are not included in the Metadata
   # Sometimes they are included in the zip-archive, in this case copy 
   #  just that file
   cd $ArtworkPath/$UserDir
   wget -O "$ArtistName - $AlbumName.jpg" https://$IMAGE.jpg

   # Unzip download
   cd $MusicPath
   mkdir -p "$ArtistName/$AlbumRelease - $AlbumName"
   cd "$ArtistName/$AlbumRelease - $AlbumName"
   wget https://$ALBUM
   unzip $Download.zip
   rm $Download.zip

   # Rename all files to the "$SongNumber $SongName.flac" scheme

Importing Albums to MusicDB
---------------------------

There are two ways to import music:

   * The ``musicdb add`` command: :doc:`/mod/add` (the semi-automatic way)
   * The ``musicdb database`` command: :doc:`/mod/database` (the hard way)
   * The ``musicdb repair`` command: :doc:`/mod/repair` (not recommended - it was not made for importing)

After adding the music via ``musicdb database`` or ``musicdb repair``,
the artwork must be imported using ``musicdb artwork`` (:doc:`/mod/artwork`).

Because the import methods update the access permissions of the files, ``musicdb`` should be run as *root*.


Using the database module
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # add an artist (and all albums and songs)
   musicdb database add artist $MusicPath/$ArtistName
   musicdb artwork -u

   # add an album (and all songs)
   musicdb database add artist $MusicPath/$ArtistName/$Release\ -\ $AlbumName
   musicdb artwork -u

   # oprional you can run the AI to predict the genre tags for the new songs
   musicdb musicai -f -p store $MusicPath/$ArtistName

Using the repair module
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   musicdb -q repair
   # select the "Orphan Album/Artist"
   # and press ``a`` to add it to the album.

   musicdb artwork -u

   # oprional you can run the AI to predict the genre tags for the new songs
   musicdb musicai -f -p store $MusicPath/$ArtistName


   
Updating Songs
--------------

When updating a song file, or when renaming it, call the ``musicdb -q repair`` command: :doc:`/mod/repair`
Select the "Orpanh File" in the left list, press ``tab`` to switch to the right list and select the "Orphan DB Entry".
Then press ``u`` to update the database entry with the new file.


