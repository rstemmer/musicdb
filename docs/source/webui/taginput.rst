
Tag Management
============================

taginput.js
-----------

Files
^^^^^

.. code-block:: html

   <!-- Some Basic Dependencies -->
   <link rel="stylesheet" href="lib/font-awesome/font-awesome.css">
   <link rel="stylesheet" href="css/fonts.css">
   <link rel="stylesheet" href="css/base.css">
   <link rel="stylesheet" href="css/style.css">
   <script src="lib/jquery/jquery-3.min.js"></script>  

   <!-- Major Dependency -->
   <script src="js/uimod/tagmanager.js"></script>

   <!-- Taginput Element -->
   <link rel="stylesheet" href="css/uimod/taginput.css">
   <script src="js/uimod/taginput.js"></script>

MusicDB Interface
^^^^^^^^^^^^^^^^^

   * :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetSongTag`
   * :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetAlbumTag`
   * :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveSongTag`
   * :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveAlbumTag`

Every call is a *Request* with signature ``"UpdateTagInput"`` and a pass through variable ``taginputid`` that identifies the Taginput element.

On ``fnc == "GetSong" && sig == "UpdateTagInput"``:
   Call ``Taginput_Update``

On ``fnc == "GetAlbum" && sig == "UpdateTagInput"``:
   Call ``Taginput_Update``

Example:

   .. code-block:: javascript

   
      function onMusicDBMessage(fnc, sig, args, pass)
      {
          if(sig == "UpdateTagInput")
          {
              Taginput_Update(pass.taginputid, args.tags);
          }
      }


Functions
^^^^^^^^^

.. js:autofunction:: Taginput_Create

.. js:autofunction:: Taginput_Show

.. js:autofunction:: Taginput_Update

tagmanager.js
-------------

Files
^^^^^

.. code-block:: html

   <script src="js/uimod/tagmanager.js"></script>

MusicDB Interface
^^^^^^^^^^^^^^^^^

On ``fnc == "GetTags"``:
   Call ``Tagmanager_onGetTags``

Example:

   The function :meth:`~lib.ipc.protocol.musicdbprotocol2.MusicDBProtocol2.GetTags` must be called to update the tags-cache the tagmanager manages.
   The signature should be ignored in case there is another trigger that updates the tags.

   .. code-block:: javascript

      MusicDB_Request("GetTags", "UpdateTagsCache");
      
      // …

      function onMusicDBMessage(fnc, sig, args, pass)
      {
          if(fnc == "GetTags")
          {
              Tagmanager_onGetTags(args);
          }
      }

Functions
^^^^^^^^^

.. js:autofunction:: Tagmanager_onGetTags

.. js:autofunction:: Tagmanager_GetTags

.. js:autofunction:: Tagmanager_GetGenres

.. js:autofunction:: Tagmanager_GetSubgenres

.. js:autofunction:: Tagmanager_GetMoods

