from datetime import datetime

from appium.webdriver import Remote

from kronik.logger import commands_logger as logger
from kronik.session import Session, get_session_dir


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
