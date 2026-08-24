-- Reshape `organizations` to exactly fit "Outreach DB - v5 - All Cities.csv".
--
-- The v5 CSV is the source of truth, so both tables are recreated empty and
-- reloaded with `python tools/csv_to_event.py "tools/Outreach DB - v5 - All Cities.csv"`.
-- The 330 rows imported by 009 came from a superseded export and carry no ZIP
-- code, which the new NOT NULL column requires; they are all present in v5.
--
-- Changes against 009:
--   + zip_code   -- CSV "ZIP Code". TEXT, not NUMBER: 145 of the 3700 ZIPs are
--                   New England / NJ codes with a leading zero ("04330"), which
--                   an integer column would silently corrupt into 4330.
--   + audit_status/audit_notes -- CSV "URL Audit Status"/"URL Audit Notes".
--                   Notes are nullable: 3660 of 3700 rows repeat one generic
--                   "no change required" sentence, so only the 40 'corrected'
--                   rows carry real content, and only those are stored.
--   - theme      -- was hardcoded 'pollinators' on every row; no CSV counterpart.
--   - source_url -- was a byte-for-byte copy of `link`; no CSV counterpart.
--
-- CSV "Cooperative Extension?" is deliberately not a column: it is exactly
-- equivalent to the presence of the "Cooperative Extension" tag on all 3700
-- rows (verified, zero mismatches), so it lives in organization_tags.
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS organization_tags;
DROP TABLE IF EXISTS organizations;

CREATE TABLE organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL
        CHECK (length(state) = 2 AND state = upper(state)),
    zip_code TEXT NOT NULL
        CHECK (zip_code GLOB '[0-9][0-9][0-9][0-9][0-9]'),
    description TEXT NOT NULL,
    link TEXT NOT NULL,
    audit_status TEXT NOT NULL DEFAULT 'checked'
        CHECK (audit_status IN ('checked', 'corrected')),
    audit_notes TEXT,
    verified_by TEXT,
    verified_at TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'archived', 'flagged')),
    -- A 'corrected' audit is only meaningful if it says what was corrected.
    CONSTRAINT audit_notes_required_when_corrected
        CHECK (audit_status <> 'corrected' OR audit_notes IS NOT NULL),
    CONSTRAINT unique_organization UNIQUE (name, city, state)
);

CREATE TABLE organization_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    CONSTRAINT unique_organization_tags UNIQUE (organization_id, tag)
);

CREATE INDEX ix_organizations_state ON organizations(state);
CREATE INDEX ix_organizations_city_state ON organizations(city, state);
CREATE INDEX ix_organization_tags_organization_id ON organization_tags(organization_id);
CREATE INDEX ix_organization_tags_tag ON organization_tags(tag);

COMMIT;
PRAGMA foreign_keys = ON;
