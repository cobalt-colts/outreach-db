"""Import the Outreach DB CSV export into the organizations tables.

Expects the v5 column layout:
    Organization, Location, ZIP Code, Website, Tags, Description,
    Cooperative Extension?, URL Audit Status, URL Audit Notes

"Cooperative Extension?" is intentionally not imported as a column: it is
exactly equivalent to the "Cooperative Extension" tag, which lands in
organization_tags. Rows are validated before any write, so a malformed export
fails without leaving the database half-populated.
"""

import argparse
import csv
import re
import sqlite3
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "conf" / "db.sqlite"

EXPECTED_COLUMNS = [
    "Organization",
    "Location",
    "ZIP Code",
    "Website",
    "Tags",
    "Description",
    "Cooperative Extension?",
    "URL Audit Status",
    "URL Audit Notes",
]

# The note every unchanged row repeats; carries no information worth storing.
GENERIC_AUDIT_NOTE = (
    "URL reviewed for reachability/redirect behavior and organization match; "
    "no change required."
)

LOCATION_PATTERN = re.compile(r"^\s*(?P<city>[^,]+?)\s*,\s*(?P<state>[A-Z]{2})\s*$")
ZIP_PATTERN = re.compile(r"^\d{5}$")


class CSVFormatError(ValueError):
    """Raised when the export does not match the expected v5 layout."""


def parse_row(row: dict[str, str], line: int) -> tuple[dict[str, str | None], list[str]]:
    """Validate one CSV row and split it into an organization and its tags."""
    location = (row["Location"] or "").strip()
    match = LOCATION_PATTERN.match(location)
    if match is None:
        raise CSVFormatError(f"line {line}: Location {location!r} is not 'City, ST'")

    # Kept as text: leading-zero ZIPs (04330) must survive the round trip.
    zip_code = (row["ZIP Code"] or "").strip()
    if not ZIP_PATTERN.match(zip_code):
        raise CSVFormatError(f"line {line}: ZIP Code {zip_code!r} is not five digits")

    link = (row["Website"] or "").strip()
    if not link:
        raise CSVFormatError(f"line {line}: Website is empty")
    if not link.startswith(("https://", "http://")):
        link = "https://" + link

    audit_status = (row["URL Audit Status"] or "").strip().lower()
    if audit_status not in {"checked", "corrected"}:
        raise CSVFormatError(
            f"line {line}: URL Audit Status {audit_status!r} is not Checked/Corrected"
        )

    audit_notes: str | None = (row["URL Audit Notes"] or "").strip()
    if audit_notes == GENERIC_AUDIT_NOTE or not audit_notes:
        audit_notes = None
    if audit_status == "corrected" and audit_notes is None:
        raise CSVFormatError(f"line {line}: 'Corrected' row has no audit notes")

    name = (row["Organization"] or "").strip()
    description = (row["Description"] or "").strip()
    if not name or not description:
        raise CSVFormatError(f"line {line}: Organization and Description are required")

    organization = {
        "name": name,
        "city": match["city"],
        "state": match["state"],
        "zip_code": zip_code,
        "description": description,
        "link": link,
        "audit_status": audit_status,
        "audit_notes": audit_notes,
    }

    # dict.fromkeys de-duplicates while preserving the CSV's tag order.
    tags = list(dict.fromkeys(t.strip() for t in (row["Tags"] or "").split(",") if t.strip()))
    return organization, tags


def read_csv(csv_file: Path) -> list[tuple[dict[str, str | None], list[str]]]:
    with csv_file.open(mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        missing = [c for c in EXPECTED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise CSVFormatError(f"{csv_file.name} is missing columns: {missing}")

        # enumerate from 2: line 1 is the header.
        return [parse_row(row, line) for line, row in enumerate(reader, start=2)]


def import_events(csv_file: Path, db_path: Path = DEFAULT_DB_PATH) -> tuple[int, int]:
    """Import organizations and tags idempotently. Returns (organizations, tags)."""
    parsed = read_csv(csv_file)

    insert_organization = """
        INSERT INTO organizations
            (name, city, state, zip_code, description, link, audit_status, audit_notes)
        VALUES
            (:name, :city, :state, :zip_code, :description, :link, :audit_status, :audit_notes)
        ON CONFLICT(name, city, state) DO UPDATE SET
            zip_code = excluded.zip_code,
            description = excluded.description,
            link = excluded.link,
            audit_status = excluded.audit_status,
            audit_notes = excluded.audit_notes
    """

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        tag_count = 0

        for organization, tags in parsed:
            cursor.execute(insert_organization, organization)
            row = cursor.execute(
                """
                SELECT id FROM organizations
                WHERE name = :name AND city = :city AND state = :state
                """,
                organization,
            ).fetchone()
            if row is None:
                raise RuntimeError(
                    f"Could not find the imported organization {organization['name']!r}"
                )

            cursor.executemany(
                """
                INSERT INTO organization_tags (organization_id, tag)
                VALUES (?, ?)
                ON CONFLICT(organization_id, tag) DO NOTHING
                """,
                [(row[0], tag) for tag in tags],
            )
            tag_count += len(tags)

    return len(parsed), tag_count


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="csv_to_event",
        description="Import an Outreach DB CSV export into the sqlite3 database.",
    )
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    try:
        organizations, tags = import_events(args.csv_file, args.db)
    except CSVFormatError as error:
        sys.exit(f"Import aborted: {error}")

    print(f"Imported {organizations} organizations and {tags} tag links.")


if __name__ == "__main__":
    main()
