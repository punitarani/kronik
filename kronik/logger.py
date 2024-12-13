import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[int] = logging.INFO) -> logging.Logger:
    """
    Set up a logger with a specific format and configuration.

    Format: [LEVEL] timestamp - logger_name - message
    """
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent propagation to parent loggers

    if not logger.handlers:  # Avoid adding handlers multiple times
        logger.setLevel(level)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s - %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Add formatter to handler
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    return logger


# Create main application logger
app_logger = setup_logger("kronik")

# Create sub-loggers for different modules
actions_logger = setup_logger("kronik.actions")
brain_logger = setup_logger("kronik.brain")
commands_logger = setup_logger("kronik.commands")
