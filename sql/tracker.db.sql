CREATE TABLE IF NOT EXISTS meta
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT,
    value       TEXT DEFAULT ''
);
INSERT INTO meta (key, value) VALUES ("version", 4);

CREATE TABLE IF NOT EXISTS songrelations
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    songida     INTEGER,
    songidb     INTEGER,
    weight      INTEGER DEFAULT 1
);

-- CREATE TABLE IF NOT EXISTS artistrelations
-- (
--     id          INTEGER PRIMARY KEY AUTOINCREMENT,
--     artistida   INTEGER,
--     artistidb   INTEGER,
--     weight      INTEGER DEFAULT 1
-- );

CREATE TABLE IF NOT EXISTS videorelations
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    videoida    INTEGER,
    videoidb    INTEGER,
    weight      INTEGER DEFAULT 1
);


CREATE TABLE IF NOT EXISTS playedsongs
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    songid      INTEGER,
    timestamp   INTEGER DEFAULT 0,
    random      INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS playedvideos
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    videoid     INTEGER,
    timestamp   INTEGER DEFAULT 0,
    random      INTEGER DEFAULT 0
);

-- vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

