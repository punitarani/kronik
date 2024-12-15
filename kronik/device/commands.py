import base64
from datetime import datetime
from pathlib import Path

from appium.webdriver import Remote

from kronik.logger import commands_logger as logger
from kronik.session import Session, get_session_dir

# Global state for screen recording
_is_recording = False


def home(driver: Remote) -> None:
    """
    Navigate to the device's home screen.
    """
    try:
        logger.info("Navigating to home screen")
        driver.press_keycode(3)  # Android home key code
        logger.info("Successfully navigated to home screen")
    except Exception as e:
        logger.error(f"Failed to navigate to home screen: {str(e)}", exc_info=True)
        raise


def screenshot(driver: Remote, session: Session) -> str:
    """
    Take a screenshot and save it to the current session's screenshots directory.

    Args:
        driver: The Appium driver instance
        session: The current session instance

    Returns:
        str: Path to the saved screenshot file
    """
    try:
        # Use the session's directory to save the screenshot
        screenshots_dir = get_session_dir(session.id)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = screenshots_dir / filename

        logger.info(f"Taking screenshot: {filename}")

        # Take and save screenshot
        driver.get_screenshot_as_file(str(filepath))

        return str(filepath)

    except Exception as e:
        logger.error(f"Failed to take screenshot: {str(e)}", exc_info=True)
        raise


def start_screenrecord(driver: Remote, session: Session) -> Path | None:
    """
    Start screen recording using media projection.

    Args:
        driver: The Appium driver instance
        session: The current session instance

    Returns:
        Path: Recording filepath or None if recording is already in progress
    """
    global _is_recording

    try:
        if _is_recording:
            logger.warning("Screen recording is already in progress")
            return None

        # Use the session's directory to save the recording
        recordings_dir = get_session_dir(session.id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        filepath = recordings_dir.joinpath(filename)

        logger.info(f"Starting screen recording: {filename}")

        # Start recording with specific options for better reliability
        driver.start_recording_screen(
            videoSize="1920x1080",
            bitRate=8000000,
            forceRestart=True,
            audio=True,
        )

        _is_recording = True
        return filepath

    except Exception as exc:
        logger.error(f"Failed to start screen recording: {str(exc)}", exc_info=True)
        _is_recording = False
        raise


def stop_screenrecord(
    driver: Remote, session: Session, filepath: Path | None = None
) -> Path | None:
    """
    Stop the current screen recording and save it.

    Args:
        driver: The Appium driver instance
        session: The current session instance
        filepath: The filepath to save the recording to

    Returns:
        Path | None: Saved recording filepath or None
    """
    global _is_recording

    try:
        if not _is_recording:
            logger.warning("No screen recording in progress")
            return None

        logger.info(f"Stopping screen recording: {filepath}")

        # Stop recording and get base64 data
        base64_data = driver.stop_recording_screen()

        # Save the recording
        if filepath is None:
            recordings_dir = get_session_dir(session.id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"
            filepath = recordings_dir.joinpath(filename)

        # Decode and save the file
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(base64_data))

        logger.info(f"Screen recording saved: {filepath}")

        # Reset state
        _is_recording = False
        return filepath

    except Exception as e:
        logger.error(f"Failed to stop screen recording: {str(e)}", exc_info=True)
        _is_recording = False
        raise
