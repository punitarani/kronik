"""Integration tests for store operations."""

import pytest

from kronik.models import Analysis, Category, Session, TikTokStats
from kronik.store.session import SessionStore
from kronik.store.tiktok import TikTokStore


@pytest.fixture
def session_store():
    """Create a SessionStore instance."""
    return SessionStore()


@pytest.fixture
def tiktok_store():
    """Create a TikTokStore instance."""
    return TikTokStore()


def test_session_workflow(session_store, tiktok_store, sample_tiktok, sample_analysis):
    """Test complete session workflow with TikToks and analysis."""
    # Create an active session
    session = Session(id="workflow_test", status="active")
    session_store.create(session)

    # Add TikToks to session
    tiktoks = []
    for i in range(3):
        modified_tiktok = TikTokStats(
            title=f"TikTok {i}",
            channel=sample_tiktok.channel,
            tiktok_url=f"https://tiktok.com/@test_channel/video/workflow_{i}",
        )
        tiktok_id = tiktok_store.create(modified_tiktok, session.id)
        tiktoks.append(tiktok_id)

    # Add analysis to TikToks
    for i, tiktok_id in enumerate(tiktoks):
        modified_analysis = Analysis(
            transcript=f"Transcript {i}",
            analysis=f"Analysis {i}",
            tags=[f"tag_{i}", "test"],
            category=Category.ENTERTAINMENT,
            rating=5,
            like=True,
        )
        tiktok_store.add_analysis(modified_analysis, tiktok_id)

    # Verify session contains all TikToks with analysis
    results = tiktok_store.list_tiktoks_from_session(session.id)
    assert len(results) == 3
    for tiktok, analysis in results:
        assert tiktok is not None
        assert analysis is not None
        assert analysis.transcript.startswith("Transcript")
        assert analysis.analysis.startswith("Analysis")
        assert len(analysis.tags) == 2
        assert "test" in analysis.tags

    # Complete session
    session_store.update_status(session.id, "completed")
    updated_session = session_store.get(session.id)
    assert updated_session.status == "completed"

    # Delete session and verify cascade
    session_store.delete(session.id)
    assert session_store.get(session.id) is None
    for tiktok_id in tiktoks:
        assert tiktok_store.get(tiktok_id) is None


def test_concurrent_sessions(session_store, tiktok_store, sample_tiktok):
    """Test managing multiple active sessions."""
    # Create multiple sessions
    sessions = []
    for i in range(3):
        session = Session(id=f"concurrent_{i}", status="active")
        session_store.create(session)
        sessions.append(session)

    # Add TikToks to each session
    for session in sessions:
        for i in range(2):
            modified_tiktok = TikTokStats(
                title=f"TikTok {session.id}_{i}",
                channel=sample_tiktok.channel,
                tiktok_url=f"https://tiktok.com/@test_channel/video/{session.id}_{i}",
            )
            tiktok_store.create(modified_tiktok, session.id)

    # Verify TikToks are correctly associated
    for session in sessions:
        results = tiktok_store.list_tiktoks_from_session(session.id)
        assert len(results) == 2
        for tiktok, _ in results:
            assert session.id in tiktok.title
            assert session.id in str(tiktok.tiktok_url)

    # Complete sessions one by one
    for session in sessions:
        session_store.update_status(session.id, "completed")
        assert session_store.get(session.id).status == "completed"

    # Verify only one active session remains
    active_sessions = [s for s in session_store.list_all() if s.status == "active"]
    assert len(active_sessions) == 0


def test_duplicate_tiktok_across_sessions(session_store, tiktok_store, sample_tiktok):
    """Test handling duplicate TikToks across different sessions."""
    # Create two sessions
    session1 = Session(id="session_1", status="active")
    session2 = Session(id="session_2", status="active")
    session_store.create(session1)
    session_store.create(session2)

    # Add same TikTok to both sessions (should fail)
    tiktok_store.create(sample_tiktok, session1.id)
    with pytest.raises(Exception):  # SQLite will raise IntegrityError
        tiktok_store.create(sample_tiktok, session2.id)

    # Verify TikTok only exists in first session
    results1 = tiktok_store.list_tiktoks_from_session(session1.id)
    results2 = tiktok_store.list_tiktoks_from_session(session2.id)
    assert len(results1) == 1
    assert len(results2) == 0


def test_analysis_updates(session_store, tiktok_store, sample_tiktok):
    """Test updating analysis data."""
    # Create session and TikTok
    session = Session(id="analysis_test", status="active")
    session_store.create(session)
    tiktok_id = tiktok_store.create(sample_tiktok, session.id)

    # Add initial analysis
    initial_analysis = Analysis(
        transcript="Initial transcript",
        analysis="Initial analysis",
        tags=["initial", "test"],
        category=Category.ENTERTAINMENT,
        rating=3,
        like=False,
    )
    tiktok_store.add_analysis(initial_analysis, tiktok_id)

    # Verify initial analysis
    _, analysis = tiktok_store.get(tiktok_id)
    assert analysis is not None
    assert analysis.transcript == "Initial transcript"
    assert analysis.tags == ["initial", "test"]

    # Update analysis
    updated_analysis = Analysis(
        transcript="Updated transcript",
        analysis="Updated analysis",
        tags=["updated", "test"],
        category=Category.EDUCATION,
        rating=5,
        like=True,
    )
    tiktok_store.add_analysis(updated_analysis, tiktok_id)

    # Verify update
    _, analysis = tiktok_store.get(tiktok_id)
    assert analysis is not None
    assert analysis.transcript == "Updated transcript"
    assert analysis.tags == ["updated", "test"]
    assert analysis.category == Category.EDUCATION
    assert analysis.rating == 5
    assert analysis.like is True
