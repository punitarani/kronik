"""
kronik/control.py

This module contains the core logic to run the kronik agent.
It handles the device and brain integration and control.
"""

from time import sleep

from appium.webdriver import Remote

from kronik.device.actions import scroll_down, scroll_up
from kronik.device.commands import home, screenshot
from kronik.logger import control_logger as logger
from kronik.session import Session


async def control(driver: Remote, session: Session) -> None:
    # 1. Go to the home page and take a screenshot
    home(driver)
    screenshot(driver, session)

    # 2. Scroll up and take a screenshot
    scroll_up(driver)
    screenshot(driver, session)

    # 3. Wait 5 seconds
    logger.info("Waiting for 5 seconds")
    sleep(5)

    # 4. Scroll down and take a screenshot
    scroll_down(driver)
    screenshot(driver, session)

    logger.info("Completed all actions successfully")
