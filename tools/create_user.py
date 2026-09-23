import getpass
import sys
from pathlib import Path

from argon2 import PasswordHasher
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import engine, init_db
from app.models import User


def main() -> None:
    email = input("User Email: ").strip().lower()
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    try:
        team_number = int(input("Team number: "))
    except ValueError:
        print("Team number must be an integer")
        return

    password = getpass.getpass("User Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    if password != confirm_password:
        print("Passwords do not match")
        return

    is_admin = input("Is admin (y/n): ").strip().lower()
    if is_admin == "y":
        permission_level = 0
    elif is_admin == "n":
        permission_level = 1
    else:
        print("Please enter y or n")
        return

    init_db()
    user = User(
        email=email,
        password_argon2=PasswordHasher().hash(password),
        permission_level=permission_level,
        first_name=first_name,
        last_name=last_name,
        team_number=team_number,
    )
    try:
        with Session(engine) as session:
            session.add(user)
            session.commit()
    except IntegrityError:
        print(f"A user with email {email} already exists")
        return

    print(f"Created user {email}")


if __name__ == "__main__":
    main()
