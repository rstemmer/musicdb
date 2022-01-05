
Upload and Importing Music
==========================

This chapter described how to upload and import music.

The process to get music into the MusicDB univers is split into three parts:

#. **Upload:** Uploading the music from the clients computer onto the server that runs MusicDB
#. **Integration:** Integrate the uploaded music into the Music Directory managed by MusicDB
#. **Import:** Add the files into the MusicDB Database, make them visible in the WebUI and available for the stream.

After the import, all music files follow the :ref:`Music Naming Scheme`.

The document :doc:`/basics/definitions` provides an overview of some therms used in this chapter.


Uploading an Album
------------------


Importing an Album
------------------



Updating Album Settings
-----------------------


Updating Song Settings
----------------------



Importing Videos to MusicDB
---------------------------

Use the ``musicdb database`` command: :doc:`/mod/database` to import videos.
And the ``musicdb videoframes`` command: :doc:`/mod/videoframes` to generate the artwork used by the WebUI.

.. code-block:: bash

   # add an album (and all songs)
   musicdb database add $MusicPath/$ArtistName/$Release\ -\ $VideoName.$Ext
   musicdb videoframes --video $MusicPath/$ArtistName/$Release\ -\ $VideoName.$Ext -u

