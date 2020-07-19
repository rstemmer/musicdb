CREATE TABLE IF NOT EXISTS meta
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT,
    value       TEXT DEFAULT ''
);
INSERT INTO meta (key, value) VALUES ("version", 5);


CREATE TABLE IF NOT EXISTS artists
(
    artistid    INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    path        TEXT
);


CREATE TABLE IF NOT EXISTS albums
(
    albumid     INTEGER PRIMARY KEY AUTOINCREMENT,
    artistid    INTEGER,
    name        TEXT,
    path        TEXT,
    numofsongs  INTEGER,
    numofcds    INTEGER,
    origin      TEXT,
    release     INTEGER,
    artworkpath TEXT DEFAULT 'default.jpg',
    bgcolor     TEXT DEFAULT '#101010',
    fgcolor     TEXT DEFAULT '#F0F0F0',
    hlcolor     TEXT DEFAULT '#909090',
    added       INTEGER DEFAULT 0
);


CREATE TABLE IF NOT EXISTS songs 
(
    songid      INTEGER PRIMARY KEY AUTOINCREMENT,
    albumid     INTEGER,
    artistid    INTEGER,
    name        TEXT,
    path        TEXT,
    number      INTEGER,
    cd          INTEGER,
    disabled    INTEGER,
    playtime    INTEGER,
    bitrate     INTEGER,
    likes       INTEGER DEFAULT 0,
    dislikes    INTEGER DEFAULT 0,
    favorite    INTEGER DEFAULT 0,
    lyricsstate INTEGER DEFAULT 0,
    checksum    TEXT    DEFAULT "",
    lastplayed  INTEGER DEFAULT 0
);


CREATE TABLE IF NOT EXISTS videos
(
    videoid     INTEGER PRIMARY KEY AUTOINCREMENT,
    songid      INTEGER DEFAULT NULL,
    albumid     INTEGER DEFAULT NULL,
    artistid    INTEGER,
    name        TEXT,
    path        TEXT,
    disabled    INTEGER DEFAULT 0,
    playtime    INTEGER,
    origin      TEXT,
    release     INTEGER,
    added       INTEGER,
    codec       TEXT,
    xresolution INTEGER,
    yresolution INTEGER,
    thumbnailpath TEXT  DEFAULT "default.jpg",
    likes       INTEGER DEFAULT 0,
    dislikes    INTEGER DEFAULT 0,
    favorite    INTEGER DEFAULT 0,
    livevideo   INTEGER DEFAULT 0,
    badaudio    INTEGER DEFAULT 0,
    checksum    TEXT    DEFAULT "",
    lastplayed  INTEGER DEFAULT 0
);


CREATE TABLE IF NOT EXISTS lyrics
(
    songid      INTEGER,
    lyrics      TEXT
);
        

CREATE TABLE IF NOT EXISTS tags
(
    tagid       INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    class       INTEGER,
    parentid    INTEGER DEFAULT NULL,
    icontype    INTEGER DEFAULT NULL,
    icon        TEXT    DEFAULT NULL,
    color       TEXT    DEFAULT NULL,
    posx        INTEGER DEFAULT NULL,
    posy        INTEGER DEFAULT NULL
);

 -- TAG_CLASS_GENRE     = 1 # genre-tags (metal, electro,…)
INSERT INTO tags (name, class, posx) VALUES ("Other", 1, 0);


CREATE TABLE IF NOT EXISTS albumtags
(
    entryid     INTEGER PRIMARY KEY AUTOINCREMENT,
    albumid     INTEGER,
    tagid       INTEGER,
    confidence  REAL    DEFAULT 1.0,
    approval    INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS songtags
(
    entryid     INTEGER PRIMARY KEY AUTOINCREMENT,
    songid      INTEGER,
    tagid       INTEGER,
    confidence  REAL    DEFAULT 1.0,
    approval    INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS videotags
(
    entryid     INTEGER PRIMARY KEY AUTOINCREMENT,
    videoid     INTEGER,
    tagid       INTEGER,
    confidence  REAL    DEFAULT 1.0,
    approval    INTEGER DEFAULT 1
);

-- vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

