
LyCra - Lyrics Crawler
======================

LyCra stands for Lyrics Crawler and provides an environment for crawlers to search for lyrics for songs in the database.

A crawler is a Python script in the crawler directory ``musicdb/lib/crawler``.
It is a derived class from :class:`lib.crawlerapi.LycraCrawler` as shown in the class diragram below.
The name of the crawler file must be exact the same name the class of the crawler has.
If the crawlers' filename is ``Example.py``, the class definition must be ``class Example(LycraCrawler)``.
The constructor must have one parameter for a :class:`~lib.db.lycra.LycraDatabase` database object.

The class diagram for a crawler:

   .. graphviz::

      digraph hierarchy {
         size="5,5"
         node[shape=record,style=filled,fillcolor=gray95]
         edge[dir=back, arrowtail=empty]

         api [label = "{LycraCrawler|# name\l# version\l# db\l|+ Crawl\l# DoCrawl\l}"]
         crawler[label = "{ExampleCrawler||/# DoCrawl\l}"]

         api -> crawler
      }

A minimal crawler implementation looks like this:

   .. code-block:: python

      from musicdb.lib.crawlerapi import LycraCrawler
      from musicdb.lib.db.lycradb import LycraDatabase

      class Example(LycraCrawler):
          def __init__(self, db):
              LycraCrawler.__init__(self, db, "Example", "1.0.0")

          def DoCrawl(self, artistname, albumname, songname, songid):
              return False

Lycra API Class
---------------

.. automodule:: musicdb.mdbapi.lycra

.. autoclass:: musicdb.mdbapi.lycra.Lycra
   :members:

Crawler Base Class
------------------

.. autoclass:: musicdb.lib.crawlerapi.LycraCrawler
   :members:


Lycra Database
--------------

.. automodule:: musicdb.lib.db.lycradb

.. autoclass:: musicdb.lib.db.lycradb.LycraDatabase
   :members:





