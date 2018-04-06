Handling log-files
=========================

There are two programs that create a lot of logging data: ``icecast`` and ``musicdb server`` itself.
To handle those log files it is recommended to make use of `logrotate <https://linux.die.net/man/8/logrotate>`_ .

The following example configuration contains settings for all three.
The variable ``DATADIR`` points to the directory where all MusicDB relevant data and configurations are stored.

.. literalinclude:: ../../../share/logrotate.conf

You may have to adapt the paths to your setup. I run *MusicDB* under the user/group *musicdb*.
So, you may also rename the ``su`` section for *MusicDB*.

