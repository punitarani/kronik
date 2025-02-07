"""Database clients for kronik."""

import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator

import chromadb

from kronik import DATA_DIR

DB_DIR = DATA_DIR.joinpath("db")
CHROMA_DIR = DB_DIR.joinpath("chroma")
SQL_FP = DB_DIR.joinpath("kronik.db")

chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))


class Database:
    """SQLite database client."""

    def __init__(self, max_retries: int = 3, retry_delay: float = 0.1):
        """Initialize database client.

        Args:
            max_retries: Maximum number of connection retries
            retry_delay: Delay between retries in seconds
        """
        self._connection = None
        self._max_retries = max_retries
        self._retry_delay = retry_delay

    def connect(self, path: Path | str = None):
        """Connect to database with retry logic.

        Args:
            path: Path to database file, or ":memory:" for in-memory database

        Raises:
            sqlite3.Error: If connection fails after max retries
        """
        if path is None:
            path = DATA_DIR / "kronik.db"

        for attempt in range(self._max_retries):
            try:
                self._connection = sqlite3.connect(
                    path, detect_types=sqlite3.PARSE_DECLTYPES, timeout=10.0  # 10 second timeout
                )
                # Enable foreign key support
                self._connection.execute("PRAGMA foreign_keys = ON")
                # Register adapters and converters for datetime
                sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
                sqlite3.register_converter(
                    "TIMESTAMP", lambda dt: datetime.fromisoformat(dt.decode())
                )
                break
            except sqlite3.Error as e:
                if attempt == self._max_retries - 1:
                    raise
                time.sleep(self._retry_delay)

    @property
    def connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self.connect()
        return self._connection

    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """Execute SQL query.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            SQLite cursor
        """
        return self.connection.execute(query, params or ())

    def executescript(self, script: str) -> None:
        """Execute SQL script.

        Args:
            script: SQL script to execute
        """
        self.connection.executescript(script)

    def commit(self) -> None:
        """Commit transaction."""
        self.connection.commit()

    def close(self) -> None:
        """Close database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """Context manager for database transactions.

        Automatically commits on success or rolls back on error.

        Example:
            with db.transaction():
                db.execute("INSERT INTO ...")
                db.execute("UPDATE ...")
        """
        try:
            yield
            self.commit()
        except Exception:
            self.connection.rollback()
            raise


# Global database instance
db = Database()
