"""One-off migration script to split users.fullname into first_name/last_name.

Run this after deploying the code that expects separate first and last name
columns. The script is idempotent: if the columns already exist it will skip
adding them, and it only drops users.fullname when present.
"""

from __future__ import annotations

from typing import Any

import pymysql
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

pymysql.install_as_MySQLdb()

from database.database import get_engine  # noqa: E402


def column_exists(conn: Connection, table: str, column: str) -> bool:
    result = conn.execute(
        text(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = :table
              AND column_name = :column
            """
        ),
        {"table": table, "column": column},
    )
    return bool(result.scalar())


def run_migration() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        if not column_exists(conn, "users", "first_name"):
            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN first_name VARCHAR(191) NULL AFTER email"
                )
            )

        if not column_exists(conn, "users", "last_name"):
            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN last_name VARCHAR(191) NULL AFTER first_name"
                )
            )

        # Backfill only rows that still need values (fresh columns will be NULL).
        conn.execute(
            text(
                """
                UPDATE users
                SET
                    first_name = CASE
                        WHEN fullname IS NULL OR fullname = '' THEN 'User'
                        ELSE SUBSTRING_INDEX(fullname, ' ', 1)
                    END,
                    last_name = CASE
                        WHEN fullname IS NULL OR fullname = '' THEN 'User'
                        WHEN fullname NOT LIKE '% %' THEN SUBSTRING_INDEX(fullname, ' ', 1)
                        ELSE TRIM(SUBSTRING(fullname, LOCATE(' ', fullname) + 1))
                    END
                WHERE (first_name IS NULL OR last_name IS NULL)
                """
            )
        )

        # Ensure blanks are replaced so we can enforce NOT NULL.
        conn.execute(
            text(
                "UPDATE users SET first_name = 'User' WHERE first_name IS NULL OR TRIM(first_name) = ''"
            )
        )
        conn.execute(
            text(
                "UPDATE users SET last_name = first_name WHERE last_name IS NULL OR TRIM(last_name) = ''"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE users "
                "MODIFY COLUMN first_name VARCHAR(191) NOT NULL, "
                "MODIFY COLUMN last_name VARCHAR(191) NOT NULL"
            )
        )

        if column_exists(conn, "users", "fullname"):
            conn.execute(text("ALTER TABLE users DROP COLUMN fullname"))


def main() -> None:
    try:
        run_migration()
    except SQLAlchemyError as exc:  # pragma: no cover
        raise SystemExit(f"Migration failed: {exc}") from exc
    else:
        print("Migration completed successfully.")


if __name__ == "__main__":
    main()
