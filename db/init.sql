CREATE TABLE IF NOT EXISTS domains (
    domain TEXT PRIMARY KEY,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS policies (
    client_group TEXT,
    category TEXT,
    allowed INTEGER,
    PRIMARY KEY (client_group, category)
);

CREATE TABLE IF NOT EXISTS clients (
    ip TEXT PRIMARY KEY,
    client_group TEXT
);
