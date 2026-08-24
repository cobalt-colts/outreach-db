-- outreach_events -> organizations: these are standing orgs, not dated events.
-- Splits location into city/state (all current rows are "City, ST"), adds
-- theme/source_url/verification/status, and loosens the uniqueness check so
-- regenerating a listing's description doesn't create a duplicate.
--
-- source_url has no historical data, so legacy rows are backfilled from the
-- existing link column; it is NOT NULL for all rows going forward.
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- SQLModel may have already created these tables when an application process
-- starts before this migration is run. Keeping the creation idempotent lets the
-- migration finish moving the legacy rows and record itself correctly.
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    description TEXT NOT NULL,
    link TEXT NOT NULL,
    theme TEXT NOT NULL,
    source_url TEXT NOT NULL,
    verified_by TEXT,
    verified_at TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'archived', 'flagged')),
    CONSTRAINT unique_organization UNIQUE (name, city, state)
);

INSERT OR IGNORE INTO organizations
    (id, name, city, state, description, link, theme, source_url, status)
SELECT
    id,
    name,
    TRIM(SUBSTR(location, 1, INSTR(location, ',') - 1)),
    TRIM(SUBSTR(location, INSTR(location, ',') + 1)),
    description,
    link,
    'pollinators',
    link,
    'active'
FROM outreach_events;

CREATE TABLE IF NOT EXISTS organization_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    CONSTRAINT unique_organization_tags UNIQUE (organization_id, tag)
);

INSERT OR IGNORE INTO organization_tags (id, organization_id, tag)
SELECT id, event_id, tag FROM outreach_event_tags;

DROP TABLE outreach_event_tags;
DROP TABLE outreach_events;

CREATE INDEX IF NOT EXISTS ix_organizations_state ON organizations(state);
CREATE INDEX IF NOT EXISTS ix_organization_tags_organization_id ON organization_tags(organization_id);

COMMIT;
PRAGMA foreign_keys = ON;
