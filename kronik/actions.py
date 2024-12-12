from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from kronik.logger import actions_logger as logger


def scroll_up(driver):
    logger.info("Scrolling up")

    # Get the window size
    window_size = driver.get_window_size()
    height, width = window_size["height"], window_size["width"]

    # Define start and end points for vertical scroll
    start_y = int(height * 0.75)
    end_y = int(height * 0.25)
    x = int(width / 2)

    # Initialize touch actions
    touch_input = PointerInput(interaction.POINTER_TOUCH, "finger")
    actions = ActionBuilder(driver, mouse=touch_input)

    # Scroll down to up
    actions.pointer_action.move_to_location(x, start_y)
    actions.pointer_action.pointer_down()
    actions.pointer_action.move_to_location(x, end_y)
    actions.pointer_action.pointer_up()
    actions.perform()


def scroll_down(driver):
    logger.info("Scrolling down")

    # Get the window size
    window_size = driver.get_window_size()
    height, width = window_size["height"], window_size["width"]

    # Define start and end points for vertical scroll
    start_y = int(height * 0.25)
    end_y = int(height * 0.75)
    x = int(width / 2)

    # Initialize touch actions
    touch_input = PointerInput(interaction.POINTER_TOUCH, "finger")
    actions = ActionBuilder(driver, mouse=touch_input)

    # Scroll down to up
    actions.pointer_action.move_to_location(x, start_y)
    actions.pointer_action.pointer_down()
    actions.pointer_action.move_to_location(x, end_y)
    actions.pointer_action.pointer_up()
    actions.perform()
