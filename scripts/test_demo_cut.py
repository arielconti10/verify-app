"""Tests for the cutting logic in `demo_cut.py`.

Only the decision of which pieces to keep is tested here — that is the part that can fail
silently. The ffmpeg render is validated separately against a synthetic video with known
durations (see references/natural-recording.md).

Run:
    python3 -m unittest discover -s scripts -p 'test_demo_cut*.py'
"""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("demo_cut", Path(__file__).with_name("demo_cut.py"))
demo_cut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo_cut)

SCRIPT = Path(__file__).with_name("demo_cut.py")


def kept(segments):
    return round(sum(end - start for start, end in segments), 3)


class BuildSegmentsTest(unittest.TestCase):
    """
    Contiguous segments are merged on purpose: cutting at a point where nothing was removed
    only adds an extra cut. That is why `(0,3) + (3,3.6)` becomes `(0,3.6)`.
    """

    def test_no_freeze_keeps_the_whole_video(self):
        self.assertEqual(demo_cut.build_segments(10.0, [], keep=0.6), [(0.0, 10.0)])

    def test_middle_freeze_is_shortened_to_keep(self):
        # 4s freeze (3 to 7) with keep 0.6: keeps 0 to 3.6 and jumps straight to 7.
        segments = demo_cut.build_segments(10.0, [(3.0, 7.0)], keep=0.6)
        self.assertEqual(segments, [(0.0, 3.6), (7.0, 10.0)])
        self.assertEqual(kept(segments), 6.6)

    def test_freeze_at_the_start_keeps_its_beginning(self):
        segments = demo_cut.build_segments(10.0, [(0.0, 5.0)], keep=0.6)
        self.assertEqual(segments, [(0.0, 0.6), (5.0, 10.0)])

    def test_freeze_at_the_end_keeps_its_beginning(self):
        # The final hold on the result is a freeze: keep the start of it.
        segments = demo_cut.build_segments(10.0, [(8.0, 10.0)], keep=0.6)
        self.assertEqual(segments, [(0.0, 8.6)])

    def test_freeze_shorter_than_keep_removes_nothing(self):
        segments = demo_cut.build_segments(10.0, [(4.0, 4.4)], keep=0.6)
        self.assertEqual(segments, [(0.0, 10.0)])

    def test_adjacent_freezes_produce_one_keep_each(self):
        segments = demo_cut.build_segments(10.0, [(3.0, 5.0), (5.0, 7.0)], keep=0.6)
        self.assertEqual(segments, [(0.0, 3.6), (5.0, 5.6), (7.0, 10.0)])

    def test_segment_below_the_minimum_is_dropped(self):
        # Only 0.1s left after the freeze, below MIN_SEGMENT.
        segments = demo_cut.build_segments(10.0, [(9.9, 10.0)], keep=0.6)
        self.assertEqual(segments, [(0.0, 9.9)])

    def test_freeze_longer_than_the_video_does_not_overflow(self):
        segments = demo_cut.build_segments(10.0, [(2.0, 99.0)], keep=0.6)
        self.assertEqual(segments, [(0.0, 2.6)])

    def test_segments_never_pass_the_end_of_the_video(self):
        segments = demo_cut.build_segments(10.0, [(5.0, 12.0)], keep=5.0)
        self.assertTrue(segments)
        for _, end in segments:
            self.assertLessEqual(end, 10.0)

    def test_long_video_with_many_pauses_shrinks_a_lot(self):
        # Reproduces the measured case: a 43s recording with 7 thinking pauses.
        freezes = [(0.0, 5.3), (5.4, 20.1), (20.3, 22.7), (22.7, 25.7), (26.0, 30.8), (30.8, 37.2), (37.3, 43.4)]
        segments = demo_cut.build_segments(43.4, freezes, keep=0.6)
        self.assertLess(kept(segments), 6.0)
        self.assertGreater(kept(segments), 2.0)


class CliTest(unittest.TestCase):
    """
    These tests exercise the CLI path, which starts by requiring ffmpeg/ffprobe. Without them the
    script fails before reaching the rule under test, so the tests are skipped — the CI runner that
    only runs type checks does not have ffmpeg installed.
    """

    @unittest.skipUnless(
        shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires ffmpeg and ffprobe on PATH"
    )
    def test_refuses_to_write_inside_a_capture_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = Path(folder) / "capture"
            capture.mkdir()
            (capture / "capture.json").write_text("{}")
            video = capture / "interaction.mp4"
            video.write_bytes(b"does not matter")

            result = subprocess.run([sys.executable, str(SCRIPT), str(video)], capture_output=True, text=True)

            self.assertEqual(result.returncode, 1)
            self.assertIn("managed capture directory", result.stderr)

    @unittest.skipUnless(
        shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires ffmpeg and ffprobe on PATH"
    )
    def test_accepts_output_outside_the_capture_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = Path(folder) / "capture"
            capture.mkdir()
            (capture / "capture.json").write_text("{}")
            video = capture / "interaction.mp4"
            video.write_bytes(b"does not matter")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(video), "-o", str(Path(folder) / "demo.mp4"), "--dry-run"],
                capture_output=True,
                text=True,
            )

            # Gets past the directory check and fails later, because it is not a valid video.
            self.assertNotIn("managed capture directory", result.stderr)


if __name__ == "__main__":
    unittest.main()
