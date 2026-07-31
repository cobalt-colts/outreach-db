BEGIN;
ALTER TABLE users ADD COLUMN email TEXT;
ALTER TABLE users ADD COLUMN password_argon2 TEXT;
ALTER TABLE users ADD COLUMN permission_level INTEGER NOT NULL DEFAULT 0 CHECK (permission_level >= 0);
COMMIT;
