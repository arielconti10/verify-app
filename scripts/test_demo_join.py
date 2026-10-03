"""Tests for joining demo takes without trimming them."""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("demo_join", Path(__file__).with_name("demo_join.py"))
demo_join = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo_join)

SCRIPT = Path(__file__).with_name("demo_join.py")


class ConcatListTest(unittest.TestCase):
    def test_lists_takes_in_order(self):
        text = demo_join.concat_list([Path("/tmp/01.mp4"), Path("/tmp/02.mp4")])
        self.assertEqual(text, "file '/tmp/01.mp4'\nfile '/tmp/02.mp4'\n")

    def test_escapes_quotes_in_paths(self):
        text = demo_join.concat_list([Path("/tmp/it's.mp4")])
        self.assertIn("file '/tmp/it'\\''s.mp4'", text)


class CliTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ffmpeg"), "requires ffmpeg on PATH")
    def test_refuses_to_write_inside_a_capture_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = Path(folder) / "capture"
            capture.mkdir()
            (capture / "capture.json").write_text("{}")
            first = Path(folder) / "01.mp4"
            second = Path(folder) / "02.mp4"
            first.write_bytes(b"a")
            second.write_bytes(b"b")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(first), str(second), "-o", str(capture / "demo.mp4")],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("managed capture directory", result.stderr)


if __name__ == "__main__":
    unittest.main()
