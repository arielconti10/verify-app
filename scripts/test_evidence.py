"""Regression tests for local evidence acceptance, including rejection paths."""

import copy
import importlib.util
import json
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("evidence", Path(__file__).with_name("evidence.py"))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
ORIGIN = "http://127.0.0.1:8123"
METRICS = {
    "width": 1440,
    "height": 900,
    "dpr": 2,
    "scale": 1,
    "origin": ORIGIN,
    "fonts": "loaded",
    "imagesReady": True,
}


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.path = self.folder / "screen.png"
        self.path.write_bytes(b"fixture")
        self.item = {
            "path": "screen.png",
            "kind": "screenshot",
            "before": dict(METRICS),
            "after": dict(METRICS),
            "sha256": e.digest(self.path),
        }
        self.record = {
            "schema": 1,
            "profile": copy.deepcopy(e.PROFILE),
            "session": "evidence-" + "a" * 32,
            "origin": ORIGIN,
            "toolVersion": "agent-browser 0.38.1",
            "launchArgs": ["--force-device-scale-factor=2"],
            "active": None,
            "assets": [self.item],
        }

    def check(self):
        e.save(self.folder, self.record)
        with patch.object(e, "inspect", return_value={"width": 2880, "height": 1800}):
            return e.validate(self.folder)

    def test_valid_record_passes(self):
        self.assertEqual(self.check()["status"], "pass")

    def test_changed_bytes_fail(self):
        self.path.write_bytes(b"replacement")
        with self.assertRaisesRegex(ValueError, "changed evidence"):
            self.check()

    def test_missing_asset_fails(self):
        self.path.unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.check()

    def test_unregistered_media_fails(self):
        (self.folder / "bypass.jpg").write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError, "Unregistered"):
            self.check()

    def test_empty_and_incomplete_runs_fail(self):
        for field, value in [("active", {"kind": "video"}), ("assets", [])]:
            original = self.record[field]
            self.record[field] = value
            with self.assertRaises(ValueError):
                self.check()
            self.record[field] = original

    def test_changed_policy_fails(self):
        self.record["profile"]["fps"] = 30
        with self.assertRaisesRegex(ValueError, "policy"):
            self.check()

    def test_wrong_browser_settings_fail(self):
        for key, value in [
            ("width", 1280),
            ("dpr", 1),
            ("scale", 1.25),
            ("origin", "https://other.example.test"),
            ("fonts", "loading"),
            ("imagesReady", False),
        ]:
            with self.subTest(key=key):
                self.item["after"] = {**METRICS, key: value}
                with self.assertRaises(ValueError):
                    self.check()

    def test_wrong_launch_and_tool_fail(self):
        for key, value in [("launchArgs", []), ("toolVersion", "agent-browser 0.37.0")]:
            original = self.record[key]
            self.record[key] = value
            with self.assertRaises(ValueError):
                self.check()
            self.record[key] = original

    def test_path_escape_and_symlink_fail(self):
        self.item["path"] = "../screen.png"
        with self.assertRaises(ValueError):
            self.check()
        self.item["path"] = "link.png"
        (self.folder / "link.png").symlink_to(self.path)
        with self.assertRaisesRegex(ValueError, "Symbolic"):
            self.check()

    def test_wrong_video_settings_fail(self):
        self.path.rename(self.folder / "take.mp4")
        self.item.update(path="take.mp4", kind="video", recordArgs=["--fps", "30"])
        with self.assertRaisesRegex(ValueError, "recording settings"):
            self.check()

    def test_browser_options_ignore_environment_defaults(self):
        with (
            patch.dict(
                e.os.environ,
                {
                    "AGENT_BROWSER_ARGS": "--force-device-scale-factor=1",
                    "AGENT_BROWSER_CDP": "9222",
                },
            ),
            patch.object(e, "run", return_value='{"success":true,"data":{}}') as call,
        ):
            e.browser(self.record, "snapshot", "-i")
        args = call.call_args.args[0]
        self.assertIn("--force-device-scale-factor=2", args)
        self.assertNotIn("AGENT_BROWSER_CDP", call.call_args.kwargs["env"])
        self.assertIn("--config", args)

    def test_stop_leaves_failed_capture_incomplete(self):
        self.record["active"] = {**self.item, "kind": "video", "path": "take.mp4"}
        e.save(self.folder, self.record)
        with (
            patch.object(e, "browser") as browser,
            patch.object(e, "measure", side_effect=ValueError("Wrong DPR")),
        ):
            with self.assertRaisesRegex(ValueError, "DPR"):
                e.capture(self.folder, "stop", None)
            browser.assert_called_once_with(self.record, "record", "stop")
        self.assertIsNotNone(e.load(self.folder)["active"])

    def test_application_origins(self):
        for url, expected in [
            ("http://localhost:3000/page", "http://localhost:3000"),
            ("https://preview.example.test/path?q=1", "https://preview.example.test"),
            ("http://[::1]:8123/", "http://[::1]:8123"),
            ("https://EXAMPLE.test:443/", "https://example.test"),
        ]:
            self.assertEqual(e.application_origin(url), expected)
        for url in (
            "file:///tmp/page.html",
            "javascript:alert(1)",
            "http:///missing",
            "https://user:secret@example.test",
            "https://example.test:bad",
        ):
            with self.assertRaises(ValueError):
                e.application_origin(url)

    def test_init_uses_supplied_route_without_package_manager(self):
        folder = self.folder / "new"
        with (
            patch.object(e, "run", return_value="agent-browser 0.38.1") as run,
            patch.object(e, "browser") as browser,
            patch.object(e, "measure", return_value=METRICS),
        ):
            result = e.initialize(folder, ORIGIN + "/settings", None)
        self.assertEqual(result["status"], "ready")
        run.assert_called_once_with(["agent-browser", "--version"])
        self.assertEqual(e.load(folder)["origin"], ORIGIN)
        self.assertTrue(
            any(call.args[1:] == ("open", ORIGIN + "/settings") for call in browser.call_args_list)
        )

    def test_capture_lifecycle_registers_only_finished_media(self):
        self.path.unlink()
        self.record["assets"] = []
        e.save(self.folder, self.record)

        def browser(record, *args):
            if args[0] == "screenshot":
                Path(args[-1]).write_bytes(b"screenshot")
            elif "start" in args:
                Path(args[args.index("start") + 1]).write_bytes(b"video")

        with (
            patch.object(e, "browser", side_effect=browser),
            patch.object(e, "measure", return_value=METRICS),
            patch.object(e, "inspect", return_value={"width": 2880, "height": 1800}),
        ):
            self.assertEqual(e.capture(self.folder, "screenshot", "new.png")["status"], "captured")
            self.assertEqual(e.capture(self.folder, "start", "take.mp4")["status"], "recording")
            with self.assertRaises(ValueError):
                e.validate(self.folder)
            with self.assertRaises(ValueError):
                e.capture(self.folder, "close", None)
            e.capture(self.folder, "stop", None)
            self.assertEqual(e.validate(self.folder)["status"], "pass")
            self.assertEqual(len(e.load(self.folder)["assets"]), 2)
            self.assertEqual(e.capture(self.folder, "close", None)["status"], "closed")

    def test_failed_initialization_closes_browser_and_keeps_incomplete_record(self):
        folder = self.folder / "failed-init"
        with (
            patch.object(e, "run", return_value="agent-browser 0.38.1"),
            patch.object(e, "browser") as browser,
            patch.object(e, "measure", side_effect=ValueError("Wrong DPR")),
        ):
            with self.assertRaisesRegex(ValueError, "DPR"):
                e.initialize(folder, ORIGIN, self.folder / "auth.json")
        self.assertEqual(browser.call_args.args[1:], ("close",))
        self.assertEqual(browser.call_args_list[0].args[1:3], ("state", "load"))
        self.assertEqual(e.load(folder)["active"]["kind"], "initializing")

    def test_measure_rejects_unready_images(self):
        with patch.object(e, "browser", return_value={"result": METRICS}):
            self.assertEqual(e.measure(self.record), METRICS)
        with patch.object(e, "browser", return_value={"result": {**METRICS, "imagesReady": False}}):
            with self.assertRaisesRegex(ValueError, "images"):
                e.measure(self.record)

    def test_cli_reports_acceptance_and_failure_as_json(self):
        e.save(self.folder, self.record)
        for corrupt, code in [(False, 0), (True, 1)]:
            if corrupt:
                self.path.unlink()
            output = io.StringIO()
            with (
                patch.object(sys, "argv", ["evidence.py", "check", str(self.folder)]),
                patch.object(e, "inspect", return_value={"width": 2880, "height": 1800}),
                patch("sys.stdout", output),
            ):
                self.assertEqual(e.main(), code)
            self.assertEqual(json.loads(output.getvalue())["status"], "fail" if corrupt else "pass")

    def test_cli_rejects_setting_override(self):
        result = subprocess.run(
            [
                "python3",
                str(Path(e.__file__)),
                "start",
                str(self.folder),
                "take.mp4",
                "--fps",
                "30",
            ],
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_cli_refuses_concurrent_access(self):
        with (self.folder / ".capture.lock").open("a") as lock:
            e.fcntl.flock(lock, e.fcntl.LOCK_EX | e.fcntl.LOCK_NB)
            result = subprocess.run(
                ["python3", str(Path(e.__file__)), "check", str(self.folder)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("unavailable", json.loads(result.stdout)["error"].lower())

    def test_cli_empty_directory_exits_nonzero(self):
        result = subprocess.run(
            ["python3", str(Path(e.__file__)), "check", str(self.folder)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires FFmpeg")
class MediaTests(unittest.TestCase):
    def test_real_media_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)

            def make(name, size, fps=60):
                args = [
                    "ffmpeg",
                    "-nostdin",
                    "-v",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    f"color=black:s={size}:r={fps}",
                ]
                if name.endswith("png"):
                    args += ["-frames:v", "1"]
                else:
                    args += [
                        "-t",
                        "0.1",
                        "-c:v",
                        "libx264",
                        "-preset",
                        "ultrafast",
                        "-pix_fmt",
                        "yuv420p",
                    ]
                e.run([*args, str(folder / name)])
                return folder / name

            e.inspect(make("valid.png", "2880x1800"), "screenshot")
            e.inspect(make("valid.mp4", "2880x1800"), "video")
            with self.assertRaisesRegex(ValueError, "dimensions"):
                e.inspect(make("small.png", "1440x900"), "screenshot")
            with self.assertRaisesRegex(ValueError, "60 fps"):
                e.inspect(make("slow.mp4", "2880x1800", 30), "video")
            broken = folder / "broken.png"
            broken.write_bytes(b"\x89PNG\r\n\x1a\n")
            with self.assertRaises(ValueError):
                e.inspect(broken, "screenshot")


if __name__ == "__main__":
    unittest.main()
