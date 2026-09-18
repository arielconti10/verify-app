#!/usr/bin/env python3
"""Fixed desktop capture and independent local validation. No package patches."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid
from urllib.parse import urlsplit

PROFILE = {"name": "desktop-v1", "width": 1440, "height": 900, "dpr": 2,
           "scale": 1, "pixels": [2880, 1800], "fps": 60}
MEDIA = {".png", ".mp4", ".jpg", ".jpeg", ".webm", ".gif", ".mov", ".avif", ".webp"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(args, env=None, timeout=60):
    result = subprocess.run(args, capture_output=True, text=True, env=env, timeout=timeout)
    require(result.returncode == 0, f"{args[0]} failed: {result.stderr[-1500:] or result.stdout[-1500:]}")
    return result.stdout.strip()


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save(folder, record):
    temporary = folder / "capture.json.tmp"
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(folder / "capture.json")


def load(folder):
    record = json.loads((folder / "capture.json").read_text())
    require(isinstance(record, dict), "Capture record must be an object")
    require("active" in record and isinstance(record.get("assets"), list), "Incomplete capture record")
    require(record.get("schema") == 1 and record.get("profile") == PROFILE, "Unknown or changed capture policy")
    require(re.fullmatch(r"evidence-[a-f0-9]{32}", record.get("session", "")), "Invalid capture session")
    return record


def browser(record, *args):
    # Isolate launch configuration from user defaults and other agents' sessions.
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENT_BROWSER_")}
    with tempfile.TemporaryDirectory(prefix="evidence-config-") as directory:
        config = Path(directory) / "config.json"
        config.write_text("{}")
        value = json.loads(run(["agent-browser", "--config", str(config), "--session", record["session"],
                               "--args", "--force-device-scale-factor=2", "--json", *args], env=env))
    require(value.get("success") is True, "Browser command failed")
    return value.get("data")


def check_metrics(metrics, origin):
    require(isinstance(metrics, dict), "Missing browser measurements")
    for key in ("width", "height", "dpr", "scale"):
        require(metrics.get(key) == PROFILE[key], f"Browser {key} must be {PROFILE[key]}")
    require(metrics.get("origin") == origin, "Browser left the selected application origin")
    require(metrics.get("fonts") == "loaded", "Fonts are not loaded")
    require(metrics.get("imagesReady") is True, "Visible images are not loaded")


def measure(record):
    data = browser(record, "eval", """document.fonts.ready.then(() => ({
      width:innerWidth,height:innerHeight,dpr:devicePixelRatio,scale:visualViewport.scale,
      origin:location.origin,fonts:document.fonts.status,
      imagesReady:[...document.images].filter(i=>{const r=i.getBoundingClientRect();
        return r.width>0&&r.height>0&&r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth})
        .every(i=>i.complete&&i.naturalWidth>0)
    }))""")
    metrics = data["result"]
    check_metrics(metrics, record["origin"])
    return metrics


def asset_path(folder, name):
    require(isinstance(name, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*\.(png|mp4)", name),
            "Use a plain PNG or MP4 filename with letters, numbers, hyphens, or underscores")
    path = folder / name
    require(not path.is_symlink(), "Symbolic links are not evidence files")
    return path


def inspect(path, kind):
    info = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
    streams = info.get("streams", [])
    require(len(streams) == 1 and streams[0].get("codec_type") == "video", "Require one video/image stream without audio")
    stream = streams[0]
    require([stream.get("width"), stream.get("height")] == PROFILE["pixels"], "Wrong image dimensions: require 2880 x 1800")
    require(stream.get("codec_name") == ("png" if kind == "screenshot" else "h264"), "Wrong evidence codec")
    if kind == "screenshot":
        with path.open("rb") as source:
            require(source.read(8) == b"\x89PNG\r\n\x1a\n", "Screenshot is not a PNG")
    else:
        require("mp4" in info.get("format", {}).get("format_name", "").split(","), "Video is not MP4")
        require(stream.get("pix_fmt") == "yuv420p", "Video must use yuv420p")
        require(stream.get("r_frame_rate") == "60/1" and stream.get("avg_frame_rate") == "60/1", "Video must be 60 fps")
        duration = float(info["format"]["duration"])
        require(0 < duration <= 301, "Video duration must be greater than zero and at most five minutes")
        frames = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
                                "-show_entries", "frame=width,height", "-of", "json", str(path)], timeout=180))["frames"]
        require(bool(frames), "Video contains no decoded frames")
        require(all([f.get("width"), f.get("height")] == PROFILE["pixels"] for f in frames), "Video frame dimensions changed")
    run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"], timeout=180)
    return {"codec": stream["codec_name"], "width": stream["width"], "height": stream["height"],
            "fps": stream.get("avg_frame_rate"), "duration": info.get("format", {}).get("duration")}


def validate(folder):
    record = load(folder)
    require(record.get("active") is None, "Recording or capture remains incomplete")
    require(record.get("assets"), "No evidence files were captured")
    require(application_origin(record.get("origin", "")) == record["origin"], "Invalid application origin")
    require(record.get("launchArgs") == ["--force-device-scale-factor=2"], "Wrong browser launch settings")
    require(re.fullmatch(r"agent-browser \d+\.\d+\.\d+", record.get("toolVersion", "")), "Missing tool version")
    require(tuple(map(int, record["toolVersion"].split()[1].split("."))) >= (0, 38, 1), "Require agent-browser 0.38.1 or later")
    names = []
    results = []
    for item in record["assets"]:
        path = asset_path(folder, item["path"])
        require(item.get("kind") in ("screenshot", "video"), "Unknown evidence kind")
        require(path.suffix == (".png" if item["kind"] == "screenshot" else ".mp4"), "Wrong evidence extension")
        require(path.name not in names, "Duplicate evidence entry")
        names.append(path.name)
        for field in ("before", "after"):
            check_metrics(item.get(field), record["origin"])
        require(path.is_file() and digest(path) == item.get("sha256"), f"Missing or changed evidence: {path.name}")
        if item["kind"] == "video":
            require(item.get("recordArgs") == ["--fps", "60", "--cursor"], "Wrong recording settings")
        results.append({"path": path.name, **inspect(path, item["kind"])})
    actual = {str(p.relative_to(folder)) for p in folder.rglob("*") if p.suffix.lower() in MEDIA}
    require(actual == set(names), "Unregistered evidence files exist in the proof directory")
    return {"status": "pass", "scope": "capture-settings-and-file-integrity", "assets": results,
            "limits": ["Local records are not signed attestations.", "Sharpness, pointer visibility, natural input, and feature correctness require review.",
                       "Nominal fps does not prove distinct source frames or smooth playback."]}


def application_origin(url):
    parsed = urlsplit(url)
    require(parsed.scheme in ("http", "https") and bool(parsed.hostname), "Require an HTTP or HTTPS application URL")
    require(parsed.username is None and parsed.password is None, "Do not include credentials in the application URL")
    port = parsed.port
    host = parsed.hostname.lower()
    if ":" in host:
        host = "[" + host + "]"
    suffix = "" if port is None or (parsed.scheme, port) in (("http", 80), ("https", 443)) else f":{port}"
    return f"{parsed.scheme}://{host}{suffix}"


def initialize(folder, url, state):
    require(not folder.exists(), "Use a new proof directory")
    origin = application_origin(url)
    version = run(["agent-browser", "--version"])
    require(re.fullmatch(r"agent-browser \d+\.\d+\.\d+", version), "Cannot identify agent-browser version")
    require(tuple(map(int, version.split()[1].split("."))) >= (0, 38, 1), "Require agent-browser 0.38.1 or later")
    record = {"schema": 1, "profile": PROFILE, "session": "evidence-" + uuid.uuid4().hex,
              "origin": origin, "toolVersion": version, "launchArgs": ["--force-device-scale-factor=2"],
              "assets": [], "active": {"kind": "initializing"}}
    folder.mkdir(parents=True)
    save(folder, record)
    try:
        if state:
            browser(record, "state", "load", str(Path(state).expanduser().resolve()))
        browser(record, "open", url)
        browser(record, "set", "viewport", "1440", "900", "2")
        measure(record)
        record["active"] = None
        save(folder, record)
    except Exception:
        browser(record, "close")
        raise
    return {"status": "ready", "session": record["session"], "directory": str(folder)}


def capture(folder, command, name):
    record = load(folder)
    if command == "close":
        require(record.get("active") is None, "Stop the recording before closing")
        browser(record, "close")
        return {"status": "closed"}
    if command == "stop":
        item = record.get("active")
        require(item and item.get("kind") == "video", "No managed recording is active")
        # Stop even if the end-state measurements later fail.
        browser(record, "record", "stop")
        path = asset_path(folder, item["path"])
    else:
        require(record.get("active") is None, "A capture is already active")
        kind = "video" if command == "start" else "screenshot"
        path = asset_path(folder, name)
        require(path.suffix == (".mp4" if kind == "video" else ".png"), "Wrong capture extension")
        require(not path.exists(), "Do not overwrite evidence")
        item = {"path": name, "kind": kind, "before": measure(record)}
        if kind == "video":
            item["recordArgs"] = ["--fps", "60", "--cursor"]
        record["active"] = item
        save(folder, record)
        if kind == "video":
            browser(record, "--input-mode", "human", "record", "start", str(path), *item["recordArgs"])
            return {"status": "recording", "session": record["session"]}
        browser(record, "screenshot", "--screenshot-format", "png", str(path))
    item["after"] = measure(record)
    item["measured"] = inspect(path, item["kind"])
    item["sha256"] = digest(path)
    record["assets"].append(item)
    record["active"] = None
    save(folder, record)
    return {"status": "captured", "path": str(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "screenshot", "start", "stop", "check", "close"):
        sub = commands.add_parser(command)
        sub.add_argument("directory", type=Path)
        if command == "init":
            sub.add_argument("url")
            sub.add_argument("--state")
        if command in ("screenshot", "start"):
            sub.add_argument("filename")
    args = parser.parse_args()
    folder = args.directory.resolve()
    lock = None
    try:
        if args.command != "init":
            lock = (folder / ".capture.lock").open("a")
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.command == "init":
            result = initialize(folder, args.url, args.state)
        elif args.command == "check":
            result = validate(folder)
        else:
            result = capture(folder, args.command, getattr(args, "filename", None))
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "fail", "error": str(error)}, indent=2))
        return 1
    finally:
        if lock is not None:
            lock.close()


if __name__ == "__main__":
    sys.exit(main())
