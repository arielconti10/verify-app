"""Checks for body preservation, validated inputs, and attachment markup."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
import format_evidence as f


class FormatterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.pair = {
            "kind": "action",
            "label": "Select model",
            "before": "before.png",
            "after": "after.png",
            "before_label": "Default",
            "after_label": "Selected",
        }

    def render(self, pairs=None, body=""):
        with patch.object(
            f.evidence,
            "validate",
            return_value={
                "assets": [
                    {"path": p} for p in ("before.png", "after.png", "before.mp4", "after.mp4")
                ]
            },
        ) as validate:
            result = f.prepare({"comparisons": pairs or [self.pair]}, self.root, body)
            validate.assert_called_once_with(self.root)
            return result

    def test_preserves_outside_bytes_and_repeated_render(self):
        prefix, suffix = "Title  \r\n\r\n", "\r\n  Footer\t"
        body = prefix + f.START + "old" + f.END + suffix
        result = self.render(body=body)
        self.assertTrue(result["body"].startswith(prefix))
        self.assertTrue(result["body"].endswith(suffix))
        self.assertEqual(self.render(body=result["body"]), result)

    def test_append_preserves_original_text(self):
        body = "Existing paragraph.  \r\n"
        self.assertTrue(self.render(body=body)["body"].startswith(body))

    def test_bad_markers_rejected(self):
        for body in [f.START, f.END, f.END + f.START, f.START * 2 + f.END]:
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.render(body=body)

    def test_preview_and_video_standalone_markup(self):
        self.pair.update(kind="preview", after="after.mp4")
        del self.pair["before"]
        result = self.render()
        self.assertIn("### Preview:", result["body"])
        self.assertIn(f"\n\n![Selected]({self.root}/after.mp4)\n", result["body"])
        self.assertEqual(result["attachments"], [str(self.root / "after.mp4")])

    def test_image_table_and_attachment_deduplication(self):
        result = self.render([self.pair, self.pair])
        self.assertIn("| Before: Default | After: Selected |", result["body"])
        self.assertEqual(len(result["attachments"]), 2)

    def test_label_markup_is_escaped(self):
        self.pair["label"] = "<script>[a]|*b*"
        result = self.render()["body"]
        self.assertNotIn("<script>", result)
        self.assertIn("&#124;", result)

    def test_invalid_pair_and_paths_rejected(self):
        for changes in [
            {"kind": "preview"},
            {"kind": "unknown"},
            {"before": None},
            {"after": "after.mp4"},
            {"after": "name with spaces.png"},
            {"after": "image.svg"},
            {"label": "two\nlines"},
        ]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.render([{**self.pair, **changes}])

    def test_changed_media_rejected(self):
        with patch.object(f.evidence, "validate", side_effect=ValueError("changed evidence")):
            with self.assertRaisesRegex(ValueError, "changed evidence"):
                f.prepare({"comparisons": [self.pair]}, self.root, "")

    def test_unregistered_file_rejected(self):
        with patch.object(f.evidence, "validate", return_value={"assets": []}):
            with self.assertRaisesRegex(ValueError, "Unaccepted"):
                f.prepare({"comparisons": [self.pair]}, self.root, "")

    def test_busy_capture_rejected(self):
        with (self.root / ".capture.lock").open("a") as lock:
            f.evidence.fcntl.flock(lock, f.evidence.fcntl.LOCK_EX | f.evidence.fcntl.LOCK_NB)
            with self.assertRaises(OSError):
                self.render()

    def test_attachment_limit_rejected_before_validation(self):
        pairs = [
            {**self.pair, "before": None, "kind": "preview", "after": f"image-{i}.png"}
            for i in range(51)
        ]
        with patch.object(f.evidence, "validate") as validate:
            with self.assertRaisesRegex(ValueError, "50 attachments"):
                f.prepare({"comparisons": pairs}, self.root, "")
            validate.assert_not_called()

    def test_cli_failure_writes_no_publish_plan(self):
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({"comparisons": [self.pair]}))
        result = subprocess.run([sys.executable, f.__file__, str(manifest)], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")


if __name__ == "__main__":
    unittest.main()
