BEGIN;
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS outreach_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    link TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outreach_event_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER REFERENCES outreach_events(id) ON DELETE CASCADE,
    tag TEXT NOT NULL
);
COMMIT;