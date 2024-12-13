"""
main.py

poetry run python kronik/main.py
"""

import asyncio
import subprocess
import time
from time import sleep

import requests
from appium.webdriver import Remote

from kronik.control import control
from kronik.device.config import appium_driver, appium_server_url
from kronik.logger import app_logger as logger

EMULATOR_NAME = "KronikPixel"


def start_emulator():
    """
    Start the Android emulator.
    """
    logger.info("Starting Android emulator...")
    emulator_process = subprocess.Popen(
        ["emulator", "-avd", EMULATOR_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(5)  # Allow the emulator process to start
    logger.info("Waiting for the emulator to boot...")
    for _ in range(60):  # Wait up to 60 seconds
        try:
            result = subprocess.check_output(
                ["adb", "shell", "getprop", "sys.boot_completed"], stderr=subprocess.DEVNULL
            )
            if result.strip() == b"1":
                logger.info("Emulator booted successfully.")
                return emulator_process
        except subprocess.CalledProcessError:
            pass
        sleep(1)
    emulator_process.terminate()
    raise TimeoutError("Emulator did not boot within the timeout period.")


def start_appium_server():
    """
    Start the Appium server and wait for it to become ready.
    """
    logger.info("Starting Appium server...")
    appium_process = subprocess.Popen(
        ["appium", "--port", "4723"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    sleep(5)  # Allow the Appium server process to initialize

    logger.info("Waiting for the Appium server to be ready...")
    for _ in range(60):  # Wait up to 60 seconds
        try:
            # Check if the Appium server is responding
            response = requests.get(f"{appium_server_url()}/status", timeout=10)
            if response.status_code == 200:
                logger.info("Appium server is ready.")
                return appium_process
        except requests.exceptions.RequestException as exc:
            logger.debug(f"Appium server not ready yet: {exc}")
            sleep(1)
    appium_process.terminate()
    raise TimeoutError("Appium server did not start within the timeout period.")


async def main(driver: Remote):
    logger.info("Starting kronik")
    try:
        await control(driver=DRIVER)
    except Exception as exc:
        logger.error(f"Error in kronik: {str(exc)}", exc_info=True)
        raise


if __name__ == "__main__":
    _emulator_process = None
    _appium_process = None
    DRIVER = None
    try:
        # Start the emulator and Appium server
        _emulator_process = start_emulator()
        _appium_process = start_appium_server()

        # Initialize the Appium driver
        DRIVER = appium_driver()

        # Run the main async function
        asyncio.run(main(DRIVER))
    except KeyboardInterrupt:
        logger.info("Shutting down")
    except TimeoutError as te:
        logger.error(f"Timeout error: {te}")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        if DRIVER:
            DRIVER.quit()
        if _appium_process:
            _appium_process.terminate()
            logger.info("Appium server stopped.")
        if _emulator_process:
            _emulator_process.terminate()
            logger.info("Emulator stopped.")
