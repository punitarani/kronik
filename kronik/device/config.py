from appium.options.android import UiAutomator2Options
from appium.options.common import AppiumOptions
from appium.webdriver import Remote


def appium_server_url():
    return "http://localhost:4723"


def appium_options() -> AppiumOptions:
    options = UiAutomator2Options()

    options.platformName = "Android"
    options.automationName = "uiautomator2"
    options.deviceName = "KronikPixel"
    options.appPackage = "com.android.settings"
    options.appActivity = ".Settings"
    options.language = "en"
    options.locale = "US"

    return options


def appium_driver(
    url: str = appium_server_url(), options: AppiumOptions = appium_options()
) -> Remote:
    return Remote(url, options=options)
