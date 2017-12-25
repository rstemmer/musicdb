
CREATE TABLE IF NOT EXISTS songrelations
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    songida     INTEGER,
    songidb     INTEGER,
    weight      INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS artistrelations
(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    artistida   INTEGER,
    artistidb   INTEGER,
    weight      INTEGER DEFAULT 1
);

-- vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

