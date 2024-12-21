from pathlib import Path
from shutil import rmtree
from unittest.mock import MagicMock, patch

import pytest

from kronik import PROJECT_ROOT
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
            save_dir=self.test_dir, use_chrome_cookies=False, logs=True  # Disable logging in tests
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

        result = await self.downloader.download(self.TEST_URL, "test_tiktok_success")

        assert isinstance(result, Path)
        assert mock_instance.download.called

    @pytest.mark.asyncio
    @patch("yt_dlp.YoutubeDL")
    async def test_download_failure(self, mock_ytdl):
        """Tests download failure handling"""
        mock_ytdl.return_value.__enter__.return_value.download.side_effect = Exception("Failed")

        result = await self.downloader.download(self.TEST_URL, "test_tiktok_failure")
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_url(self):
        """Tests download with invalid URL"""
        result = await self.downloader.download("https://invalid-url.com", "test_tiktok_invalid")
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_integration(self):
        """Tests actual TikTok video download"""
        result = await self.downloader.download(self.TEST_URL, "test_tiktok_integration")

        assert result is not None
        assert result.exists()
        assert result.stat().st_size > 0
