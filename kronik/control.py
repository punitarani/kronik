"""
kronik/control.py

This module contains the core logic to run the kronik agent.
It handles the device and brain integration and control.
"""

from time import sleep

from appium.webdriver import Remote

from kronik.device.actions import scroll_down, scroll_up
from kronik.device.commands import (
    home,
    screenshot,
    start_screenrecord,
    stop_screenrecord,
)
from kronik.logger import control_logger as logger
from kronik.session import Session
from kronik.utils import extract_audio, transcribe


async def control(driver: Remote, session: Session) -> None:
    recording_fp = start_screenrecord(driver, session)

    # 1. Go to the home page and take a screenshot
    home(driver)
    screenshot(driver, session)

    # 2. Scroll up and take a screenshot
    scroll_up(driver)
    screenshot(driver, session)

    # 3. Wait 2 seconds
    logger.info("Waiting for 2 seconds")
    sleep(2)

    # 4. Scroll down and take a screenshot
    scroll_down(driver)
    screenshot(driver, session)

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

    logger.info("Completed all actions successfully")
