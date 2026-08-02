"""Apply pending SQL migrations to the outreach database."""

import argparse
import sqlite3
import sys
from pathlib import Path


# Allow this utility to be run directly with `python tools/migrate.py`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

MIGRATIONS_DIR = PROJECT_ROOT / "app" / "migrations"
DEFAULT_DB_PATH = PROJECT_ROOT / "conf" / "db.sqlite"


def get_migrations(migrations_dir: Path = MIGRATIONS_DIR) -> list[Path]:
    """Return SQL migration files in their filename-defined order."""
    return sorted(migrations_dir.glob("*.sql"))


def apply_migrations(db_path: Path, migrations_dir: Path = MIGRATIONS_DIR) -> list[str]:
    """Apply each migration that has not yet been recorded as completed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (filename TEXT PRIMARY KEY)"
        )
        connection.commit()

        completed = {
            row[0]
            for row in connection.execute("SELECT filename FROM schema_migrations")
        }
        applied: list[str] = []

        for migration in get_migrations(migrations_dir):
            if migration.name in completed:
                continue

            try:
                connection.executescript(migration.read_text())
                connection.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (?)",
                    (migration.name,),
                )
                connection.commit()
            except sqlite3.Error as error:
                connection.rollback()
                raise RuntimeError(
                    f"Failed to apply migration {migration.name}: {error}"
                ) from error

            applied.append(migration.name)
            print(f"Applied migration: {migration.name}")

    return applied


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"SQLite database path (default: {DEFAULT_DB_PATH})",
    )
    args = parser.parse_args()

    applied = apply_migrations(args.db.resolve())
    if not applied:
        print("No pending migrations.")


if __name__ == "__main__":
    main()
