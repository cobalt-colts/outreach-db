import sqlite3
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "conf" / "db.sqlite"
DEFAULT_MIGRATIONS_PATH = Path(__file__).resolve().parent / "migrations"


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
        for sql_file in sql_files:
            connection.executescript(sql_file.read_text(encoding="utf-8"))


def get_me(uid: int, db_path: str | Path = DEFAULT_DB_PATH) -> dict[str, Any] | None:
    """Return one user as a mapping, using a short-lived connection per request."""
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

    return dict(row) if row is not None else None
