BEGIN;
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_argon2 TEXT NOT NULL,
    permission_level INTEGER NOT NULL DEFAULT 0 CHECK (permission_level >= 0)
);
COMMIT;
