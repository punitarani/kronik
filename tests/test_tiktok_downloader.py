from pathlib import Path
from shutil import rmtree
from unittest.mock import MagicMock, patch

import pytest

from kronik import PROJECT_ROOT
from kronik.models import TikTokStats
from kronik.utils.tiktok_downloader import DownloadConfig, TikTokDownloader


class TestTikTokDownloader:
    """Tests for TikTok video downloader"""

    TEST_URL = "https://www.tiktok.com/@tiktok/video/6635480525911887110"
    TEST_DATA_DIR = PROJECT_ROOT.joinpath("tests", "data", "tiktok_downloads")
    CLEANUP = True  # Set to `False` to keep test files for debugging
    ENABLE_LOGS = False  # Set to `True` to enable download logs

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment and downloader instance"""
        self.test_dir = self.TEST_DATA_DIR
        self.test_dir.mkdir(parents=True, exist_ok=True)

        config = DownloadConfig(
            save_dir=self.test_dir, use_chrome_cookies=False, logs=True
        )
        self.downloader = TikTokDownloader(config)

        yield

        if self.CLEANUP and self.test_dir.exists():
            rmtree(self.test_dir)

    def test_url_validation(self):
        """Tests URL validation for various TikTok URLs"""
        valid_urls = [self.TEST_URL]
        invalid_urls = [
            "https://not-tiktok.com/watch?v=123",
            "not_a_url",
        ]

        for url in valid_urls:
            assert self.downloader._is_tiktok_url(url)

        for url in invalid_urls:
            assert not self.downloader._is_tiktok_url(url)

    def test_output_path(self):
        """Tests output path generation"""
        path = self.downloader._get_output_path("test_video")

        assert path.parent == self.downloader.config.save_dir
        assert path.name.startswith("test_video")
        assert path.suffix == ".mp4"

    @pytest.mark.asyncio
    @patch("yt_dlp.YoutubeDL")
    async def test_successful_download(self, mock_ytdl):
        """Tests successful video download"""
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance

        # Mock the extract_info response with required fields
        mock_instance.extract_info.return_value = {
            "title": "Test Video",
            "channel": "Test Channel",
            "channel_id": "test123",
            "channel_url": "https://www.tiktok.com/@test",
            "webpage_url": "https://www.tiktok.com/@test/video/123",
            "track": "Test Track",
            "duration": 30,
            "view_count": 1000,
            "like_count": 100,
            "repost_count": 10,
            "comment_count": 50,
            "uploader": "test_user",
            "uploader_id": "test123",
            "description": "Test description",
            "upload_date": "20241221",
            "timestamp": 1703187600,
        }

        result = await self.downloader.download(self.TEST_URL)
        assert result is not None
        path, stats = result
        assert isinstance(path, Path)

    @pytest.mark.asyncio
    @patch("yt_dlp.YoutubeDL")
    async def test_download_failure(self, mock_ytdl):
        """Tests download failure handling"""
        mock_ytdl.return_value.__enter__.return_value.download.side_effect = Exception("Failed")

        result = await self.downloader.download(self.TEST_URL)
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_url(self):
        """Tests download with invalid URL"""
        result = await self.downloader.download("https://invalid-url.com")
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_download(self):
        """Tests TikTok video download and TikTokStats parsing"""
        info = {
            "title": "You made 2018 an AMAZING year. \nHow do we tell the story of 2018 in 2min? #tiktokrewind\n\n",
            "channel": "TikTok",
            "channel_id": "MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM",
            "channel_url": "https://www.tiktok.com/@MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM",
            "webpage_url": "https://www.tiktok.com/@tiktok/video/6635480525911887110",
            "thumbnails": [
                {"id": "dynamicCover", "url": "https://example.com/dynamic_cover.jpg"},
                {
                    "id": "cover",
                    "url": "https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/3ea3effcf88849a58f60e91635e420ae",
                },
                {"id": "originCover", "url": "https://example.com/origin_cover.jpg"},
            ],
            "timestamp": 1544943202,
            "view_count": 7300000,
            "like_count": 953100,
            "repost_count": 26000,
            "comment_count": 17600,
            "duration": 137,
            "track": "original sound",
        }

        result = await self.downloader.download(self.TEST_URL)
        assert result is not None

        dl_fp, stats = result

        assert dl_fp.exists()
        assert dl_fp.stat().st_size > 0

        assert isinstance(stats, TikTokStats)
        assert stats.title == info["title"]
        assert stats.channel == info["channel"]
        assert stats.channel_id == info["channel_id"]
        assert str(stats.channel_url) == info["channel_url"]
        assert str(stats.tiktok_url) == info["webpage_url"]
        assert str(stats.thumbnail_url).split("?")[0] == info["thumbnails"][1]["url"]
        assert stats.timestamp == info["timestamp"]
        assert stats.view_count >= info["view_count"]
        assert stats.like_count >= info["like_count"]
        assert stats.repost_count >= info["repost_count"]
        assert stats.comment_count >= info["comment_count"]
        assert stats.duration == info["duration"]
        assert stats.track == info["track"]
