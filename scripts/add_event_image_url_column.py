"""Ensure the events.image_url column exists in the database."""

from pathlib import Path
import sys

import pymysql
from sqlalchemy import inspect, text

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

pymysql.install_as_MySQLdb()

from database.database import get_engine


def ensure_image_url_column() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("events")}
    if "image_url" in columns:
        print("events.image_url already present; nothing to do.")
        return

    ddl = text("ALTER TABLE events ADD COLUMN image_url VARCHAR(512) NULL")
    with engine.begin() as connection:
        connection.execute(ddl)
    print("Added events.image_url column.")


if __name__ == "__main__":
    ensure_image_url_column()
