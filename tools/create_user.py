import getpass
import sqlite3
from pathlib import Path

from argon2 import PasswordHasher

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "conf" / "db.sqlite"
DEFAULT_MIGRATIONS_PATH = Path(__file__).resolve().parent / "migrations"

ph = PasswordHasher()

email = input("User Email: ")
password = getpass.getpass("User Password: ")
confirmpassword = getpass.getpass("Confirm Password: ")

if password != confirmpassword:
    print("Passwords do not match")
    quit()

password = ph.hash(password)

isadmin = input("Is admin (y/n): ")
if isadmin == "y":
    permlevel = 0
elif isadmin == "n":
    permlevel = 1
else:
    print("Please enter y or n")
    quit()

conn = sqlite3.connect(DEFAULT_DB_PATH)
cur = conn.cursor()

cur.execute("INSERT INTO users (email, password_argon2, permission_level) VALUES (?, ?, ?)", (email, password, permlevel))
conn.commit()

