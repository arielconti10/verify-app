"""Prepare a local PR body and attachment list from freshly checked managed evidence."""

import argparse
from contextlib import ExitStack
import html
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
import evidence

START = "<!-- verify-app:evidence:start -->"
END = "<!-- verify-app:evidence:end -->"


def text(value):
    evidence.require(isinstance(value, str) and value.strip(), "Labels must be nonempty strings")
    evidence.require(not any(ord(c) < 32 for c in value), "Labels must use one line")
    value = html.escape(value)
    for char in "\\`*_[]|":
        value = value.replace(char, f"&#{ord(char)};")
    return value


def replace_section(body, section):
    counts = body.count(START), body.count(END)
    if counts == (0, 0):
        separator = (
            "" if not body or body.endswith("\n\n") else "\n" if body.endswith("\n") else "\n\n"
        )
        return body + separator + section + "\n"
    evidence.require(counts == (1, 1), "Evidence markers are incomplete or duplicated")
    start, end = body.index(START), body.index(END)
    evidence.require(start < end, "Evidence markers are reversed")
    return body[:start] + section + body[end + len(END) :]


def asset(value, base):
    evidence.require(isinstance(value, str), "Media paths must be strings")
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    # Preserve the filename for the validator's symbolic-link check.
    path = path.parent.resolve() / path.name
    evidence.require(
        not re.search(r"[\s#<>()[\]|]", str(path)),
        "Use media paths without whitespace or #<>()[ ]|",
    )
    evidence.require(path.suffix in (".png", ".mp4"), "Managed evidence supports PNG and MP4")
    return path


def prepare(manifest, base, body):
    pairs = manifest.get("comparisons")
    evidence.require(isinstance(pairs, list) and pairs, "Provide a nonempty comparisons list")
    rows, paths = [], []
    for pair in pairs:
        kind = pair.get("kind")
        evidence.require(
            kind in ("action", "change", "preview"), "Kind must be action, change, or preview"
        )
        before = asset(pair["before"], base) if pair.get("before") else None
        after = asset(pair["after"], base)
        evidence.require((before is None) == (kind == "preview"), "Only preview omits before")
        evidence.require(
            before is None or before.suffix == after.suffix, "Pair media types must match"
        )
        title = text(pair["label"])
        left = text(pair["before_label"]) if before else None
        right = text(pair["after_label"])
        rows.append((kind, title, before, after, left, right))
        paths.extend([before, after] if before else [after])
    paths = list(dict.fromkeys(paths))
    evidence.require(len(paths) <= 50, "GitHub accepts at most 50 attachments per command")
    with ExitStack() as stack:
        for folder in sorted({p.parent for p in paths}):
            lock = stack.enter_context((folder / ".capture.lock").open("a"))
            evidence.fcntl.flock(lock, evidence.fcntl.LOCK_EX | evidence.fcntl.LOCK_NB)
            result = evidence.validate(folder)
            accepted = {item["path"] for item in result["assets"]}
            evidence.require(
                all(p.name in accepted for p in paths if p.parent == folder), "Unaccepted media"
            )
        lines = [START, "## Verification evidence", ""]
        for kind, title, before, after, left, right in rows:
            name = {"action": "User action", "change": "Code change", "preview": "Preview"}[kind]
            lines.extend([f"### {name}: {title}", ""])
            if after.suffix == ".png" and before:
                lines.extend(
                    [
                        f"| Before: {left} | After: {right} |",
                        "| --- | --- |",
                        f"| ![Before: {left}]({before}) | ![After: {right}]({after}) |",
                        "",
                    ]
                )
            else:
                for label, path in ([(left, before)] if before else []) + [(right, after)]:
                    lines.extend([f"**{label}**", "", f"![{label}]({path})", ""])
        lines.append(END)
        return {
            "body": replace_section(body, "\n".join(lines)),
            "attachments": [str(p) for p in paths],
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--body-file", type=Path)
    args = parser.parse_args()
    try:
        body = args.body_file.read_bytes().decode("utf-8") if args.body_file else ""
        plan = prepare(json.loads(args.manifest.read_text()), args.manifest.resolve().parent, body)
        print(json.dumps(plan, indent=2))
        return 0
    except (
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        OSError,
        evidence.subprocess.SubprocessError,
    ) as error:
        print(f"Cannot prepare evidence: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
