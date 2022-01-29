Documentation Installation
==========================

Usually you can access the documentation on `online at rstemmer.github.io/musicdb <https://rstemmer.github.io/musicdb/build/html/index.html>`_
In case you want to have the documentation installed on your server you can do this with the following steps.

Download the ``musicdb-$version-doc.tar.zst`` file from the `GitHub Repository <https://github.com/rstemmer/musicdb/releases>`_ and install it to ``/usr/share/doc/musicdb/html``.
For example:

.. code-block:: bash

   mkdir -p /usr/share/doc/musicdb/htmldoc
   tar -xf musicdb-8.0.0-doc.tar.zst --strip-components=1 -C /usr/share/doc/musicdb/htmldoc


