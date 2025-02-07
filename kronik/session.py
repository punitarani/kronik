"""
kronik/session.py

This module handles session management for kronik.
Each session represents a single run of the application.
"""

import json
from datetime import datetime
from pathlib import Path

from kronik import DATA_DIR
from kronik.logger import session_logger as logger
from kronik.models import SessionStatus


class Session:
    """
    Represents a single run of the kronik application.
    Handles session identification and basic metadata.
    """

    def __init__(self):
        """Initialize a new session with a unique ID."""
        # Generate session ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.id = f"session_{timestamp}"
        self.created_at = datetime.now().isoformat()
        self.status = SessionStatus.ACTIVE

        logger.info(f"Created new session: {self.id}")

    def close(self):
        """Mark the session as completed."""
        self.status = SessionStatus.COMPLETED
        logger.info(f"Closed session: {self.id}")

    @property
    def metadata(self) -> dict:
        """Get the session metadata."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "status": self.status.value,
        }


def get_session_dir(session_id: str) -> Path:
    """Get the directory path for a session."""
    return DATA_DIR.joinpath("sessions", session_id)


def save_session_metadata(session: Session) -> None:
    """Save session metadata to a file."""
    session_dir = get_session_dir(session.id)
    session_dir.mkdir(parents=True, exist_ok=True)

    metadata_file = session_dir / "metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(session.metadata, f, indent=2)


def list_sessions() -> list[dict]:
    """List all sessions sorted by creation time."""
    sessions_dir = DATA_DIR / "sessions"
    if not sessions_dir.exists():
        return []

    sessions = []
    for session_dir in sessions_dir.iterdir():
        if session_dir.is_dir():
            metadata_file = session_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    sessions.append(metadata)

    # Sort sessions by creation time
    return sorted(sessions, key=lambda x: x["created_at"], reverse=True)
