"""
main.py

poetry run python kronik/main.py
"""

import asyncio
from time import sleep

from appium.webdriver import Remote

from kronik.actions import scroll_down, scroll_up
from kronik.commands import home, screenshot
from kronik.config import appium_driver
from kronik.logger import app_logger as logger

DRIVER = appium_driver()


async def main(driver: Remote = DRIVER):
    logger.info("Starting kronik")
    try:
        # 1. Go to home page and take screenshot
        home(driver)
        screenshot(driver)

        # 2. Scroll up and take screenshot
        scroll_up(driver)
        screenshot(driver)

        # 3. Wait 5 seconds
        logger.info("Waiting for 5 seconds")
        sleep(5)

        # 4. Scroll down and take screenshot
        scroll_down(driver)
        screenshot(driver)

        logger.info("Completed all actions successfully")

    except Exception as e:
        logger.error(f"Error in kronik: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down")
        DRIVER.quit()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        DRIVER.quit()
        raise
