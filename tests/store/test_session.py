"""Tests for the SessionStore."""

import time

import pytest
from sqlite3 import IntegrityError

from kronik.models import Session, SessionStatus
from kronik.store.session import SessionStore


@pytest.fixture
def store():
    """Create a SessionStore instance."""
    return SessionStore()


def test_create_session(store, sample_session):
    """Test creating a new session."""
    store.create(sample_session)

    # Verify session was created
    session = store.get(sample_session.id)
    assert session is not None
    assert session.id == sample_session.id
    assert session.status == sample_session.status


def test_create_duplicate_session(store, sample_session):
    """Test creating a session with duplicate ID raises error."""
    store.create(sample_session)

    with pytest.raises(IntegrityError):
        store.create(sample_session)


def test_get_session(store, sample_session):
    """Test retrieving a session."""
    store.create(sample_session)

    session = store.get(sample_session.id)
    assert session is not None
    assert session.id == sample_session.id
    assert session.status == sample_session.status
    assert session.created_at is not None


def test_get_nonexistent_session(store):
    """Test retrieving a non-existent session returns None."""
    session = store.get("nonexistent")
    assert session is None


def test_list_all_sessions(store, sample_session):
    """Test listing all sessions."""
    # Create multiple sessions
    store.create(sample_session)
    store.create(Session(id="test_session_2", status=SessionStatus.COMPLETED))

    sessions = store.list_all()
    assert len(sessions) == 2
    assert any(s.id == sample_session.id for s in sessions)
    assert any(s.id == "test_session_2" for s in sessions)


def test_list_all_sessions_with_limit(store):
    """Test listing sessions respects limit."""
    # Create multiple sessions
    for i in range(5):
        store.create(Session(id=f"test_session_{i}", status=SessionStatus.ACTIVE))

    sessions = store.list_all(limit=3)
    assert len(sessions) == 3


def test_update_session_status(store, sample_session):
    """Test updating a session's status."""
    store.create(sample_session)

    # Update status
    success = store.update_status(sample_session.id, SessionStatus.COMPLETED)
    assert success is True

    # Verify update
    session = store.get(sample_session.id)
    assert session.status == SessionStatus.COMPLETED


def test_update_nonexistent_session(store):
    """Test updating a non-existent session returns False."""
    success = store.update_status("nonexistent", SessionStatus.COMPLETED)
    assert success is False


def test_delete_session(store, sample_session):
    """Test deleting a session."""
    store.create(sample_session)

    # Delete session
    success = store.delete(sample_session.id)
    assert success is True

    # Verify deletion
    session = store.get(sample_session.id)
    assert session is None


def test_delete_nonexistent_session(store):
    """Test deleting a non-existent session returns False."""
    success = store.delete("nonexistent")
    assert success is False


def test_get_active_session(store, sample_session):
    """Test getting the most recent active session."""
    # Create multiple sessions with delays to ensure order
    store.create(sample_session)  # active
    time.sleep(0.001)  # Small delay for SQLite timestamp resolution
    store.create(Session(id="test_session_2", status=SessionStatus.COMPLETED))
    time.sleep(0.001)  # Small delay for SQLite timestamp resolution
    store.create(Session(id="test_session_3", status=SessionStatus.ACTIVE))

    session = store.get_active()
    assert session is not None
    assert session.status == SessionStatus.ACTIVE
    assert session.id == "test_session_3"  # Most recent


def test_get_active_session_none_active(store):
    """Test getting active session when none are active."""
    store.create(Session(id="test_session_1", status=SessionStatus.COMPLETED))

    session = store.get_active()
    assert session is None
