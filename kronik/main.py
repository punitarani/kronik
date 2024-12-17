"""
main.py

Usage: poetry run python kronik/main.py [--skip-device]
"""

import argparse
import asyncio
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import requests
from appium.webdriver import Remote
from dotenv import load_dotenv

from kronik import PROJECT_ROOT
from kronik.control import control
from kronik.device.config import appium_driver, appium_server_url
from kronik.logger import app_logger as logger
from kronik.session import Session, save_session_metadata


@dataclass
class DeviceSetup:
    """Class to manage device and server processes."""

    emulator_process: Optional[subprocess.Popen] = None
    appium_process: Optional[subprocess.Popen] = None
    driver: Optional[Remote] = None

    def cleanup(self) -> None:
        """Clean up all running processes."""
        if self.driver:
            self.driver.quit()
        if self.appium_process:
            self.appium_process.terminate()
            logger.info("Appium server stopped.")
        if self.emulator_process:
            self.emulator_process.terminate()
            logger.info("Emulator stopped.")


class DeviceManager:
    """Manages device setup and initialization."""

    EMULATOR_NAME = "KronikPixel"
    BOOT_TIMEOUT = 60
    APPIUM_PORT = "4723"

    @classmethod
    def _is_emulator_booted(cls) -> bool:
        """Check if emulator is booted and responsive."""
        try:
            result = subprocess.check_output(
                ["adb", "shell", "getprop", "sys.boot_completed"], stderr=subprocess.DEVNULL
            )
            return result.strip() == b"1"
        except subprocess.CalledProcessError:
            return False

    @classmethod
    def _is_appium_responsive(cls) -> bool:
        """Check if Appium server is running and responsive."""
        try:
            response = requests.get(f"{appium_server_url()}/status", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    @classmethod
    def check_emulator_running(cls) -> None:
        """Check if emulator is running and fully booted."""
        if not cls._is_emulator_booted():
            raise RuntimeError(
                "No running emulator found. Please start the emulator first when using --skip-device"
            )
        logger.info("Found running emulator")

    @classmethod
    def check_appium_running(cls) -> None:
        """Check if Appium server is running and responding."""
        if not cls._is_appium_responsive():
            raise RuntimeError(
                "No running Appium server found. Please start Appium first when using --skip-device"
            )
        logger.info("Found running Appium server")

    @classmethod
    def start_emulator(cls) -> subprocess.Popen:
        """Start and wait for Android emulator to boot."""
        logger.info("Starting Android emulator...")
        emulator_process = subprocess.Popen(
            ["emulator", "-avd", cls.EMULATOR_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(5)  # Allow initial process startup

        logger.info("Waiting for the emulator to boot...")
        for _ in range(cls.BOOT_TIMEOUT):
            if cls._is_emulator_booted():
                logger.info("Emulator booted successfully.")
                return emulator_process
            time.sleep(1)

        emulator_process.terminate()
        raise TimeoutError("Emulator did not boot within the timeout period.")

    @classmethod
    def start_appium_server(cls) -> subprocess.Popen:
        """Start and wait for Appium server to be ready."""
        logger.info("Starting Appium server...")
        appium_process = subprocess.Popen(
            ["appium", "--port", cls.APPIUM_PORT], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(5)  # Allow initial process startup

        logger.info("Waiting for the Appium server to be ready...")
        for _ in range(cls.BOOT_TIMEOUT):
            if cls._is_appium_responsive():
                logger.info("Appium server is ready.")
                return appium_process
            time.sleep(1)

        appium_process.terminate()
        raise TimeoutError("Appium server did not start within the timeout period.")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Kronik automation tool")
    parser.add_argument("--skip-device", action="store_true", help="Skip emulator and appium setup")
    return parser.parse_args()


async def main() -> None:
    """Main application logic."""
    logger.info("Starting kronik")
    args = parse_args()
    device_setup = DeviceSetup()
    session = None

    # Load environment variables
    env_loaded = load_dotenv(PROJECT_ROOT.joinpath(".env"))
    if not env_loaded:
        logger.error("No .env file found to load environment variables")
    else:
        logger.info("Loaded environment variables from .env file")

    try:
        # Initialize session
        session = Session()
        save_session_metadata(session)
        logger.info(f"Starting new session: {session.id}")

        # Start the emulator and Appium server if not skipped
        if not args.skip_device:
            device_setup.emulator_process = DeviceManager.start_emulator()
            device_setup.appium_process = DeviceManager.start_appium_server()
        # Else, check if the emulator and Appium server are already running
        else:
            DeviceManager.check_emulator_running()
            DeviceManager.check_appium_running()

        # Start Appium driver
        device_setup.driver = appium_driver()

        # Run the control async function
        await control(device_setup.driver, session)

    except KeyboardInterrupt:
        logger.info("Shutting down")
    except TimeoutError as te:
        logger.error(f"Timeout error: {te}")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        if session:
            session.close()
            save_session_metadata(session)
        device_setup.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
