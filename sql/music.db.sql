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
    bgcolor     TEXT DEFAULT '#080808',
    fgcolor     TEXT DEFAULT '#F0F0F0',
    hlcolor     TEXT DEFAULT '#909090'
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
    qskips      INTEGER DEFAULT 0,
    qadds       INTEGER DEFAULT 0,
    qremoves    INTEGER DEFAULT 0,
    favorite    INTEGER DEFAULT 0,
    qrndadds    INTEGER DEFAULT 0,
    lyricsstate INTEGER DEFAULT 0,
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

-- vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

