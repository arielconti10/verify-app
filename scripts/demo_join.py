#!/usr/bin/env python3
"""Join demo takes that were recorded separately.

The evidence recording stays continuous. A watchable demo does not come from cutting that file.
Freeze detection treats a pointer move as a still image, because the pointer changes too few pixels,
and the cut then removes the gesture.

Record each gesture as its own take. Stop the recorder while choosing the next action. This script
only places those takes one after another, without trimming or re-encoding.

Usage:
    python3 scripts/demo_join.py take-1.mp4 take-2.mp4 -o demo.mp4
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class DemoJoinError(Exception):
    pass


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise DemoJoinError(f"{name} not found on PATH. Install ffmpeg.")


def capture_directory(path: Path) -> Path | None:
    for parent in path.parents:
        if (parent / "capture.json").is_file():
            return parent
    return None


def concat_list(videos: list[Path]) -> str:
    lines = []
    for video in videos:
        escaped = str(video).replace("'", "'\\''")
        lines.append(f"file '{escaped}'")
    return "\n".join(lines) + "\n"


def join(videos: list[Path], output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="demo-join-") as directory:
        listing = Path(directory) / "list.txt"
        listing.write_text(concat_list(videos))
        result = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-nostats",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(listing),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                "-y",
                str(output),
            ],
            capture_output=True,
            text=True,
        )
    if result.returncode != 0:
        raise DemoJoinError(f"ffmpeg failed to join:\n{result.stderr[-800:]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("videos", type=Path, nargs="+", help="takes in playback order")
    parser.add_argument("-o", "--output", type=Path, required=True, help="joined demo file")
    args = parser.parse_args()

    try:
        require_tool("ffmpeg")
        videos = [video.resolve() for video in args.videos]
        output = args.output.resolve()
        for video in videos:
            if not video.is_file():
                raise DemoJoinError(f"File not found: {video}")
            if video == output:
                raise DemoJoinError("The output cannot be one of the takes")
        if len(videos) < 2:
            raise DemoJoinError("Pass at least two takes")
        managed = capture_directory(output)
        if managed is not None:
            raise DemoJoinError(
                f"{managed} is a managed capture directory.\n"
                "Write the demo outside it so the joined file is not treated as evidence."
            )
        join(videos, output)
        print(f"demo: {output}")
        return 0
    except (DemoJoinError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
