from pydantic import BaseModel, HttpUrl


class TikTokStats(BaseModel):
    """TikTok Statistics"""

    title: str | None = None
    channel: str | None = None
    channel_id: str | None = None
    channel_url: HttpUrl | None = None
    tiktok_url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None
    timestamp: int | None = None
    view_count: int | None = None
    like_count: int | None = None
    repost_count: int | None = None
    comment_count: int | None = None
    duration: int | None = None
    track: str | None = None

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
