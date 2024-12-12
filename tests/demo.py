import unittest
from time import sleep, time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

# Define Appium server URL
appium_server_url = "http://localhost:4723"

# Set up desired capabilities using UiAutomator2Options
options = UiAutomator2Options()
options.platformName = "Android"
options.automationName = "uiautomator2"
options.deviceName = "KronikPixel"
options.appPackage = "com.android.settings"
options.appActivity = ".Settings"
options.language = "en"
options.locale = "US"


class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, options=options)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_vertical_scroll(self) -> None:
        # Get the window size
        window_size = self.driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]

        # Define start and end points for vertical scroll
        start_y = int(height * 0.8)
        end_y = int(height * 0.2)
        x = int(width / 2)

        # Initialize touch actions
        touch_input = PointerInput(interaction.POINTER_TOUCH, "finger")
        actions = ActionBuilder(self.driver, mouse=touch_input)

        # Perform vertical scrolls for 60 seconds
        end_time = time() + 60
        while time() < end_time:
            # Scroll down to up
            actions.pointer_action.move_to_location(x, start_y)
            actions.pointer_action.pointer_down()
            actions.pointer_action.move_to_location(x, end_y)
            actions.pointer_action.pointer_up()
            actions.perform()
            sleep(1)

            # Scroll up to down
            actions.pointer_action.move_to_location(x, end_y)
            actions.pointer_action.pointer_down()
            actions.pointer_action.move_to_location(x, start_y)
            actions.pointer_action.pointer_up()
            actions.perform()
            sleep(1)


if __name__ == "__main__":
    unittest.main()
