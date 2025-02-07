"""Session store for managing session data in SQLite."""

from datetime import datetime
from sqlite3 import IntegrityError
from typing import List, Optional

from kronik.models import Session, SessionStatus
from kronik.store.client import db


class SessionStore:
    """Handles all session-related database operations."""

    def create(self, session: Session) -> None:
        """Create a new session record.

        Args:
            session: Session object to store

        Raises:
            sqlite3.IntegrityError: If session with same ID already exists
        """
        with db.transaction():
            query = """
                INSERT INTO session (id, status)
                VALUES (?, ?)
            """
            db.execute(query, (session.id, session.status.value))

    def get(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            Session object if found, None otherwise
        """
        query = """
            SELECT id, status, created_at
            FROM session
            WHERE id = ?
        """
        result = db.execute(query, (session_id,)).fetchone()

        if not result:
            return None

        return Session(
            id=result[0],
            status=SessionStatus(result[1]),
            created_at=result[2],  # SQLite returns datetime directly
        )

    def list_all(self, limit: int = 100) -> List[Session]:
        """List all sessions, newest first.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of Session objects
        """
        query = """
            SELECT id, status, created_at
            FROM session
            ORDER BY created_at DESC
            LIMIT ?
        """
        results = db.execute(query, (limit,)).fetchall()

        return [
            Session(
                id=row[0],
                status=SessionStatus(row[1]),
                created_at=row[2],  # SQLite returns datetime directly
            )
            for row in results
        ]

    def update_status(self, session_id: str, status: SessionStatus) -> bool:
        """Update a session's status.

        Args:
            session_id: Session to update
            status: New status value

        Returns:
            True if session was updated, False if session not found

        Raises:
            ValueError: If status is invalid
        """
        with db.transaction():
            query = """
                UPDATE session
                SET status = ?
                WHERE id = ?
            """
            cursor = db.execute(query, (status.value, session_id))
            return cursor.rowcount > 0

    def delete(self, session_id: str) -> bool:
        """Delete a session and all its related data.

        Args:
            session_id: Session to delete

        Returns:
            True if session was deleted, False if session not found
        """
        with db.transaction():
            query = """
                DELETE FROM session
                WHERE id = ?
            """
            cursor = db.execute(query, (session_id,))
            return cursor.rowcount > 0

    def get_active(self) -> Optional[Session]:
        """Get the most recent active session.

        Returns:
            Most recent active Session or None
        """
        query = """
            SELECT id, status, created_at
            FROM session
            WHERE status = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = db.execute(query, (SessionStatus.ACTIVE.value,)).fetchone()

        if not result:
            return None

        return Session(
            id=result[0],
            status=SessionStatus(result[1]),
            created_at=result[2],  # SQLite returns datetime directly
        )
