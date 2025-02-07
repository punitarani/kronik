def pytest_configure(config):
    """Configure pytest options."""
    config.option.asyncio_default_fixture_loop_scope = "function"


"""Test fixtures for kronik."""

import os
from pathlib import Path

import pytest

from kronik import DATA_DIR
from kronik.models import Analysis, Category, Session, SessionStatus, TikTokStats
from kronik.store.client import db


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create a test database and initialize schema."""
    # Use in-memory database for tests
    db.connect(":memory:")

    # Read and execute schema
    schema_path = Path(os.path.dirname(__file__)).parent / "scripts" / "init.sql"
    with open(schema_path) as f:
        db.executescript(f.read())

    yield db

    # Cleanup
    db.close()


@pytest.fixture
def sample_session():
    """Create a sample session for testing."""
    return Session(
        id="test_session_1",
        status=SessionStatus.ACTIVE,
    )


@pytest.fixture
def sample_tiktok():
    """Create a sample TikTok for testing."""
    return TikTokStats(
        title="Test TikTok",
        channel="Test Channel",
        channel_id="test_channel_1",
        channel_url="https://tiktok.com/@test_channel",
        tiktok_url="https://tiktok.com/@test_channel/video/1",
        thumbnail_url="https://tiktok.com/thumbnail/1",
        timestamp=1234567890,
        view_count=1000,
        like_count=100,
        repost_count=10,
        comment_count=50,
        duration=60,
        track="Test Track",
    )


@pytest.fixture
def sample_analysis():
    """Create a sample Analysis for testing."""
    return Analysis(
        transcript="Test transcript",
        analysis="Test analysis",
        tags=["test", "sample"],
        category=Category.ENTERTAINMENT,
        rating=5,
        like=True,
    )
