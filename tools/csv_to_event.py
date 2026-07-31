import argparse
import sqlite3
import csv

conn = sqlite3.connect('conf/db.sqlite')
cursor = conn.cursor()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="CSV to Event",
        description="Converts a CSV file into an event record in a sqlite3 database."
    )

    parser.add_argument('csv_file')
    args = parser.parse_args()

    with open(args.csv_file, mode='r', encoding='utf-8') as file:
        csv = csv.DictReader(file)
        insert_query = "INSERT INTO outreach_events (name, location, link, description) VALUES (:name, :location, :link, :description)"

        for row in csv:
            cursor.execute(insert_query, row)
            pk_id = cursor.lastrowid
            tags = row["tags"]
            tags_array = row["tags"].split(", ")
            for tag in tags_array:
                cursor.execute(
                    "INSERT INTO outreach_event_tags (event_id, tag) VALUES (?, ?)",
                    (pk_id, tag)
                )

    conn.commit()