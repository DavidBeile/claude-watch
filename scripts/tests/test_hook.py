"""Tests for the hook microscope, in particular short-video handling."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

import hook  # noqa: E402
from hook import _frames_in_window, analyse_hook  # noqa: E402

MAIN_PASS_FRAMES = [
    {"index": 0, "timestamp_seconds": 0.0, "path": "/tmp/f0.jpg"},
    {"index": 1, "timestamp_seconds": 3.0, "path": "/tmp/f1.jpg"},
    {"index": 2, "timestamp_seconds": 9.5, "path": "/tmp/f2.jpg"},
    {"index": 3, "timestamp_seconds": 14.0, "path": "/tmp/f3.jpg"},
    {"index": 4, "timestamp_seconds": 22.0, "path": "/tmp/f4.jpg"},
]

FAKE_WORDS = [{"word": "Everybody", "start": 0.2},
              {"word": "missed", "start": 0.7}]


class TestFramesInWindow(unittest.TestCase):

    def test_keeps_only_frames_inside_window(self):
        got = _frames_in_window(MAIN_PASS_FRAMES, 10.0)
        self.assertEqual([f["index"] for f in got], [0, 1, 2])

    def test_empty_and_none_are_safe(self):
        self.assertEqual(_frames_in_window(None, 10.0), [])
        self.assertEqual(_frames_in_window([], 10.0), [])

    def test_tolerates_frames_without_timestamp(self):
        got = _frames_in_window([{"index": 0}, {"timestamp_seconds": 1.0}], 10.0)
        self.assertEqual(len(got), 1)


class TestAnalyseHook(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="watch-hook-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, duration, *, has_key=True, frames=None):
        """Call analyse_hook with ffmpeg/Whisper/extract stubbed out."""
        creds = ("groq", "key-123") if has_key else (None, None)
        with mock.patch.object(hook, "load_api_key", return_value=creds), \
             mock.patch.object(hook, "extract",
                               return_value=[{"index": 0,
                                              "timestamp_seconds": 0.0,
                                              "path": "/tmp/hook0.jpg"}]) as ex, \
             mock.patch.object(hook.shutil, "which", return_value="/usr/bin/ffmpeg"), \
             mock.patch.object(hook.subprocess, "run") as run, \
             mock.patch.object(hook, "transcribe_audio",
                               return_value=([], None, FAKE_WORDS)) as tr:
            result = analyse_hook(
                "/tmp/video.mp4", self.tmp,
                full_video_duration=duration,
                main_pass_frames=(MAIN_PASS_FRAMES if frames is None else frames),
            )
        return result, ex, run, tr

    # --- the regression this change is about ---------------------------------

    def test_short_video_still_gets_word_timestamps(self):
        result, extract_mock, _, transcribe_mock = self._run(25.0)
        self.assertTrue(result["ran"])
        self.assertEqual(result["words"], FAKE_WORDS)
        transcribe_mock.assert_called_once()
        # The whole point: no near-duplicate frame re-extract.
        extract_mock.assert_not_called()
        self.assertEqual(result["frames_source"], "main-pass")

    def test_short_video_reuses_main_pass_frames_in_window(self):
        result, _, _, _ = self._run(25.0)
        self.assertEqual([f["index"] for f in result["frames"]], [0, 1, 2])

    def test_typical_short_duration_is_not_skipped(self):
        for duration in (15.0, 22.0, 28.0, 29.9):
            with self.subTest(duration=duration):
                result, _, _, _ = self._run(duration)
                self.assertTrue(result["ran"], f"{duration}s was skipped")

    # --- long videos keep the dense re-pass -----------------------------------

    def test_long_video_runs_dense_repass(self):
        result, extract_mock, _, _ = self._run(180.0)
        extract_mock.assert_called_once()
        self.assertEqual(result["frames_source"], "dense-repass")
        self.assertTrue(result["ran"])

    def test_unknown_duration_treated_as_long(self):
        result, extract_mock, _, _ = self._run(0.0)
        extract_mock.assert_called_once()
        self.assertEqual(result["frames_source"], "dense-repass")

    # --- window clamping ------------------------------------------------------

    def test_audio_slice_clamped_to_video_end(self):
        _, _, run_mock, _ = self._run(6.0)
        argv = run_mock.call_args[0][0]
        self.assertEqual(argv[argv.index("-t") + 1], "6.0")

    def test_long_video_slices_full_ten_seconds(self):
        _, _, run_mock, _ = self._run(180.0)
        argv = run_mock.call_args[0][0]
        self.assertEqual(argv[argv.index("-t") + 1], "10.0")

    # --- nothing to gain ------------------------------------------------------

    def test_short_video_without_whisper_key_is_skipped_with_reason(self):
        result, extract_mock, _, _ = self._run(25.0, has_key=False)
        self.assertFalse(result["ran"])
        self.assertIn("no Whisper key", result["skipped_reason"])
        extract_mock.assert_not_called()

    def test_short_video_without_main_pass_frames_still_transcribes(self):
        result, _, _, transcribe_mock = self._run(25.0, frames=[])
        self.assertTrue(result["ran"])
        self.assertEqual(result["frames"], [])
        self.assertEqual(result["words"], FAKE_WORDS)
        transcribe_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
