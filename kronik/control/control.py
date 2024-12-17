"""
kronik/control.py

This module contains the core logic to run the kronik agent.
It handles the device and brain integration and control.
"""

import asyncio
import time

from appium.webdriver import Remote

from kronik.control.tiktok import TikTokController
from kronik.device.app import SupportedApp, open_app, verify_app_installed
from kronik.device.commands import screenshot, start_screenrecord, stop_screenrecord
from kronik.logger import control_logger as logger
from kronik.session import Session
from kronik.utils import extract_audio, transcribe


async def control(driver: Remote, session: Session) -> None:
    # Verify all required apps are installed
    missing_apps = []
    for app in SupportedApp:
        if not verify_app_installed(driver, app):
            missing_apps.append(app.display_name)
    if missing_apps:
        raise Exception(f"Required apps not installed: {', '.join(missing_apps)}")

    recording_fp = start_screenrecord(driver, session)

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

    # Set up timing variables
    start_time = time.time()
    duration = 60  # Run for 60 seconds
    scroll_delay = 2  # Time between scrolls

    logger.info(f"Starting TikTok interaction loop for {duration} seconds")

    try:
        while time.time() - start_time < duration:
            # Like the video
            tiktok.like()

            # Take screenshot after interaction
            screenshot(driver, session)

            # Get current video link
            video_link = tiktok.get_link()
            if video_link:
                logger.info(f"Current video: {video_link}")

            # Scroll to next video
            tiktok.scroll_next()

            # Wait before next interaction
            await asyncio.sleep(scroll_delay)

            # Log remaining time periodically
            elapsed = time.time() - start_time
            remaining = duration - elapsed
            if int(remaining) % 10 == 0:  # Log every 10 seconds
                logger.info(f"Scrolling: {int(remaining)}s remaining")

    except Exception as e:
        logger.error(f"Error during TikTok interaction loop: {str(e)}")
        raise

    finally:
        # Stop recording and process the video
        recording_fp = stop_screenrecord(driver, session, recording_fp)
        if recording_fp is not None:
            audio_fp = extract_audio(recording_fp)
            if audio_fp is None:
                logger.warning("No audio stream found in the recording.")
            else:
                transcription = transcribe(audio_fp)
                logger.info(f"Transcription: {transcription}")
        else:
            logger.warning("No recording file path available for audio extraction.")

        logger.info("Completed all actions")
