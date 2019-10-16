
Docker
======

This chapter explains how to build and use the Docker based demo

Build the Image
---------------

There are two scripts provided in the ``docker`` directory of the MusicDB root directory.
The ``build.sh`` script creates the Docker image, the ``run.sh`` script executes the built Docker container.

Before you execute the scripts, please read the ``README`` file inside the docker directory.
Also, follow the instruction prompted by the executed scripts.

Using the Image
---------------

When the container gets started via the ``run.sh`` script, 
some important information get print into the shell and
you are in a bash inside the container.
Because Docker container come without systemd you have too boot some daemons (for example apache and the MusicDB Server itself)
by executing the ``container-boot.sh`` script.

MusicDB's log file can be read via ``less -R /opt/musicdb/data/debuglog.ansi``.

After the ``container-boot.sh`` script got executed, the MusicDB Demo is running and ready to use.

To access the WebUI you have to tell Firefox that you trust the URL/Port by accessing not only the main WebUI URL but also the web socket URL,
as explained in the prompted text.

Furthermore you have to add some music (See :doc:`/mod/add`) and create some genres (See :doc:`/mod/genres`) to get in contact with all features of MusicDB.
This is also explained in the prompted text.


