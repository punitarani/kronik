import asyncio
import logging
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Optional

import yt_dlp
from pydantic import BaseModel

from kronik.logger import downloader_logger as logger


class DownloadConfig(BaseModel):
    """Configuration for downloading TikTok videos"""

    save_dir: Path
    use_chrome_cookies: bool = True
    format: str = "best"
    resolution: str = "720"
    logs: bool = True


class TikTokDownloader:
    """Downloads TikTok videos with error handling and logging"""

    def __init__(self, config: DownloadConfig):
        self.config = config
        self.config.save_dir.mkdir(parents=True, exist_ok=True)

        # Configure logger based on config
        self.logger = logger if config.logs else logging.getLogger("disabled")
        if not config.logs:
            self.logger.disabled = True

    async def download(self, url: str, name: str) -> Optional[Path]:
        """Downloads a TikTok video and returns its saved path asynchronously

        Args:
            url: TikTok video URL
            name: Base name for the saved file

        Returns:
            Path to the downloaded file if successful, None otherwise
        """
        if not self._is_tiktok_url(url):
            self.logger.error(f"Failed to Download: Invalid TikTok URL - {url}")
            return None

        output_path = self._get_output_path(name)
        self.logger.debug(f"Downloading: {url}")

        try:
            # Run yt-dlp download in a thread pool to avoid blocking
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, partial(self._download_video, url, output_path))

            self.logger.info(f"Downloaded {url} to {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to Download: {str(e)}")
            return None

    def _download_video(self, url: str, output_path: Path) -> None:
        """Helper method to perform the actual download"""
        with yt_dlp.YoutubeDL(self._get_ydl_options(output_path)) as ydl:
            ydl.download([url])

    @staticmethod
    def _is_tiktok_url(url: str) -> bool:
        """Checks if URL matches TikTok pattern"""
        return url.startswith(
            ("https://www.tiktok.com/", "https://vm.tiktok.com/", "https://vt.tiktok.com/")
        )

    def _get_output_path(self, name: str) -> Path:
        """Generates unique output path with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.config.save_dir / f"{name}_{timestamp}.mp4"

    def _get_ydl_options(self, output_path: Path) -> dict:
        """Returns yt-dlp options for downloading"""
        options = {
            "outtmpl": str(output_path),
            "format": self.config.format,
            "resolution": self.config.resolution,
            "quiet": True,
            "no_warnings": True,
            "extractor_args": {"tiktok": {"webpage_download": True}},
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            },
            "logger": None,
        }

        if self.config.use_chrome_cookies:
            options["cookiesfrombrowser"] = ("chrome",)

        return options
