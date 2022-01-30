
Security Concept
================

**MusicDB has no user authentication integrated.**

MusicDB is designed to be a single-user multi-client application.
This means, that multiple clients can connect from anywhere to the server.
But it is always assumed that these clients belong to the same human user.

Furthermore, MusicDB does not implement user authentication by itself.
The MusicDB websocket server relies on the HTTPS server configuration to provide user authentication
(For example via LDAP or client-side certificate authentication).

.. note::

   There exists the following assumption:
   *Anyone can access the Websocket Port. Only authenticated users can access the WebUI (more precise: ``/var/lib/musicdb/webdata/config.js``).*

To only handle websocket traffic from authenticated users, the data must contain a secret only the WebUI knows - the API-Key.

So it is important, that only authenticated users have access to the MusicDB WebUI!

The WebUI then provides the API key that is checked by the MusicDB Websocket Server with each request.
If the key is valid, the server processes the request and may answer with a response.
If the key is invalid, the request will be ignored.

The MusicDB Websocket Server itself used TLS to ensure the data send via the websocket connection is encrypted.

**Furthermore** it is assumed that the audio stream gets protected by `Icecast <https://icecast.org/>`_,
which also allows user authentication for accessing the audio stream.
Icecast and MusicDB should run on the same server, because MusicDB does not support TLD secured communication to Icecast.

File Access Permissions
-----------------------

See :doc:`/basics/data` for a detailed documentation on the access permissions for the MusicDB file structure.

Password Protected Audio Stream
-------------------------------

If you want to protect the audio stream, you need to configure the corresponding mount points as follows:

.. code-block:: xml

   <mount>
      <!-- … -->

      <authentication type="htpasswd">
         <option name="filename" value="/var/lib/icecast/users" />
         <option name="allow_duplicate_users" value="1" />
      </authentication>

      <!-- … -->
   </mount>

   <!-- … -->

   <paths>
      <!-- … -->

      <ssl-certificate>/etc/ssl/Icecast.pem</ssl-certificate>

      <!-- … -->
   </paths>

Then create the file ``Icecast.pem`` file, configure the ``users`` file and restart Icecast:

.. code-block:: bash

   # Create Icecast.pem …

   # Setup users
   touch /var/lib/icecast/users
   chown icecast:icecast /var/lib/icecast/users
   chmod u=rw,g=r,o-rw /var/lib/icecast/users

   # Restart Icecast
   systemctl restart icecast



