from pathlib import Path

from google.genai.types import (
    GenerateContentConfig,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    SafetySetting,
)

from kronik.llm.client import client
from kronik.logger import brain_logger as logger
from kronik.models import Analysis, Category

from .prompts import analyze_tiktok_prompt


def _analyze_tiktok_generation_config() -> GenerateContentConfig:
    response_schema = {
        "type": "OBJECT",
        "required": ["transcript", "analysis", "tags", "category", "rating", "like"],
        "properties": {
            "transcript": {"type": "STRING"},
            "analysis": {"type": "STRING"},
            "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
            "category": {
                "type": "STRING",
                "enum": [category.value for category in Category],
            },
            "rating": {"type": "INTEGER"},
            "like": {"type": "BOOLEAN"},
        },
    }

    harm_categories = [category.value for category in HarmCategory]

    safety_settings = [
        SafetySetting(
            category=harm_category,
            threshold=HarmBlockThreshold.BLOCK_NONE,
        )
        for harm_category in harm_categories
    ]

    generation_config = GenerateContentConfig(
        system_instruction=analyze_tiktok_prompt,
        temperature=1.5,
        safety_settings=safety_settings,
        response_schema=response_schema,
        response_mime_type="application/json",
    )

    return generation_config


async def analyze_tiktok(tiktok_fp: Path) -> Analysis | None:
    """
    Analyze a TikTok
    """
    logger.info(f"Starting TikTok analysis for: {tiktok_fp}")

    # Ensure the file exists
    if not tiktok_fp.exists():
        logger.error(f"TikTok file not found: {tiktok_fp}")
        raise FileNotFoundError(f"File not found: {tiktok_fp}")

    logger.debug(f"Reading TikTok file: {tiktok_fp}")
    with open(tiktok_fp, "rb") as f:
        tiktok_bytes = f.read()

    tiktok_content = Part.from_bytes(
        data=tiktok_bytes,
        mime_type="video/mp4",
    )
    logger.debug("Created TikTok content part for Gemini")

    logger.info("Sending TikTok to Gemini for analysis")
    try:
        response = await client.aio.models.generate_content(
            model="gemini-1.5-flash-8b",
            contents=[
                "Please analyze this TikTok video from the persona's perspective.",
                # TODO: Add metadata content
                tiktok_content,
            ],
            config=_analyze_tiktok_generation_config(),
        )
        logger.debug(
            f"Successfully received response from Gemini: {response.candidates[0].content.parts[0].text}"
        )
        return Analysis.model_validate_json(response.candidates[0].content.parts[0].text)

    except Exception as e:
        logger.error(f"Error during TikTok analysis: {str(e)}")
        raise
