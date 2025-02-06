"""
Setup script for kronik.

This script handles all initialization tasks:
1. Creates necessary directories
2. Initializes databases
3. Checks dependencies
4. Validates environment
"""

import shutil
import sys

from kronik import DATA_DIR, PROJECT_ROOT
from kronik.logger import setup_logger
from kronik.store.client import db

logger = setup_logger(__name__)


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    if shutil.which("ffmpeg") is None:
        logger.error("ffmpeg is not installed. Please install it first.")
        sys.exit(1)
    logger.info("ffmpeg is installed")


def create_directories():
    """Create all necessary directories."""
    dirs = [
        DATA_DIR,
        DATA_DIR / "db",
        DATA_DIR / "sessions",
        DATA_DIR / "downloads",
        DATA_DIR / "logs",
    ]

    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def initialize_db():
    """Create and initialize the database using init.sql"""
    schema_path = PROJECT_ROOT.joinpath("scripts", "init.sql")

    logger.info("Initializing database")
    with open(schema_path) as f:
        db.executescript(f.read())
    db.commit()
    logger.info("Database initialized successfully")


def check_env():
    """Check if .env file exists with required variables."""
    env_path = PROJECT_ROOT / ".env"
    required_vars = [
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
    ]

    if not env_path.exists():
        logger.warning(".env file not found. Creating template...")
        with open(env_path, "w") as f:
            for var in required_vars:
                f.write(f"{var}=\n")
        logger.info(f"Please fill in your API keys in {env_path}")
        return False

    return True


def setup():
    """Run all setup tasks."""
    logger.info("Starting kronik setup...")

    # Check system dependencies
    check_ffmpeg()

    # Create necessary directories
    create_directories()

    # Initialize database
    initialize_db()

    # Check environment
    env_ready = check_env()

    if env_ready:
        logger.info("Setup completed successfully!")
    else:
        logger.warning("Setup completed with warnings. Please check the logs above.")


if __name__ == "__main__":
    setup()
