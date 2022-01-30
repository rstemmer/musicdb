
Database
========

All databases have a table ''meta'' with the following scheme:

    +----+-----+-------+
    | id | key | value |
    +----+-----+-------+

    key:
        A string to identify a meta data variable

    value:
        The value to a key as string

One important key is ''version' that allows to identify old schemes and allows an easy update of the database.
There may be other keys depending on the databases. In that case they are described in the documentations of the related modules.

.. automodule:: musicdb.lib.db.database

Database Class
--------------

.. autoclass:: musicdb.lib.db.database.Database
   :members:

