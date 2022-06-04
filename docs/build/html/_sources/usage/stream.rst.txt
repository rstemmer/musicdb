Audio Stream
============

This chapter of the documentation explains how to connect to the MusicDB audio stream.
The audio stream allows you to listen to your music.
It streams the music you put into the song queue via the WebUI.

You can connect with any music player to the stream, that allows HTTP streams.
For this documentation, `VLC <https://www.videolan.org/>`_ is used because it runs on any operating system.

It is assumed that MusicDB was set up correctly and there has been music added to the database.


Managing the Audio Stream
-------------------------

In the top right part of the WebUI there are two buttons: *Start Audo Stream* and *Next Song*.

.. figure:: ../images/StreamControls.jpg
   :align: center

   The Stream Contols are used to start/stop streaming music and to skip the current song to stream the next one.

Click on *Start Audio Stream* to start streaming music.
Next you need to connect to that stream.


Connection to Audio Stream via VLC
----------------------------------

For this documentation, `VLC <https://www.videolan.org/>`_ is used because it runs on any operating system.
It works with any other external player.
In case your stream is protected, the player needs to support user authentication (VLC does support it).

The stream can be accessed by the URL of the server the Icecast server is installed on.
This is usually the same server the MusicDB is installed on.
The default port used by Icecast is port ``8000``.
So if the server is installed on a server with the IP address ``127.0.0.1`` then the address to the audio stream is `http://127.0.0.1:8000/stream <http://127.0.0.1:8000/stream>`_


#. Start VLC
#. Open the *Media* menu
#. Select *Open Network Address*
#. Copy the stream address into the text area
#. Click on *Play*

You can open the same dialog by pressing ctrl+n or (cmd+n on a Mac).


Connection to Audio Stream via WebUI
------------------------------------

Since version 8.0.0 the WebUI has a build-in stream player.

This player is integrated into the Main Menu, but hidden by default.
To enable the player, open the *WebUI Settings*.

.. figure:: ../images/WebUISettings.jpg
   :align: center

   The WebUI settings with enabled Audio Stream Player

Next, the player needs to be configured.
At least the address to the audio stream must be configured.
If your stream is protected, you can also set the user name and password.

This can be done in the *Stream Settings* right below the *WebUI Settings* in the settings menu.

.. figure:: ../images/StreamTest.jpg
   :align: center

   The Stream settings view. The settings have successful been tested, but not yet saved.

Enter all information and click on the *Save* button to save the settings.
Clicking on *Load* restores the previous settings.
Before saving, you can use the integrated player to test the settings.

When you have enabled and configured the Audio Stream Player, you can connect to the stream via the Main Menu.

.. figure:: ../images/StreamPlayer.jpg
   :align: center

   Audio stream player embedded into the Main Menu of the WebUI

The player is reduced to a single button.
In case an error occurs, the error message is shown below the button in the Main Menu.


