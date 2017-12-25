Handling log-files
=========================

There are three major tools that create a lot of logging data: ``mpd``, ``icecast`` and ``musicdb server`` itself.
To handle those logfiles it is recommended to make use of ``logrotate``.

The following example configuration contains settings for all three.
The variable ``DATADIR`` points to the directory where all MusicDB relevant data and configurations are stored.

.. literalinclude:: ../../../share/logrotate.conf

You may have to adapt the paths to your setup. I run *MusicDB* under the user/group *musicdb*.
So, you may also rename the ``su`` section for *MusicDB*.

