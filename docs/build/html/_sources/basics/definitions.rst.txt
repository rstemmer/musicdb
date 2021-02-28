Definitions in Context of MusicDB
=================================

In this sections, several words used in context of MusicDB will be defined and differentiated.


Music, Songs and Videos
-----------------------

Songs:
   A Song is basically audio-only content.
   A song is always part of an album, that belongs to an artist.
   In MusicDB songs are visualized by the artwork of the related album.

Video:
   A Video is a song visualized by motion pictures related to the song.
   In context of MusicDB a video is always related to a singe song.
   A concert recording is not in focus of MusicDB and not considered to be a video.
   Videos are visualized by single frames from that video and/or by an short animation created of those frames.

Music:
   A piece of Music can be a Song or a Video.
   Music is the super-set of both.


Artwork, Thumbnail, Frame and Preview
-------------------------------------

Artwork:
   An Artwork is the picture of the cover of an album.
   This picture is used to represent albums and songs from that album.

Frame:
   A Frame usually is a part of a set of frames collected from a music video.

Thumbnail:
   A thumbnail is a selected frame that represents a music video.

Preview:
   A Preview is an animation created from a set of frames of a music video.
   The preview represents a music video like a Thumbnail.


Flags vs. Tags
--------------

TODO: Improve

Flag:
   Provided by a database column

Tag:
   Manageable augmentation


Music Properties & Statistics
-----------------------------

Properties are flags that are deeply bound to a song or video entry.
These flags are not manageable like tags.

Like / Dislike:
   ToDo

Favorite:
   ToDo

Hated:
   The song or video should be visually marked to avoid being "accidentally" added to the queue.
   A reason to mark a song as Hated can be a long intro/outro that destroys the mood/atmosphere when being played in a set.
   Other reasons can be the content of the song or video as well as the genre.

Disabled:
   This flag can be used to mark content that should not be considered as Song or Video by MusicDB.
   When a "song" or "video" is marked as Disabled, it will be visualized as less important content.
   Furthermore the content will not be considered by the random song selection algorithm.
   An example for a disabled "song" could be an interview of an artist on an album.
   Album intro and outro "songs" are also possible candidates to be flagged.


Bad Audio:
   The song or video has bad recorded live audio, or bad encoded audio.
   This property represents the technical aspect of audio.
   Bad post-production and mixing is also covered by this flag.
   While *Hated* songs are usually marked because of personal reasons, *Bad Audio* represents technical issues.

Live Recording:
   The song or a video contains live elements like comments from the artists on the state,
   or ambient noise from the audience.
   For videos, it can be enough that the video shows the band on a stage.



MDBState vs. StreamState
------------------------

MDBState:
   MDBState aka MusicDB State is the internal state of the MusicDB back-end and/or front-end.
   The state is stored in files in a corresponding directory that is defined in the MusicDB Configuration file.

StreamState:
   The StreamState consists of the online-state of the MusicDB back-end, the IceCast-server and the HTTPS web server.



