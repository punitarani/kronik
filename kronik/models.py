"""Models for kronik."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class SessionStatus(str, Enum):
    """Session status."""

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class Category(str, Enum):
    """Content category."""

    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    NEWS = "news"
    SPORTS = "sports"
    MUSIC = "music"
    GAMING = "gaming"
    FOOD = "food"
    FASHION = "fashion"
    TECH = "tech"
    OTHER = "other"


class Session(BaseModel):
    """Session model."""

    id: str
    status: SessionStatus
    created_at: Optional[datetime] = None


class TikTokStats(BaseModel):
    """TikTok Statistics"""

    title: Optional[str] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    channel_url: Optional[HttpUrl] = None
    tiktok_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    timestamp: Optional[int] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    repost_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration: Optional[int] = None
    track: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_info(cls, info: dict) -> "TikTokStats":
        # Get the best thumbnail
        for priority in ["cover", "originCover", "dynamicCover"]:
            thumbnail_url = next(
                (
                    thumbnail.get("url")
                    for thumbnail in info.get("thumbnails", [])
                    if thumbnail.get("id") == priority
                ),
                None,
            )
            if thumbnail_url:
                break

        return cls(
            title=info.get("title"),
            channel=info.get("channel"),
            channel_id=info.get("channel_id"),
            channel_url=info.get("channel_url"),
            tiktok_url=info.get("webpage_url"),
            thumbnail_url=thumbnail_url,
            timestamp=info.get("timestamp"),
            view_count=info.get("view_count"),
            like_count=info.get("like_count"),
            repost_count=info.get("repost_count"),
            comment_count=info.get("comment_count"),
            duration=info.get("duration"),
            track=info.get("track"),
        )


class Analysis(BaseModel):
    """Content analysis."""

    transcript: str
    analysis: str
    tags: List[str]
    category: Category
    rating: int
    like: bool
    created_at: Optional[datetime] = None
