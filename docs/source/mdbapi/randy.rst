Randomizer
==========

Randomness is art.
In context of an audio player and its task to play random songs most people would use a general purpose random-function provided by the programming languages they use.
In more critical context like security, or if the developer wants to have "perfect" randomness, a cryptography library providing cryptographic randomness would be used.
This kind of randomness is wrong for playlist/queue managers in audio software.
The randomness of tools like MusicDB is not for fuzzing data or doing security relevant task, it is for the listener.
The bad thing here is, that listeners are human.
For humans, real randomness does not *feel* random.
Real randomness allows playing multiple songs form the same album after each other.
Humans would neither expect, nor want such behavior of a randomizer.
This is why MusicDB uses a less random randomizer that feels more random.

Randy Module
------------

.. automodule:: musicdb.mdbapi.randy


Randy Class
-----------

.. autoclass:: musicdb.mdbapi.randy.Randy
   :members:

