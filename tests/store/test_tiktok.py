"""Tests for the TikTokStore."""

import pytest
from sqlite3 import IntegrityError

from kronik.models import Analysis, Category, TikTokStats
from kronik.store.session import SessionStore
from kronik.store.tiktok import TikTokStore


@pytest.fixture
def store():
    """Create a TikTokStore instance."""
    return TikTokStore()


@pytest.fixture
def session_store():
    """Create a SessionStore instance."""
    return SessionStore()


@pytest.fixture
def stored_session(session_store, sample_session):
    """Create and store a sample session."""
    session_store.create(sample_session)
    return sample_session


def test_create_tiktok(store, sample_tiktok, stored_session):
    """Test creating a new TikTok."""
    tiktok_id = store.create(sample_tiktok, stored_session.id)
    assert tiktok_id > 0

    # Verify TikTok was created
    result = store.get(tiktok_id)
    assert result is not None
    tiktok, analysis = result

    assert tiktok.title == sample_tiktok.title
    assert tiktok.channel == sample_tiktok.channel
    assert tiktok.tiktok_url == sample_tiktok.tiktok_url
    assert analysis is None


def test_create_duplicate_tiktok(store, sample_tiktok, stored_session):
    """Test creating a TikTok with duplicate URL raises error."""
    store.create(sample_tiktok, stored_session.id)

    with pytest.raises(IntegrityError):
        store.create(sample_tiktok, stored_session.id)


def test_get_tiktok(store, sample_tiktok, stored_session):
    """Test retrieving a TikTok."""
    tiktok_id = store.create(sample_tiktok, stored_session.id)

    result = store.get(tiktok_id)
    assert result is not None
    tiktok, analysis = result

    assert tiktok.title == sample_tiktok.title
    assert tiktok.channel == sample_tiktok.channel
    assert tiktok.tiktok_url == sample_tiktok.tiktok_url
    assert analysis is None


def test_get_nonexistent_tiktok(store):
    """Test retrieving a non-existent TikTok returns None."""
    result = store.get(999)
    assert result is None


def test_list_tiktoks_from_session(store, sample_tiktok, stored_session):
    """Test listing TikToks from a session."""
    # Create multiple TikToks
    store.create(sample_tiktok, stored_session.id)

    modified_tiktok = TikTokStats(
        title="Another TikTok",
        channel=sample_tiktok.channel,
        tiktok_url="https://tiktok.com/@test_channel/video/2",
    )
    store.create(modified_tiktok, stored_session.id)

    results = store.list_tiktoks_from_session(stored_session.id)
    assert len(results) == 2
    assert all(isinstance(t, TikTokStats) for t, a in results)
    assert all(a is None for t, a in results)


def test_list_tiktoks_from_session_with_limit(store, sample_tiktok, stored_session):
    """Test listing TikToks respects limit."""
    # Create multiple TikToks
    for i in range(5):
        modified_tiktok = TikTokStats(
            title=f"TikTok {i}",
            channel=sample_tiktok.channel,
            tiktok_url=f"https://tiktok.com/@test_channel/video/{i}",
        )
        store.create(modified_tiktok, stored_session.id)

    results = store.list_tiktoks_from_session(stored_session.id, limit=3)
    assert len(results) == 3


def test_add_analysis(store, sample_tiktok, sample_analysis, stored_session):
    """Test adding analysis to a TikTok."""
    tiktok_id = store.create(sample_tiktok, stored_session.id)

    success = store.add_analysis(sample_analysis, tiktok_id)
    assert success is True

    # Verify analysis was added
    result = store.get(tiktok_id)
    assert result is not None
    tiktok, analysis = result

    assert analysis is not None
    assert analysis.transcript == sample_analysis.transcript
    assert analysis.analysis == sample_analysis.analysis
    assert analysis.tags == sample_analysis.tags
    assert analysis.category == sample_analysis.category
    assert analysis.rating == sample_analysis.rating
    assert analysis.like == sample_analysis.like


def test_add_analysis_to_nonexistent_tiktok(store, sample_analysis):
    """Test adding analysis to non-existent TikTok raises error."""
    with pytest.raises(IntegrityError):
        store.add_analysis(sample_analysis, 999)


def test_update_analysis(store, sample_tiktok, sample_analysis, stored_session):
    """Test updating existing analysis."""
    tiktok_id = store.create(sample_tiktok, stored_session.id)
    store.add_analysis(sample_analysis, tiktok_id)

    # Update analysis
    updated_analysis = Analysis(
        transcript="Updated transcript",
        analysis="Updated analysis",
        tags=["updated"],
        category=Category.EDUCATION,
        rating=1,
        like=False,
    )

    success = store.add_analysis(updated_analysis, tiktok_id)
    assert success is True

    # Verify update
    result = store.get(tiktok_id)
    assert result is not None
    tiktok, analysis = result

    assert analysis is not None
    assert analysis.transcript == updated_analysis.transcript
    assert analysis.analysis == updated_analysis.analysis
    assert analysis.tags == updated_analysis.tags
    assert analysis.category == updated_analysis.category
    assert analysis.rating == updated_analysis.rating
    assert analysis.like == updated_analysis.like


def test_delete_tiktok(store, sample_tiktok, sample_analysis, stored_session):
    """Test deleting a TikTok and its analysis."""
    tiktok_id = store.create(sample_tiktok, stored_session.id)
    store.add_analysis(sample_analysis, tiktok_id)

    success = store.delete(tiktok_id)
    assert success is True

    # Verify deletion
    result = store.get(tiktok_id)
    assert result is None


def test_delete_nonexistent_tiktok(store):
    """Test deleting a non-existent TikTok returns False."""
    success = store.delete(999)
    assert success is False


def test_get_by_url(store, sample_tiktok, stored_session):
    """Test finding a TikTok by URL."""
    store.create(sample_tiktok, stored_session.id)

    result = store.get_by_url(str(sample_tiktok.tiktok_url))
    assert result is not None
    tiktok, analysis = result

    assert tiktok.title == sample_tiktok.title
    assert tiktok.channel == sample_tiktok.channel
    assert str(tiktok.tiktok_url) == str(sample_tiktok.tiktok_url)


def test_get_by_nonexistent_url(store):
    """Test finding a non-existent TikTok by URL returns None."""
    result = store.get_by_url("https://tiktok.com/@nonexistent/video/1")
    assert result is None
