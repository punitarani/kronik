from pathlib import Path

import ffmpeg

from kronik.logger import setup_logger

logger = setup_logger(__name__)


def has_audio_stream(video_fp: Path) -> bool:
    """
    Check if the video file contains an audio stream.

    Args:
        video_fp (Path): Path to the video file

    Returns:
        bool: True if the video has an audio stream, False otherwise
    """
    try:
        probe = ffmpeg.probe(str(video_fp))
        return any(stream["codec_type"] == "audio" for stream in probe["streams"])
    except ffmpeg.Error:
        return False


def extract_audio(video_fp: Path, bitrate: str = "192k", codec: str = "libmp3lame") -> Path | None:
    """
    Extract audio from a video file using ffmpeg-python and save it as MP3.
    Returns None if no audio stream is found.

    Args:
        video_fp (Path): Path to the input video file.
        bitrate (str, optional): Audio bitrate. Defaults to '192k'.
        codec (str, optional): Audio codec to use. Defaults to 'libmp3lame'.

    Returns:
        Path | None: Path to the extracted audio file, or None if no audio stream exists

    Raises:
        FileNotFoundError: If input video file doesn't exist.
        RuntimeError: If output file creation fails.
    """
    # Ensure video_fp is a Path object
    video_fp = Path(video_fp)

    if not video_fp.exists():
        raise FileNotFoundError(f"Video file not found: {video_fp}")

    # Check for audio stream first
    if not has_audio_stream(video_fp):
        logger.warning(f"No audio stream found in {video_fp}")
        return None

    # Define output file path with .mp3 extension
    audio_fp = video_fp.with_suffix(".mp3")

    try:
        # Convert paths to strings and ensure they're absolute paths
        input_path = str(video_fp.absolute())
        output_path = str(audio_fp.absolute())
        logger.debug(f"Extracting audio from {input_path} to {output_path}")

        # Extract audio using ffmpeg
        stream = (
            ffmpeg.input(input_path)
            .output(filename=output_path, acodec=codec, audio_bitrate=bitrate, vn=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        if stream is None:
            raise RuntimeError("Failed to extract audio")
        if not audio_fp.exists():
            raise RuntimeError("Failed to create output file")

        logger.info(f"Successfully extracted audio to {audio_fp}")
        return audio_fp

    except ffmpeg.Error as exc:
        logger.error("FFmpeg error", exc_info=True)
        raise exc
    except Exception as exc:
        logger.error("Unexpected error", exc_info=True)
        raise exc
