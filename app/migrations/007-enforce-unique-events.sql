-- Keep the oldest copy of every event and merge its tags with tags from duplicates.
-- Foreign keys must be disabled before the transaction because the referenced tables
-- are rebuilt below.
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

CREATE TABLE outreach_events_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    link TEXT NOT NULL,
    CONSTRAINT unique_event UNIQUE (name, location, description, link)
);

INSERT INTO outreach_events_new (id, name, location, description, link)
SELECT MIN(id), name, location, description, link
FROM outreach_events
GROUP BY name, location, description, link;

CREATE TABLE outreach_event_tags_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES outreach_events_new(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    CONSTRAINT unique_event_tags UNIQUE (event_id, tag)
);

INSERT INTO outreach_event_tags_new (event_id, tag)
SELECT canonical.id, old_tags.tag
FROM outreach_event_tags AS old_tags
JOIN outreach_events AS old_events ON old_events.id = old_tags.event_id
JOIN outreach_events_new AS canonical
  ON canonical.name = old_events.name
 AND canonical.location = old_events.location
 AND canonical.description = old_events.description
 AND canonical.link = old_events.link
GROUP BY canonical.id, old_tags.tag;

DROP TABLE outreach_event_tags;
DROP TABLE outreach_events;
ALTER TABLE outreach_events_new RENAME TO outreach_events;
ALTER TABLE outreach_event_tags_new RENAME TO outreach_event_tags;

COMMIT;
PRAGMA foreign_keys = ON;
