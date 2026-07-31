BEGIN TRANSACTION;

CREATE TABLE users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_argon2 TEXT NOT NULL,
    permission_level INTEGER NOT NULL DEFAULT 0 CHECK (permission_level >= 0),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    team_number INTEGER NOT NULL
);

INSERT INTO users_new (
    id, email, password_argon2, permission_level, first_name, last_name, team_number
)
SELECT id, email, password_argon2, permission_level, first_name, last_name, team_number
FROM users;

DROP TABLE users;

ALTER TABLE users_new RENAME TO users;

COMMIT;
