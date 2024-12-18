import os

from google import genai

from kronik.logger import brain_logger as logger

logger.debug("Initializing Google Gen AI Client")
client = genai.Client(api_key=os.environ["GOOGLE_AI_API_KEY"])
