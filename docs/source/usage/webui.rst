WebUI
=====

The MusicDB WebUI is the web front-end to MusicDB.
The WebUI has the following purposes:

#. Presenting the Music Collection
#. Managing the audio stream
#. Managing the Music Collection

One goal of the WebUI is, that when using it to consume music, it should not give the user the feeling to use software.
The focus is always on the music, usually visually represented by the album artwork.
The management part consisting of configuration and music upload/import can be reached via the Main Menu at the top right.


Architecture and Terms
----------------------

The WebUI has a modular architecture consisting of different Views and Layers.
A View is an exchangeable tile embedded inside the User Interface (UI).
A Layer is an overlay that is displayed on top of the UI.

The WebUI can be in different modes.
Depending on the modes, the Views of the UI change.
The following modes exist:

#. *audio mode*: Default mode. You collection of Albums are presented in this mode.
#. *video mode*: (This mode is experimental and does not work yet)
#. *settings mode*: Provides several views to manage MusicDB and your Music Collection

The following sections describe the modes and their views.


WebUI in Audio Mode
-------------------

.. figure:: ../images/WebUIViews.jpg
   :align: center

   Overview of the Views of the WebUI in Audio Mode

The screenshot highlights the different views of the WebUI.

There are some general rules that apply to all elements:

- Clicking on an Artist name scrolls the Artist View to that artist.
- Clicking on an Album Artwork shows that album in the Album View
- Album Artworks can be Drag'n'Dropped into the Queue View to add all songs of an Album


Genre View
^^^^^^^^^^

The Genre View list all genres that exist in the database.
In this view, genres can be activated or deactivated by clicking on them.

The WebUI only shows albums that have songs of an activated genre.
Furthermore the random song selection algorithm only selects songs that are of the selected genre.

HUD
^^^

The Head-Up-Display (HUD) Provides all information about the currently streamed song.

The left part of the HUD shows the name of the Song, Album and Artist.
The middle part lists all genres and sub-genres that are associated to that song.
The right part provides a grid of mood-flags that can be set or reset by clicking on them.
Next to the mood-flags is a grid of song properties that can also be set or reset by clicking on them.

.. figure:: ../images/SongProperties.jpg
   :align: right

- *Like:* Increase the Likes-Counter
- *Dislike:* Increase the Dislikes-Counter
- *Live Recording:* Flag the song when it has been recorded on stage
- *Favorite:* Mark the song as your favorite song
- *Hated:* Mark that you do not like the song
- *Deactivated:* Deactivate the song
- *Bad File:* Bad audio file (low quality, silence at the end, …)

Deactivated songs will not be considered by the random song selection algorithm.
Furthermore they will not be inserted into the queue when the whole album shall be inserted.
To learn more about the impact of the song properties see the :ref:`Album View` section.

Stream Control
^^^^^^^^^^^^^^

The Stream Control View provides two buttons to control the audio stream.

- *Start Audio Stream:* Start streaming the top song from the Song Queue.
- *Next Song:* Skip the current streaming song and play the next one in the Song Queue.

If no song is streamed, silence is streamed.
So the stream is always online.
This has the advantage that when pausing the audio stream, all clients stay connected.

Artists View
^^^^^^^^^^^^

The Artists View provides a list with all Artists and Albums of the genres selected in the Genre View.
The artists are sorted in an alphabetic order.
You can use the alphabet bar above the Artists View to jump through the list.
The albums of an artist are sorted by release date.

Clicking on an Album shows it in the Album View.
You can also drag an album and drop it into the Queue View to insert all songs of an album into the queue.

Album View
^^^^^^^^^^

The Album View is the heart of the WebUI.
It presents the selected album.
When a new song starts to get streamed, its album will automatically be opened in the Album View.

The Album View itself consist of different parts:

# TODO: Add Screenshot of Album View parts

# TODO: Show impact of Song Properties

.. figure:: ../images/TestAlbum.jpg
   :align: center

   An album shown in the Album View

Queue View
^^^^^^^^^^

The Queue View shows all songs that are in the queue.
The top entry is the currently streamed song.
You can move the entries (except for the top one) via Drag'n'Drop to change their position in the queue.
New songs can be added by Dropping them into the queue.

Above the Queue View to timers are shown.
The left one is the current time, the right one tells you when the last song in the queue will be finished being streamed.

Below the Queue View are two buttons to add a random song to the Queue.
You can append one at the end of the queue or add it right after the current streamed song.
Of course only songs associated to the activated genres were considered.


WebUI Settings Mode
-------------------

# TODO: Start with explaining the Main Menu

