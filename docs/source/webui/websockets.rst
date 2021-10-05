
Websocket Connection
============================

For the concept and the documentation of the MusicDB API see :doc:`/basics/webapi`.
This document focus on the functions and infrastructure to connect to the server and access the API.
Reading the concept page first will help to understand this page.

Connection Process
------------------

   * green: functions inside the *musicdb.js* file
   * blue: methods of the `JavaScript WebSocket class <https://developer.mozilla.org/de/docs/Web/API/WebSocket>`_. The implementation is in the *musicdb.js* file anyway.
   * red: callbacks that must be implemented by the user. The names are shorted. The "…" stands for "onMusicDB"

   .. graphviz::

      digraph controlflow{
         compound=true;

         node [shape=doublecircle, color=black, fontsize=10, label="JavaScript\nEngine" ] JS;

         graph [color=blue, style=box];
         node  [fontsize=10];


         subgraph cluster_OnLoad {
            label = "window.onload";
            color = red;
            node [shape=box,     color=green4, label="ConnectToMusicDB"] OL_ConnectToMDB;
         }

         subgraph cluster_SocketOpen {
            label = "socket.onopen";
            node [shape=box,     color=red,    label="…ConnectionOpen"] SO_onOpen;
         }

         subgraph cluster_SocketClose {
            label = "socket.onclose";
            node [shape=box,     color=green4, label="MDB_StopWatchdog"]  SC_StopWatchdog;
            node [shape=diamond, color=black,  label="is readyState\nCLOASING or CLOSED"] SC_IF;
            node [shape=box,     color=red,    label="…ConnectionError"]  SC_onError;
            node [shape=box,     color=red,    label="…ConnectionClosed"] SC_onClosed;

            SC_StopWatchdog -> SC_IF;
            SC_IF           -> SC_onError  [label="no"];
            SC_IF           -> SC_onClosed [label="yes"];
         }

         subgraph cluster_SocketError {
            label = "socket.onerror";
            node [shape=box,     color=green4, label="MDB_StopWatchdog"] SE_StopWatchdog;
            node [shape=box,     color=red,    label="…ConnectionError"] SE_onError;

            SE_StopWatchdog -> SE_onError;
         }

         subgraph cluster_SocketMessage {
            label = "socket.onmessage";
            node [shape=box,     color=green4, label="MDB_ResetWatchdog"]           SM_ResetWatchdog;
            node [shape=box,     color=black,  label="Parse received\nJSON string"] SM_Decode;
            node [shape=diamond, color=black,  label="Check method variable"]       SM_IF;
            node [shape=box,     color=red,    label="…Notification"]               SM_onNotification;
            node [shape=box,     color=red,    label="…Message"]                    SM_onMessage;

            SM_ResetWatchdog -> SM_Decode;
            SM_Decode        -> SM_IF;
            SM_IF            -> SM_onNotification [label = "method == \"notification\""];
            SM_IF            -> SM_onMessage      [label = "else"];
         }


         JS -> OL_ConnectToMDB  [lhead=cluster_OnLoad,        label="When loaded"];
         JS -> SO_onOpen        [lhead=cluster_SocketOpen,    label="on open"];
         JS -> SC_StopWatchdog  [lhead=cluster_SocketClose,   label="on close"];
         JS -> SE_StopWatchdog  [lhead=cluster_SocketError,   label="on error"];
         JS -> SM_ResetWatchdog [lhead=cluster_SocketMessage, label="on message"];
          
      }


.. js:autofunction:: ConnectToMusicDB


Watchdog
--------

The existence of a watchdog timer in this code has historical reasons.
There was a bug in the server that caused a loss of the connection to all clients.
To fulfill the "The show must go on" requirement I implemented this code.
It is still in use because it does not hurt.

Watchdog gets started with the first received message and with each message reset.
When the connection gets closed or an error occurred, the watchdog timer gets stop.
Only when there are no more messages coming without any reason, the watchdog closes the current connection and establishes a new one.
When the watchdog timer runs to 0, a callback function ``onMusicDBWatchdogBarks`` gets called.

The watchdog does an automatic reconnect to the server when there are no packages coming from the server.
The MusicDB Server send in a period of several seconds (max 3) the state of the :mod:`musicdb.mdbapi.audiostream.AudioStreamingThread` to all clients.
On Windows systems, packages can be stuck inside Windows internal buffers for a long time (several seconds).
Keep this in mind when configuring the Watchdog.

To configure the watchdog set the following variables in the *config.js* file:

WATCHDOG_RUN (boolean):
   If ``true`` the watchdog function checks if there is still a connection the server.

WATCHDOG_INTERVAL (integer):
   If there is no sign that the connection is active for *interval* milliseconds, the watchdog will recognize it.

The following functions implement the Watchdog.
They are used internal by the socket object as shown in the figure above.
Usually they need not to be called from the user of the *musicdb.js* file.

.. js:autofunction:: MDB_WebsocketWatchdog

.. js:autofunction:: MDB_StopWebsocketWatchdog

.. js:autofunction:: MDB_ResetWebsocketWatchdog


Communication with the server
-----------------------------

The address of the server can be set in the following variable in *config.js*:

WEBSOCKET_URL (string):
   The URL to the websocket server. For example: ``"wss://testserver.org:9000"``.
   By default, the domain of the website with port ``9000`` will be used.
   It is required to use a secured websocket communication ``"wss"``.

.. attention::

   In case you use a self signed certificate, access URL including the port number via ``"https"`` to tell the browser that you trust that certificate.
   So with the example configuration, access ``"https://testserver.org:9000"`` and confirm the certificate.
   Then, a version note of the  *Autobahn* websocket framework is shown when everything is set up correct.

WEBSOCKET_APIKEY (string):
   To be able to communicate with the MusicDB WebSocket server, the correct API key must be set here.
   This is the same key as in the MusicDB configuration (musicdb.ini) under ``[websocket]->apikey``.
   This key gets generated during the first installation of MusicDB with a random key and can be changed if wanted.

Sending Data
^^^^^^^^^^^^

.. js:autofunction:: MusicDB_Call

.. js:autofunction:: MusicDB_Request

.. js:autofunction:: MusicDB_Broadcast

.. js:autofunction:: MDB_SendPacket


Receiving Data
^^^^^^^^^^^^^^

When a notification was sent from the server to the clients, the function ``onMusicDBNotification`` will be called.
For a general message the function ``onMusicDBMessage``.


Minimal usage
-------------

This code example shows a minimal example on how to use the JavaScript code for the websocket connection to the MusicDB Websocket Server.

   .. code-block:: javascript

      window.onload = function ()
      {
         // Connect to the server
         ConnectToMusicDB();
      }

      // Handle state changes
      function onMusicDBConnectionOpen()
      {
         window.console && console.log("Connection open");
      }
      function onMusicDBConnectionError()
      {
         window.console && console.log("An error occured!");
      }
      function onMusicDBWatchdogBarks()
      {
         window.console && console.log("Timeout!");
      }
      function onMusicDBConnectionClosed()
      {
         window.console && console.log("Connection closed");
      }

      // Handle messages and notifications from the server
      function onMusicDBNotification(fnc, sig, rawdata)
      {

         window.console && console.log("Notification received:");
         window.console && console.log(fnc);
         window.console && console.log(sig);
         window.console && console.log(rawdata);
      }
      function onMusicDBMessage(fnc, sig, args, pass)
      {

         window.console && console.log("Message received:");
         window.console && console.log(fnc);
         window.console && console.log(sig);
         window.console && console.log(args);
         window.console && console.log(pass);
      }
      
