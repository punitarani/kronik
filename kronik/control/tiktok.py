from appium.webdriver import Remote
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from kronik.device.actions import scroll_up
from kronik.logger import control_logger as logger
from kronik.session import Session


class TikTokController:
    def __init__(self, driver: Remote, session: Session):
        self.driver: Remote = driver
        self.session: Session = session

        # Default 2s timeout for all waits
        self.wait = WebDriverWait(self.driver, 3)

    def like(self) -> bool:
        """Double tap to like tiktok."""
        try:
            # Get window size
            window_size = self.driver.get_window_size()
            height, width = window_size["height"], window_size["width"]

            # Calculate center point for double tap
            center_x = width // 2
            center_y = height // 2

            # Perform double tap using tap action
            for _ in range(2):
                self.driver.tap([(center_x, center_y)], 100)  # 100ms tap duration
                self.driver.implicitly_wait(0.1)  # 100ms pause between taps

            logger.debug("Double tap performed successfully")
            return True

        except WebDriverException as exc:
            logger.error(f"Error performing like action: {str(exc)}")
            return False

    def scroll_next(self) -> bool:
        """Scroll down to the next tiktok. Returns True if successful."""
        try:
            scroll_up(self.driver)
            return True
        except WebDriverException as exc:
            logger.error(f"Error scrolling to next video: {str(exc)}")
            return False

    def get_link(self) -> str | None:
        """Get the sharable link for the tiktok"""
        try:
            # Find and click share button using the working selector
            share_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@content-desc, 'Share')]"))
            )
            share_button.click()

            # Find and click copy link button using the working selector
            copy_link = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//android.widget.TextView[@text='Copy link']")
                )
            )
            copy_link.click()

            # Get the copied link from clipboard
            clipboard_text = self.driver.get_clipboard_text()
            if clipboard_text:
                logger.debug(f"Copied TikTok link: {clipboard_text}")
                return clipboard_text

            return None

        except TimeoutException:
            logger.warning("Timeout while trying to get TikTok link")
            return None
        except WebDriverException as exc:
            logger.error(f"Error getting TikTok link: {str(exc)}")
            return None
        finally:
            # Try to dismiss any open dialogs/sheets by tapping back
            try:
                self.driver.back()
            except WebDriverException:
                pass
