CREATE TABLE IF NOT EXISTS domains(
    domain TEXT PRIMARY KEY,
    category TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_domains_category ON domains(category);