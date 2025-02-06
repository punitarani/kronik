import logging
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import yt_dlp
from pydantic import BaseModel

from kronik.logger import downloader_logger as logger
from kronik.models import TikTokStats


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

    async def download(self, url: str) -> Optional[tuple[Path, TikTokStats]]:
        """Downloads a TikTok video and returns its saved path and info asynchronously

        Args:
            url: TikTok video URL

        Returns:
            Tuple containing the path to the downloaded file and the info dictionary if successful,
            None otherwise
        """
        if not self._is_tiktok_url(url):
            self.logger.error(f"Failed to Download: Invalid TikTok URL - {url}")
            return None

        # Get the filename from the url
        output_path = self._get_output_path(url=url)
        self.logger.debug(f"Downloading: {url}")

        try:
            info = self._download_video(url, output_path)

            self.logger.info(f"Downloaded {url} to {output_path}")
            return output_path, TikTokStats.from_info(info=info)

        except Exception as e:
            self.logger.error(f"Failed to Download: {str(e)}")
            return None

    def _download_video(self, url: str, output_path: Path) -> dict:
        """Helper method to perform the actual download"""
        with yt_dlp.YoutubeDL(self._get_ydl_options(output_path)) as ydl:
            info = ydl.extract_info(url, download=True)
            return info

    @staticmethod
    def _is_tiktok_url(url: str) -> bool:
        """Checks if URL matches TikTok pattern"""
        return url.startswith(
            ("https://www.tiktok.com/", "https://vm.tiktok.com/", "https://vt.tiktok.com/")
        )

    def _get_output_path(self, url: str) -> Path:
        """Generates a unique output path based on the URL"""
        parsed_url = urlparse(url)

        # Get the path and split by '/' to extract the correct segment based on the URL structure
        path_segments = parsed_url.path.strip("/").split("/")
        if path_segments[0] == "t":
            fn = path_segments[1]  # Extract the ID for tiktok.com/t/ format
        elif len(path_segments) > 2 and path_segments[1] == "video":
            fn = path_segments[2]  # Extract the ID for tiktok.com/@handle/video/ format
        else:
            # Remove http(s):// and everything before first / after that
            cleaned_url = re.sub(r"^https?://[^/]+/", "", url)
            fn = re.sub(r"[^\w\-_.]", "_", cleaned_url)

        return self.config.save_dir.joinpath(f"{fn}.mp4")

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
