from enum import Enum
from typing import Optional

from appium.webdriver import Remote

from kronik.logger import control_logger as logger


class SupportedApp(Enum):
    TIKTOK = ("com.zhiliaoapp.musically", "TikTok")
    # INSTAGRAM = ("com.instagram.android", "Instagram")

    def __init__(self, package_id: str, display_name: str):
        self.package_id = package_id
        self.display_name = display_name


def open_app(driver: Remote, app: SupportedApp, wait_time: Optional[int] = 10) -> bool:
    """
    Open the specified app and verify it launched successfully.

    Args:
        driver: Appium driver instance
        app: SupportedApp enum value
        wait_time: Time to wait for app to load in seconds

    Returns:
        bool: True if app opened successfully, False otherwise

    Raises:
        Exception: If app fails to launch properly
    """
    try:
        logger.info(f"Launching {app.display_name}...")
        driver.activate_app(app.package_id)

        # Wait for app to be ready
        if wait_time:
            driver.implicitly_wait(wait_time)

        # Verify we're in the correct app
        if app.package_id.lower() not in driver.current_package.lower():
            raise Exception(
                f"Failed to launch {app.display_name}",
                f"Current package: {driver.current_package.lower()}",
            )

        logger.debug(f"{app.display_name} launched successfully")
        return True

    except Exception as e:
        logger.error(f"Error launching {app.display_name}: {str(e)}")
        raise


def verify_app_installed(driver: Remote, app: SupportedApp) -> bool:
    """
    Verify if the specified app is installed on the device.

    Args:
        driver: Appium driver instance
        app: SupportedApp enum value

    Returns:
        bool: True if app is installed, False otherwise
    """
    try:
        return driver.is_app_installed(app.package_id)
    except Exception as e:
        logger.error(f"Error checking if {app.display_name} is installed: {str(e)}")
        return False
