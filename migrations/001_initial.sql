-- Initial schema for SDLC discipline MCP server.

CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('decision','failure','pattern','context','exception','agent')),
    title TEXT NOT NULL,
    tags TEXT NOT NULL,                  -- JSON array of strings
    author TEXT NOT NULL,
    created_at TEXT NOT NULL,            -- ISO 8601 UTC
    status TEXT NOT NULL CHECK (status IN ('proposed','accepted','superseded','deprecated')),
    supersedes TEXT,
    superseded_by TEXT,
    last_referenced_at TEXT,
    reference_count INTEGER NOT NULL DEFAULT 0,
    evidence_links TEXT NOT NULL,        -- JSON array of URLs
    body TEXT NOT NULL,                  -- JSON object, shape depends on type
    FOREIGN KEY (supersedes)    REFERENCES entries(id),
    FOREIGN KEY (superseded_by) REFERENCES entries(id)
);

CREATE INDEX IF NOT EXISTS idx_entries_type    ON entries(type);
CREATE INDEX IF NOT EXISTS idx_entries_status  ON entries(status);
CREATE INDEX IF NOT EXISTS idx_entries_created ON entries(created_at);

CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
    id UNINDEXED,
    title,
    body,
    tags,
    tokenize = 'unicode61'
);

CREATE TABLE IF NOT EXISTS drafts (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('decision','failure','pattern','context','exception','agent')),
    content TEXT NOT NULL,               -- JSON object, full proposed entry minus auto fields
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    tool TEXT NOT NULL,
    entry_id TEXT,
    author TEXT,
    reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);
