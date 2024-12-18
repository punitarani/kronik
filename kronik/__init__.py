"""kronik"""

from pathlib import Path

from dotenv import load_dotenv

from kronik.logger import app_logger as logger

PROJECT_ROOT = Path(__file__).parents[1]
DATA_DIR = PROJECT_ROOT.joinpath("data")

# Load environment variables
env_loaded = load_dotenv(PROJECT_ROOT.joinpath(".env"))
if not env_loaded:
    logger.error("No .env file found to load environment variables")
else:
    logger.info("Loaded environment variables from .env file")
