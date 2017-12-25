CREATE TABLE IF NOT EXISTS lyricscache
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT, 
    crawler     TEXT,
    songid      TEXT,
    updatetime  INTEGER, -- unixtime
    url         TEXT DEFAULT "",
    lyrics      BLOB
);

-- vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

