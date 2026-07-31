import sys
from pathlib import Path

# Allow this utility to be run directly with `python tools/migrate.py`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import apply_sql_folder


if __name__ == "__main__":
    apply_sql_folder()
