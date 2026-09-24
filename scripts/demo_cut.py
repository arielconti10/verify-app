#!/usr/bin/env python3
"""Derive a fluid demo video from a verify-app capture.

The video recorded by verify-app is EVIDENCE: continuous, uncut, validated by
`evidence.py check`. While the agent thinks between one action and the next, the screen does not
change, and that shows up as dead time.

This script never touches the evidence. It reads the recording and writes a derivative with the
idle stretches removed, for use as a demo (PR, presentation, human review).

Skill rule this respects: "Keep original media unchanged. Store diagnostic derivatives outside
the managed capture directory."

Usage:
    python3 scripts/demo_cut.py recording.mp4
    python3 scripts/demo_cut.py recording.mp4 -o demo.mp4 --min-freeze 1.0 --keep 0.6
    python3 scripts/demo_cut.py recording.mp4 --dry-run --report

How it works:
    1. ffmpeg's `freezedetect` marks the intervals where the picture does not change.
    2. Each idle interval is shortened to at most `--keep` seconds (its start is preserved,
       because that is where the previous action's result is, which needs to be read).
    3. The remaining pieces are concatenated in a single ffmpeg pass.

Only idle stretches longer than `--min-freeze` are cut, so short natural pauses (reading the
screen, interface response time) stay in.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Difference below which two frames count as identical. -60dB is strict (almost no compression noise).
DEFAULT_THRESHOLD = "-60dB"
# Idle stretches shorter than this are natural pauses and stay.
DEFAULT_MIN_FREEZE = 1.0
# How much of the start of each idle stretch is preserved.
DEFAULT_KEEP = 0.6
# Shortest segment worth keeping in the result.
MIN_SEGMENT = 0.2

FREEZE_LINE = re.compile(
    r"freeze_start=(?P<start>[\d.]+)|freeze_end=(?P<end>[\d.]+)|freeze_duration=(?P<duration>[\d.]+)"
)


class DemoCutError(Exception):
    pass


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise DemoCutError(f"{name} not found on PATH. Install ffmpeg.")


def probe_duration(video: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError as error:
        raise DemoCutError(f"Could not read the duration of {video}") from error


def find_freezes(video: Path, threshold: str, min_freeze: float) -> list[tuple[float, float]]:
    """Run freezedetect and return the idle intervals, already filtered by duration."""
    command = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i",
        str(video),
        "-vf",
        f"freezedetect=n={threshold}:d={min_freeze},metadata=mode=print:file=-",
        "-map",
        "0:v",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise DemoCutError(f"freezedetect failed:\n{result.stderr[-800:]}")

    freezes: list[tuple[float, float]] = []
    pending_start: float | None = None
    for line in result.stdout.splitlines():
        match = FREEZE_LINE.search(line)
        if not match:
            continue
        if match.group("start") is not None:
            pending_start = float(match.group("start"))
        elif match.group("end") is not None and pending_start is not None:
            freezes.append((pending_start, float(match.group("end"))))
            pending_start = None
    # A freeze that reaches the end of the video without a `freeze_end` still counts.
    if pending_start is not None:
        freezes.append((pending_start, probe_duration(video)))
    return freezes


def build_segments(duration: float, freezes: list[tuple[float, float]], keep: float) -> list[tuple[float, float]]:
    """Turn the freezes into the pieces to keep: each freeze is shortened to `keep` seconds."""
    segments: list[tuple[float, float]] = []
    cursor = 0.0
    for start, end in freezes:
        if start > cursor:
            segments.append((cursor, min(start, duration)))
        # Keep the start of the freeze (where the previous action's result is) and drop the rest.
        trimmed_end = min(start + keep, end)
        if trimmed_end > start:
            segments.append((start, trimmed_end))
        cursor = max(cursor, end)
    if cursor < duration:
        segments.append((cursor, duration))

    merged: list[tuple[float, float]] = []
    for start, end in segments:
        start = max(0.0, start)
        end = min(duration, end)
        if end - start < MIN_SEGMENT:
            continue
        if merged and start - merged[-1][1] < 0.01:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged


def render(video: Path, output: Path, segments: list[tuple[float, float]]) -> None:
    if len(segments) == 1 and segments[0][0] == 0:
        raise DemoCutError("Nothing to cut: no idle stretch above the limit.")
    parts = []
    labels = []
    for index, (start, end) in enumerate(segments):
        parts.append(f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{index}]")
        labels.append(f"[v{index}]")
    filter_complex = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(segments)}:v=1:a=0[out]"

    command = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-loglevel",
        "error",
        "-i",
        str(video),
        "-filter_complex",
        filter_complex,
        "-map",
        "[out]",
        "-an",
        # Same parameters as the original capture, so the demo matches its quality.
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-y",
        str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise DemoCutError(f"ffmpeg failed to render:\n{result.stderr[-800:]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path, help="source recording (the evidence, which is never modified)")
    parser.add_argument("-o", "--output", type=Path, help="output file (default: <name>-demo.mp4)")
    parser.add_argument(
        "--min-freeze",
        type=float,
        default=DEFAULT_MIN_FREEZE,
        help=f"shortest idle stretch to cut (default: {DEFAULT_MIN_FREEZE}s)",
    )
    parser.add_argument(
        "--keep",
        type=float,
        default=DEFAULT_KEEP,
        help=f"how much of the start of each idle stretch to preserve (default: {DEFAULT_KEEP}s)",
    )
    parser.add_argument(
        "--threshold", default=DEFAULT_THRESHOLD, help=f"freezedetect threshold (default: {DEFAULT_THRESHOLD})"
    )
    parser.add_argument("--dry-run", action="store_true", help="report what would be cut, write nothing")
    parser.add_argument("--report", action="store_true", help="print the report as JSON")
    parser.add_argument("--force", action="store_true", help="allow writing inside a capture directory")
    args = parser.parse_args()

    try:
        require_tool("ffmpeg")
        require_tool("ffprobe")
        video = args.video.resolve()
        if not video.is_file():
            raise DemoCutError(f"File not found: {video}")

        output = args.output.resolve() if args.output else video.with_name(f"{video.stem}-demo.mp4")
        if output == video:
            raise DemoCutError("The output cannot be the source file itself")

        # Evidence lives in a directory with capture.json. The derivative must not land there.
        if (output.parent / "capture.json").exists() and not args.force:
            raise DemoCutError(
                f"{output.parent} is a managed capture directory.\n"
                "Write the derivative outside it (e.g. -o /tmp/demo.mp4) so demo and evidence stay apart."
            )

        duration = probe_duration(video)
        freezes = find_freezes(video, args.threshold, args.min_freeze)
        segments = build_segments(duration, freezes, args.keep)
        removed = duration - sum(end - start for start, end in segments)
        output_duration = duration - removed

        report = {
            "source": str(video),
            "sourceSeconds": round(duration, 2),
            "freezesDetected": len(freezes),
            "segments": len(segments),
            "removedSeconds": round(removed, 2),
            "outputSeconds": round(output_duration, 2),
            "compression": f"{removed / duration:.0%}" if duration else "0%",
            "output": str(output),
            "dryRun": args.dry_run,
        }

        if not args.dry_run:
            render(video, output, segments)

        if args.report:
            print(json.dumps(report, indent=2))
        else:
            print(
                f"{report['sourceSeconds']}s -> {report['outputSeconds']}s "
                f"(removed {report['removedSeconds']}s / {report['compression']} across "
                f"{report['freezesDetected']} pauses)"
            )
            if not args.dry_run:
                print(f"demo: {report['output']}")
        return 0
    except (DemoCutError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
