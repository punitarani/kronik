"""
kronik/control.py

This module contains the core logic to run the kronik agent.
It handles the device and brain integration and control.
"""

import asyncio
import json
from pathlib import Path

from appium.webdriver import Remote

from kronik.brain.models import TikTokAnalysis
from kronik.brain.tiktok import analyze_tiktok
from kronik.control.tiktok import TikTokController
from kronik.device.app import SupportedApp, open_app, verify_app_installed
from kronik.device.commands import screenshot, start_screenrecord, stop_screenrecord
from kronik.logger import control_logger as logger
from kronik.session import Session


class TikTokAnalysisEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TikTokAnalysis):
            return {
                "transcript": obj.transcript,
                "analysis": obj.analysis,
                "tags": obj.tags,
                "category": obj.category.value,
                "rating": obj.rating,
                "like": obj.like,
            }
        return super().default(obj)


async def control(driver: Remote, session: Session) -> None:
    # Verify all required apps are installed
    missing_apps = []
    for app in SupportedApp:
        if not verify_app_installed(driver, app):
            missing_apps.append(app.display_name)
    if missing_apps:
        raise Exception(f"Required apps not installed: {', '.join(missing_apps)}")

    # Launch TikTok app and wait for it to load
    try:
        open_app(driver, SupportedApp.TIKTOK)
    except Exception as e:
        logger.error(f"Error launching TikTok: {str(e)}")
        raise

    # Initialize TikTok controller
    tiktok = TikTokController(driver, session)

    # Take initial screenshot
    screenshot(driver, session)

    logger.info("Starting infinite TikTok interaction loop")

    try:
        while True:  # Infinite loop
            # Take a screenshot and start recording for 10 seconds
            screenshot(driver, session)
            recording_fp = start_screenrecord(driver, session)
            await asyncio.sleep(10)
            recording_fp = stop_screenrecord(driver, session, recording_fp)

            if recording_fp is None:
                logger.error("Failed to get recording file")
                continue

            # Analyze the TikTok
            try:
                analysis = await analyze_tiktok(Path(recording_fp))
                if analysis:
                    # Save analysis to JSON
                    recording_path = Path(recording_fp)
                    json_path = recording_path.with_suffix(".json")
                    with open(json_path, "w") as f:
                        json.dump(analysis, f, indent=2, cls=TikTokAnalysisEncoder)

                    # Like the video if the analysis suggests it
                    if analysis.like:
                        tiktok.like()
                        logger.info("Liked video based on analysis")

            except Exception as e:
                logger.error(f"Error during TikTok analysis: {str(e)}")

            # Get the current video link
            video_link = tiktok.get_link()
            if video_link:
                logger.info(f"Current video: {video_link}")

            # Scroll to next video
            tiktok.scroll_next()
            await asyncio.sleep(1)  # Brief pause between videos

    except Exception as e:
        logger.error(f"Error during TikTok interaction loop: {str(e)}")
        raise

    finally:
        logger.info("Completed all actions")
