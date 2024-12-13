from datetime import datetime

from appium.webdriver import Remote

from kronik import DATA_DIR
from kronik.logger import commands_logger as logger


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


def screenshot(driver: Remote) -> str:
    """
    Take a screenshot and save it to data/screenshots directory.

    Returns:
        str: Path to the saved screenshot file
    """
    try:
        # Create screenshots directory if it doesn't exist
        screenshots_dir = DATA_DIR.joinpath("screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)

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
