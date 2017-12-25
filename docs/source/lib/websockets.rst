
MusicDB Websocket Protocol
==========================

There are lots of classes involved to implement the websocket server.
The image below shows the whole class diagram.
Only the more important methods are included in the diragram.
For a full list of all methods see the related documentation of the class.
As library I use `Autobahn <https://github.com/crossbario/autobahn-python>`_.
The class *WebSocketServerProtocol* and *WebSocketServerFactory* are base classes from that library.
The *MusicDBWebSocketInterface* implements the API for the JavaScript clients and is documented under :doc:`/basics/webapi`.

In the following pictures the *blue* elements are related to the :class:`lib.ws.websocket.WebSocket` class.
This class abstracts the internals of the *Autobahn* module and provides a low level communication websocket interface.
The *red* elements to :class:`lib.ws.mdbwsi.MusicDBWebSocketInterface` that implements the high level API the web clients uses.

The class diagram below shows the Autobahn classes 
`WebSocketServerProtocol <http://autobahn.readthedocs.io/en/latest/reference/autobahn.asyncio.html#autobahn.asyncio.websocket.WebSocketServerProtocol>`_ 
and `WebSocketServerFactory <http://autobahn.readthedocs.io/en/latest/reference/autobahn.asyncio.html#autobahn.asyncio.websocket.WebSocketServerFactory>`_
and how they are related to the MusicDB classes for the websocket communication.
In this diagram, only the most relavant methods and attributes are mentioned.

   .. graphviz::

      digraph hierarchy {
         size="8,8"
         node[shape=record,style=filled,fillcolor=gray95]
         edge[dir=back, arrowtail=empty]

         wssp   [label = "{WebSocketServerProtocol||}"]
         ws     [label = "{WebSocket||+ SendPacket()\l+ BroadcastPacket()\l/- onOpen()\l/- onClose()\l/- onMessage()\l}", color=blue]
         mdbwsi [label = "{MusicDBWebSocketInterface||# onWSConnect()\l# onWSDisconnect()\l# onCall()\l- onMPDEvent()\l}", color=red]
         mdbwsp [label = "{MusicDBWebSocketProtoctol||}"]
         wssf   [label = "{WebSocketServerFactory||}"]
         mdbwsf [label = "{MusicDBWebSocketFactory|- clients\l|+ AddToBroadcast()\l+ RemoveFromBroadcast()\l+ BroadcastPacket()\l+ CloseConnections()\l}"]
         mdbwss [label = "{MusicDBWebSocketServer|- factory\l- factory.protocol\l|+ Setup()\l+ Start()\l+ Stop()\l+ HandleEvents()\l}"]

         wssp -> ws
         ws -> mdbwsp
         mdbwsi -> mdbwsp
         wssf -> mdbwsf
         mdbwsp -> mdbwsf [style=dotted, arrowtail=open]
         mdbwsf -> mdbwss [arrowtail=open]
      }

The relation between the Socket Server, Socket Factory and Socket Protocol is a bit insane.
The following code may make it a bit more understandable what the *Autobahn* library wants me to do:

   .. code-block:: python

      class MusicDBWebSocketServer(object):
         def __init__(self):
            self.factory          = MusicDBWebSocketFactory()
            self.factory.protocol = MusicDBWebSocketProtocol

The methods ``onWSDisconnect`` and ``onWSConnect`` are called from :class:`lib.ws.websocket.WebSocket` and implemented in :class:`lib.ws.mdbwsi.MusicDBWebSocketInterface`.
They are used to register the callback functions for the MPD module.

The following state machine shows how a connections is processed.
The :meth:`lib.ws.websocket.WebSocket.SendPacket` and :meth:`lib.ws.websocket.WebSocket.BroadcastPacket` method can be called independed from the clients requests.
Just be sure the ``onWSConnect`` method was called before.
Otherwise the mechanics behind won't work.

   .. graphviz::

      digraph finite_state_machine {
         size="8,12"

          node [shape = doublecircle, color=black, fontsize=10, label="Listen\non port"    ] Listen_on_port;
          node [shape = circle, color=red,   fontsize=10, label="__init__"                ] CB__init__;
          node [shape = circle, color=blue,  fontsize=10, label="__init__"                ] __init__;
          node [shape = circle, color=black, fontsize=10, label="Connecting"              ] Connecting;
          node [shape = circle, color=blue,  fontsize=10, label="onOpen"                  ] onOpen;
          node [shape = circle, color=red,   fontsize=10, label="onWSConnect"             ] onWSConnect;
          node [shape = circle, color=blue,  fontsize=10, label="onClose"                 ] onClose;
          node [shape = circle, color=red,   fontsize=10, label="onWSDisconnect"          ] onWSDisconnect;
          node [shape = circle, color=blue,  fontsize=10, label="onOpenHandschakeTimeout" ] onOpenHandshakeTimeout;
          // node [shape = circle, color=blue,  fontsize=10, label="onCloseHandschakeTimeout"] onCloseHandshakeTimeout;
          node [shape = circle, color=black, fontsize=10, label="Autobahn\nMagic"         ] Active;
          node [shape = circle, color=blue,  fontsize=10, label="onMessage"               ] onMessage;
          node [shape = circle, color=red,   fontsize=10, label="onCall"                  ] onCall;
          node [shape = circle, color=blue,  fontsize=10, label="SendPacket"              ] SendPacket;
          node [shape = circle, color=blue,  fontsize=10, label="BroadcastPacket"         ] BroadcastPacket;

          Listen_on_port -> __init__ [ label = "access port"];
          __init__ -> CB__init__ [ label = "create derived\nclass object" ];
          CB__init__ -> __init__;

          __init__ -> Connecting;
          Connecting -> onOpen [ label = "open Handshake" ];
          Connecting -> onOpenHandshakeTimeout [label = "timeout" ] ;

          onOpenHandshakeTimeout -> onClose [ label = "close" ];
       
          onOpen -> onWSConnect [ label = "initialize handler" ];
          onWSConnect -> onOpen;
          onOpen -> Active [ label = "successful handshake" ];

          Active -> onMessage [ label = "got data\nfrom client" ];
          onMessage -> onCall;
          onCall -> Active [ label = "no response" ];
          onCall -> SendPacket [ label = "response" ];
          onCall -> BroadcastPacket [ label = "response to all" ];
          SendPacket -> Active [ label = "send data\nto client" ];
          BroadcastPacket -> Active [ label = "send data\nto all clients" ];

          Active -> onClose [ label = "close connection" ];
       
          onClose -> onWSDisconnect [ label = "clean up" ];
          onWSDisconnect -> onClose;
       
          onClose -> Listen_on_port;

          {rank = same; __init__; CB__init__;   }
          {rank = same; onOpen; onWSConnect;    }
          {rank = same; SendPacket; BroadcastPacket;    }
          {rank = same; onClose; onWSDisconnect;}

      }

Websocket Server
----------------

.. automodule:: lib.ws.server

.. autoclass:: lib.ws.server.MusicDBWebSocketProtocol

.. autoclass:: lib.ws.server.MusicDBWebSocketServer
   :members:

Websocket Protocol
------------------

.. automodule:: lib.ws.websocket

.. autoclass:: lib.ws.websocket.MusicDBWebSocketFactory
   :members:

.. autoclass:: lib.ws.websocket.WebSocket
   :members:


