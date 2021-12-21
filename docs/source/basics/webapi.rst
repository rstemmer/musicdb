
MusicDB Websocket API
=====================

The following documentation is part of the Python code documentation for developers.
So, there may appear some pythonic codes.
Most code presented on this page is *JavaScript*.

The names for the methods and arguments are identical.
The returned values of each method are the same as sent back by the server to the client.
So when the server method has an argument *albumid* (like ``def GetAlbum(self, albumid):``), 
than the JavaScript argument is also *albumid*. 
To give the argument ``1000`` to the *GetAlbum* function, the arguments-object must look like ``{albumid: 1000}``.

Communication
-------------

Packet format
^^^^^^^^^^^^^

A packet is a JSON string with the following entries:

method:
   Different methods to communicate with the server

fncname:
   The name of the function that shall be called on the server

fncsig:
   A function signature. If there is a response, this signature can be used to tell the client what function to call next.
   This entry is not used by the server and can be ``null``. 

arguments:
   These are the arguments to the called function.
   It is an object or list of objects with each element addressing one argument of the called method on the server.
   On received packets, this are the returned values.

pass:
   A place for pass-through arguments.
   The server will not touch this entry and returns it as it is.
   This may be useful to give the receiving client some context.

key:
   This entry holds the WebSocket API key.
   If this key does not match with the key configured for the running server in the MusicDB Configuration (``[websocket]->apikey``), then the packet gets dropped.
   Its value gets set by the JavaScript implementation right before the packet gets send to the server.

The following code show an abstract of the implementation:

.. code-block:: javascript

   // method and fncname are mandatory, the other entries are optional
   fncsig = fncsig || null;
   pass   = pass   || null;
   args   = args   || null;

   // Create Packet
   var packet = {
       method:     method,
       fncname:    fncname,
       fncsig:     fncsig,
       arguments:  args,
       pass:       pass
   }

   // Make JSON string out of the packet
   var buffer;
   buffer = JSON.stringify(packet);

   // Send string to the server
   try
   {
      socket.send(buffer);
   }
   catch(error)
   {
      window.console && console.log("[MDB] Error: Sending message to server failed!");
   }


Methods
^^^^^^^

call:
   A call of a function on the server.
   There will be no response from the server.

request:
   A request of data from the server.
   The returned value are stored in the arguments entry.
   The method entry gets set to *response* by the server.

reponse:
   This marks a direct response from the server to the client who requested data.
   *This method should only be used by the server!*

broadcast:
   A broadcast is a packet from the server that got send to all connected clients.
   If the client uses the *broadcast* method, the response gets send to all clients as broadcast as well.

notification:
   An notification is similar to a broadcast with the main difference that there was no client side action before.
   Notifications can result of internal state changes of the server.
   *This method should only be used by the server!*

There is a special *broadcast* triggered whenever the server gets triggered to update its caches by system signal *USR1*
(:meth:`.mdbapi.server.UpdateCaches`).
This broadcast should be used to update the caches on client side.
It has the following signature: ``{method:"broadcast", fncname:"sys:refresh", fncsig:"UpdateCaches", arguments:null, pass:null}``

Client side interface
---------------------

The MusicDB interface on client side is implemented in the file *musicdb.js*.
This file is documented under :doc:`/webui/websockets`.
The connection can be started by calling :js:func:`ConnectToMusicDB`.
Then there can be used several functions and callback routines to communicate with the MusicDB Websocket Server.

To establish a connection on startup, just wait for the ``onload`` event from the browser:

.. code-block:: javascript

   window.onload = function ()
   {
      ConnectToMusicDB();
   }

.. note::

   The configuration must be done inside the file musicdb.js.
   Read the :doc:`/webui/websockets` documentation for setting up the watchdog and the address of the websocket server!
   See the sections for the watchdog and the communication to the server.



Callback functions
^^^^^^^^^^^^^^^^^^

   * onMusicDBConnectionOpen()
   * onMusicDBConnectionError()
   * onMusicDBWatchdogBarks()
   * onMusicDBConnectionClosed()
   * onMusicDBNotification(fnc, sig, rawdata)
   * onMusicDBMessage(fnc, sig, args, pass)

A minimal implementation may look like this:

.. code-block:: javascript

   function onMusicDBConnectionOpen()
   {
      window.console && console.log("[MDB] Open");
   }
   function onMusicDBConnectionError()
   {
      window.console && console.log("[MDB] Error");
   }
   function onMusicDBWatchdogBarks()
   {
      window.console && console.log("[MDB] WD Barks");
   }
   function onMusicDBConnectionClosed()
   {
      window.console && console.log("[MDB] Closed");
   }
   function onMusicDBNotification(fnc, sig, rawdata)
   {
      window.console && console.log("[MDB] Notification");
   }
   function onMusicDBMessage(fnc, sig, args, pass)
   {
      window.console && console.log("[MDB] Message");

      if(fnc == "GetAlbum" && sig == "ShowAlbum")
         ShowAlbum(args.artist, args.album, args.cds, args.tags);
   }


Send data to the server
^^^^^^^^^^^^^^^^^^^^^^^

The following functions are available to communicate with the server.
The arguments *args* and *pass* are optional arguments.

.. code-block:: javascript

   function MusicDB_Call(fncname, args)
   function MusicDB_Request(fncname, fncsig, args, pass)
   function MusicDB_Broadcast(fncname, fncsig, args, pass)

The documentation of these function are linked in the following list:

   * :js:func:`MusicDB_Call`
   * :js:func:`MusicDB_Request`
   * :js:func:`MusicDB_Broadcast`

Example:

.. code-block:: javascript
      
   // Request an album with ID 1000 and signal the client that the response shall be used to show it.
   MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: 1000});

Events
------

The Streaming Thread generates events that get broadcast to all clients via notifications.

The package has the following information:

   * **method:** notification
   * **pass:** ``null``
   * Event triggered by :doc:`/mdbapi/audiostream`
      * **fncname:** ``"MusicDB:AudioStream"``
      * **fncsig:** ``"onStatusChanged"`` or ``"onTimeChanged"``
      * **argument:** The playtime of the current song in seconds, when the *fncsig* is ``"onTimeChanged"``
   * Event triggered by :doc:`/mdbapi/videostream`
      * **fncname:** ``"MusicDB:VideoStream"``
      * **fncsig:** See related documentation
      * **argument:** See related documentation
   * Event triggered by :doc:`/mdbapi/songqueue`
      * **fncname:** ``"MusicDB:SongQueue"``
      * **fncsig:** ``"onSongQueueChanged"`` or ``"onSongChanged"``
      * **argument:** ``None``
   * Event triggered by :doc:`/mdbapi/videoqueue`
      * **fncname:** ``"MusicDB:VideoQueue"``
      * **fncsig:** ``"onVideoQueueChanged"`` or ``"onVideoChanged"``
      * **argument:** ``None``
   * Event triggered by :doc:`/taskmanagement/taskmanager`
      * **fncname:** ``"MusicDB:Task"``
      * **fncsig:** ``"ChunkRequest"``, ``"StateUpdate"`` or ``"InternalError"``
      * **argument:** See :meth:`.taskmanagement.taskmanager.TaskManager.NotifyClient`

See the related documentation of the event sources for more details


Server side API
---------------

.. automodule:: musicdb.lib.ws.mdbwsi


Artists
^^^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members: GetArtists,
      GetArtistsWithAlbums,
      GetFilteredArtistsWithVideos
      CreateArtist

Albums
^^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   GetAlbums,
      GetHiddenAlbums,
      GetSortedAlbumCDs,
      GetAlbum,
      HideAlbum,
      SetAlbumColor,
      AddAlbumToQueue

Songs
^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   GetSong,
      AddSongToQueue,
      AddRandomSongToQueue,
      RemoveSongFromQueue,
      MoveSongInQueue,
      GetSongRelationship,
      UpdateSongStatistic,
      CutSongRelationship,
      PlayNextSong

Videos
^^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   GetVideos,
      GetVideo,
      AddVideoToQueue,
      AddRandomVideoToQueue,
      RemoveVideoFromQueue,
      MoveVideoInQueue,
      UpdateVideoStatistic,
      SetVideoColor,
      SetVideoTimeFrame,
      PlayNextVideo,
      VideoEnded,
      SetVideoThumbnail,
      GetVideoRelationship,
      CutVideoRelationship

Queue
^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   GetSongQueue,
      GetVideoQueue,
      AddSongToQueue,
      AddRandomSongToQueue,
      AddVideoToQueue,
      AddAlbumToQueue,
      RemoveSongFromQueue,
      RemoveVideoFromQueue,
      MoveSongInQueue,
      MoveVideoInQueue

Tag related
^^^^^^^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   GetTags,
      GetTagsStatistics,
      GetSongTags,
      GetAlbumTags,
      GetVideoTags,
      SetAlbumTag,
      RemoveAlbumTag,
      SetSongTag,
      RemoveSongTag,
      SetVideoTag,
      RemoveVideoTag,
      AddGenre,
      AddSubgenre,
      AddMoodFlag,
      DeleteTag,
      ModifyTag

Lyrics
^^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   GetSongLyrics,
      SetSongLyrics

Uploading
^^^^^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   InitiateUpload,
      UploadChunk,
      GetCurrentTasks,
      AnnotateUpload,
      IntegrateContent,
      InitiateMusicImport,
      InitiateArtworkImport,
      RemoveUpload

File Handling
^^^^^^^^^^^^^
.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   SaveWebUIConfiguration,
      LoadWebUIConfiguration,
      FindNewContent,
      FindAlbumSongFiles,
      RenameMusicFile,
      RenameAlbumDirectory,
      ChangeArtistDirectory

Other
^^^^^

.. autoclass:: musicdb.lib.ws.mdbwsi.MusicDBWebSocketInterface
   :members:   Find,
      GetAudioStreamState,
      GetVideoStreamState,
      SetAudioStreamState,
      SetVideoStreamState,
      PlayNextSong,
      PlayNextVideo,
      SetMDBState,
      GetMDBState,
      GetTables


