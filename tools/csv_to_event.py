import argparse
import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "conf" / "db.sqlite"


def import_events(csv_file: Path, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Import CSV events and tags without duplicating either record type."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        with csv_file.open(mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            insert_query = """
                INSERT INTO outreach_events (name, location, link, description)
                VALUES (:name, :location, :link, :description)
                ON CONFLICT(name, location, description, link) DO NOTHING
            """

            for row in reader:
                if not row["link"].startswith("https://"):
                    row["link"] = "https://" + row["link"]

                cursor.execute(insert_query, row)
                event = cursor.execute(
                    """
                    SELECT id FROM outreach_events
                    WHERE name = :name
                      AND location = :location
                      AND description = :description
                      AND link = :link
                    """,
                    row,
                ).fetchone()
                if event is None:
                    raise RuntimeError("Could not find the imported event")

                for tag in (tag.strip() for tag in row.get("tags", "").split(",")):
                    if tag:
                        cursor.execute(
                            """
                            INSERT INTO outreach_event_tags (event_id, tag)
                            VALUES (?, ?)
                            ON CONFLICT(event_id, tag) DO NOTHING
                            """,
                            (event[0], tag),
                        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="CSV to Event",
        description="Converts a CSV file into an event record in a sqlite3 database.",
    )
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()
    import_events(args.csv_file, args.db)
