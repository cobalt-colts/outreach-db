import sqlite3
from pathlib import Path
from re import DOTALL, IGNORECASE, fullmatch
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "conf" / "db.sqlite"
DEFAULT_MIGRATIONS_PATH = Path(__file__).resolve().parent / "migrations"


def _legacy_migration_is_applied(connection: sqlite3.Connection, sql: str) -> bool:
    """Recognize old databases created before migration history was recorded."""
    statements = [statement.strip() for statement in sql.split(";") if statement.strip()]
    alteration_count = 0
    if not statements:
        return False

    for statement in statements:
        if statement.upper() in {"BEGIN", "COMMIT"}:
            continue

        match = fullmatch(
            r"ALTER\s+TABLE\s+([A-Za-z_][A-Za-z0-9_]*)\s+ADD\s+COLUMN\s+([A-Za-z_][A-Za-z0-9_]*).*",
            statement,
            IGNORECASE | DOTALL,
        )
        if match is None:
            return False

        columns = {
            row[1]
            for row in connection.execute(f"PRAGMA table_info({match.group(1)})")
        }
        if match.group(2) not in columns:
            return False
        alteration_count += 1

    return alteration_count > 0


def apply_sql_folder(
    db_path: str | Path = DEFAULT_DB_PATH,
    folder_path: str | Path = DEFAULT_MIGRATIONS_PATH,
) -> None:
    """Apply the project's idempotent SQL migrations in filename order."""
    database = Path(db_path)
    migrations = Path(folder_path)
    database.parent.mkdir(parents=True, exist_ok=True)

    sql_files = sorted(migrations.glob("*.sql"))
    if not sql_files:
        return

    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations "
            "(filename TEXT PRIMARY KEY)"
        )
        for sql_file in sql_files:
            filename = sql_file.name
            applied = connection.execute(
                "SELECT 1 FROM schema_migrations WHERE filename = ?", (filename,)
            ).fetchone()
            if applied is not None:
                continue

            sql = sql_file.read_text(encoding="utf-8")
            if not _legacy_migration_is_applied(connection, sql):
                connection.executescript(sql)
            connection.execute(
                "INSERT INTO schema_migrations (filename) VALUES (?)", (filename,)
            )


def get_user(uid: int, db_path: str | Path = DEFAULT_DB_PATH) -> dict[Any, Any] | dict[str, Any] | dict[str, str] | dict[
    bytes, bytes] | None:
    """Return one user as a mapping, using a short-lived connection per request."""
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

    return dict(row) if row is not None else None

def get_user_from_email(email: str, db_path: str | Path = DEFAULT_DB_PATH) -> dict[str, Any] | None:
    """Return the user for an email address without sharing SQLite connections."""
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT id, email, password_argon2, permission_level FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    return dict(row) if row is not None else None


def update_password_hash(
    uid: int, password_hash: str, db_path: str | Path = DEFAULT_DB_PATH
) -> None:
    """Persist an upgraded Argon2 password hash after a successful login."""
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE users SET password_argon2 = ? WHERE id = ?", (password_hash, uid)
        )

def get_events():
    with sqlite3.connect(DEFAULT_DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM outreach_events")
        return cursor.fetchall()