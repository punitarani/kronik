import unittest

from kronik import PROJECT_ROOT
from kronik.utils.av import extract_audio


class TestExtractAudio(unittest.TestCase):
    def setUp(self):
        # Set up test video file path
        self.test_video_fp = PROJECT_ROOT.joinpath("tests", "data", "atoms-for-peace.mp4")
        self.test_audio_fp = self.test_video_fp.with_suffix(".mp3")

    def test_extract_audio_success(self):
        if not self.test_video_fp.exists():
            self.skipTest(f"Test video file not found: {self.test_video_fp}")

        audio_fp = extract_audio(self.test_video_fp)
        self.assertTrue(audio_fp.exists(), "Audio file was not created")
        self.assertGreater(audio_fp.stat().st_size, 0, "Audio file is empty")

    def tearDown(self):
        # Clean up generated audio file
        if self.test_audio_fp.exists():
            self.test_audio_fp.unlink()
