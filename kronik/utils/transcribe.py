import logging
from pathlib import Path

import mlx_whisper

logger = logging.getLogger(__name__)


def transcribe(speech_fp: Path) -> str:
    """Transcribe a speech file using MLX Whisper."""
    logger.info(f"Starting transcription of file: {speech_fp}")
    try:
        result = mlx_whisper.transcribe(str(speech_fp))
        text = result["text"]
        logger.info(f"Successfully transcribed file: {speech_fp}")
        return text
    except Exception as e:
        logger.error(f"Error transcribing file {speech_fp}: {str(e)}")
        raise
