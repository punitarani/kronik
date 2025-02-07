"""Store for managing TikTok and Analysis data in SQLite."""

import json
from datetime import datetime
from sqlite3 import IntegrityError
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from pydantic import HttpUrl

from kronik.models import Analysis, TikTokStats
from kronik.store.client import db


def _validate_url(url: Optional[str | HttpUrl]) -> Optional[str]:
    """Validate and normalize URL.

    Args:
        url: URL to validate

    Returns:
        Normalized URL string if valid, None otherwise
    """
    if not url:
        return None
    try:
        # Convert to string if HttpUrl
        url_str = str(url)
        # Parse URL to validate
        result = urlparse(url_str)
        if not all([result.scheme, result.netloc]):
            return None
        return url_str
    except Exception:
        return None


class TikTokStore:
    """Handles all TikTok and Analysis related database operations."""

    def create(self, tiktok: TikTokStats, session_id: str) -> int:
        """Create a new TikTok record.

        Args:
            tiktok: TikTok stats to store
            session_id: Associated session ID

        Returns:
            ID of created TikTok record

        Raises:
            IntegrityError: If TikTok with same URL already exists
            ValueError: If TikTok URL is invalid
        """
        # Validate URLs
        tiktok_url = _validate_url(tiktok.tiktok_url)
        if not tiktok_url:
            raise ValueError("Invalid TikTok URL")

        channel_url = _validate_url(tiktok.channel_url)
        thumbnail_url = _validate_url(tiktok.thumbnail_url)

        with db.transaction():
            query = """
                INSERT INTO tiktok (
                    title, channel, channel_id, channel_url, tiktok_url,
                    thumbnail_url, timestamp, view_count, like_count,
                    repost_count, comment_count, duration, track, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor = db.execute(
                query,
                (
                    tiktok.title,
                    tiktok.channel,
                    tiktok.channel_id,
                    channel_url,
                    tiktok_url,
                    thumbnail_url,
                    tiktok.timestamp,
                    tiktok.view_count,
                    tiktok.like_count,
                    tiktok.repost_count,
                    tiktok.comment_count,
                    tiktok.duration,
                    tiktok.track,
                    session_id,
                ),
            )
            return cursor.lastrowid

    def get(self, tiktok_id: int) -> Optional[Tuple[TikTokStats, Optional[Analysis]]]:
        """Retrieve a TikTok and its analysis by ID.

        Args:
            tiktok_id: TikTok record ID

        Returns:
            Tuple of (TikTokStats, Analysis) if found, None if TikTok not found.
            Analysis may be None if it doesn't exist yet.
        """
        query = """
            SELECT t.id, t.title, t.channel, t.channel_id, t.channel_url, t.tiktok_url,
                   t.thumbnail_url, t.timestamp, t.view_count, t.like_count,
                   t.repost_count, t.comment_count, t.duration, t.track, t.created_at,
                   a.transcript, a.analysis, a.tags, a.category, a.rating, a.like, a.created_at
            FROM tiktok t
            LEFT JOIN analysis a ON t.id = a.tiktok_id
            WHERE t.id = ?
        """
        result = db.execute(query, (tiktok_id,)).fetchone()

        if not result:
            return None

        tiktok = TikTokStats(
            title=result[1],
            channel=result[2],
            channel_id=result[3],
            channel_url=result[4],
            tiktok_url=result[5],
            thumbnail_url=result[6],
            timestamp=result[7],
            view_count=result[8],
            like_count=result[9],
            repost_count=result[10],
            comment_count=result[11],
            duration=result[12],
            track=result[13],
            created_at=result[14],
        )

        analysis = None
        if result[15]:  # If transcript exists, we have analysis
            analysis = Analysis(
                transcript=result[15],
                analysis=result[16],
                tags=json.loads(result[17]) if result[17] else [],
                category=result[18],
                rating=result[19],
                like=result[20],
                created_at=result[21],
            )

        return tiktok, analysis

    def list_tiktoks_from_session(
        self, session_id: str, limit: int = 100
    ) -> List[Tuple[TikTokStats, Optional[Analysis]]]:
        """List all TikToks and their analyses for a session.

        Args:
            session_id: Session to get TikToks for
            limit: Maximum number of TikToks to return

        Returns:
            List of (TikTokStats, Analysis) tuples. Analysis may be None if not analyzed yet.
        """
        query = """
            SELECT t.id, t.title, t.channel, t.channel_id, t.channel_url, t.tiktok_url,
                   t.thumbnail_url, t.timestamp, t.view_count, t.like_count,
                   t.repost_count, t.comment_count, t.duration, t.track, t.created_at,
                   a.transcript, a.analysis, a.tags, a.category, a.rating, a.like, a.created_at
            FROM tiktok t
            LEFT JOIN analysis a ON t.id = a.tiktok_id
            WHERE t.session_id = ?
            ORDER BY t.created_at DESC
            LIMIT ?
        """
        results = db.execute(query, (session_id, limit)).fetchall()

        return [
            (
                TikTokStats(
                    title=row[1],
                    channel=row[2],
                    channel_id=row[3],
                    channel_url=row[4],
                    tiktok_url=row[5],
                    thumbnail_url=row[6],
                    timestamp=row[7],
                    view_count=row[8],
                    like_count=row[9],
                    repost_count=row[10],
                    comment_count=row[11],
                    duration=row[12],
                    track=row[13],
                    created_at=row[14],
                ),
                (
                    Analysis(
                        transcript=row[15],
                        analysis=row[16],
                        tags=json.loads(row[17]) if row[17] else [],
                        category=row[18],
                        rating=row[19],
                        like=row[20],
                        created_at=row[21],
                    )
                    if row[15]
                    else None
                ),
            )
            for row in results
        ]

    def add_analysis(self, analysis: Analysis, tiktok_id: int) -> bool:
        """Add or update analysis for a TikTok.

        Args:
            analysis: Analysis to store
            tiktok_id: Associated TikTok ID

        Returns:
            True if analysis was added/updated, False if TikTok not found

        Raises:
            IntegrityError: If TikTok doesn't exist
        """
        with db.transaction():
            # Check if TikTok exists
            check_query = "SELECT id FROM tiktok WHERE id = ?"
            if not db.execute(check_query, (tiktok_id,)).fetchone():
                raise IntegrityError("TikTok does not exist")

            # Try to update first (in case analysis exists)
            update_query = """
                UPDATE analysis 
                SET transcript = ?, analysis = ?, tags = ?,
                    category = ?, rating = ?, like = ?
                WHERE tiktok_id = ?
            """
            cursor = db.execute(
                update_query,
                (
                    analysis.transcript,
                    analysis.analysis,
                    json.dumps(analysis.tags),  # Convert list to JSON string
                    analysis.category.value,
                    analysis.rating,
                    analysis.like,
                    tiktok_id,
                ),
            )

            # If no rows were updated, insert new analysis
            if cursor.rowcount == 0:
                insert_query = """
                    INSERT INTO analysis (
                        transcript, analysis, tags, category,
                        rating, like, tiktok_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                db.execute(
                    insert_query,
                    (
                        analysis.transcript,
                        analysis.analysis,
                        json.dumps(analysis.tags),  # Convert list to JSON string
                        analysis.category.value,
                        analysis.rating,
                        analysis.like,
                        tiktok_id,
                    ),
                )

            return True

    def delete(self, tiktok_id: int) -> bool:
        """Delete a TikTok and its analysis.

        Args:
            tiktok_id: TikTok to delete

        Returns:
            True if TikTok was deleted, False if not found
        """
        with db.transaction():
            # Check if TikTok exists
            check_query = "SELECT id FROM tiktok WHERE id = ?"
            if not db.execute(check_query, (tiktok_id,)).fetchone():
                return False

            # Delete TikTok (cascade will handle analysis)
            query = """
                DELETE FROM tiktok
                WHERE id = ?
            """
            db.execute(query, (tiktok_id,))
            return True

    def get_by_url(self, url: str) -> Optional[Tuple[TikTokStats, Optional[Analysis]]]:
        """Find a TikTok and its analysis by URL.

        Args:
            url: TikTok URL to search for

        Returns:
            Tuple of (TikTokStats, Analysis) if found, None if not found.
            Analysis may be None if it doesn't exist yet.
        """
        # Validate URL
        tiktok_url = _validate_url(url)
        if not tiktok_url:
            return None

        query = """
            SELECT t.id, t.title, t.channel, t.channel_id, t.channel_url, t.tiktok_url,
                   t.thumbnail_url, t.timestamp, t.view_count, t.like_count,
                   t.repost_count, t.comment_count, t.duration, t.track, t.created_at,
                   a.transcript, a.analysis, a.tags, a.category, a.rating, a.like, a.created_at
            FROM tiktok t
            LEFT JOIN analysis a ON t.id = a.tiktok_id
            WHERE t.tiktok_url = ?
        """
        result = db.execute(query, (tiktok_url,)).fetchone()

        if not result:
            return None

        tiktok = TikTokStats(
            title=result[1],
            channel=result[2],
            channel_id=result[3],
            channel_url=result[4],
            tiktok_url=result[5],
            thumbnail_url=result[6],
            timestamp=result[7],
            view_count=result[8],
            like_count=result[9],
            repost_count=result[10],
            comment_count=result[11],
            duration=result[12],
            track=result[13],
            created_at=result[14],
        )

        analysis = None
        if result[15]:  # If transcript exists, we have analysis
            analysis = Analysis(
                transcript=result[15],
                analysis=result[16],
                tags=json.loads(result[17]) if result[17] else [],
                category=result[18],
                rating=result[19],
                like=result[20],
                created_at=result[21],
            )

        return tiktok, analysis
