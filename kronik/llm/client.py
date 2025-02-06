import os

from google import genai

client = genai.Client(api_key=os.environ["GOOGLE_AI_API_KEY"])
