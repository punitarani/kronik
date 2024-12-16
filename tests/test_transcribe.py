import unittest

from kronik import PROJECT_ROOT
from kronik.utils import transcribe


class TestTranscribe(unittest.TestCase):
    def setUp(self):
        # Set up test audio file path
        self.test_audio_fp = PROJECT_ROOT.joinpath("tests", "data", "atoms-for-peace.test.mp3")

    def test_transcribe_success(self):
        if not self.test_audio_fp.exists():
            self.skipTest(f"Test audio file not found: {self.test_audio_fp}")

        transcription = transcribe(self.test_audio_fp)
        self.assertIsInstance(transcription, str, "Transcription should be a string")
        self.assertAlmostEqual(
            len(transcription),
            2305,
            delta=100,
            msg="Transcription length should be roughly 2305 (±100) characters",
        )
