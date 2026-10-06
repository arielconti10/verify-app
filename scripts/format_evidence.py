"""Prepare a PR body and attachment list from freshly checked managed evidence.

With --pr and --repo, fetch the existing description, merge the evidence section, and with
--publish update the PR. The existing description is never printed: it can contain text
written by other people, so it stays inside this script."""

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


def outside(body):
    if START in body and END in body:
        return body[: body.index(START)], body[body.index(END) + len(END) :]
    return body, ""


def section(body):
    return body[body.index(START) : body.index(END) + len(END)]


def gh(*args):
    return evidence.subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False, timeout=600
    )


def fetch(pr, repo):
    result = gh("pr", "view", pr, "--repo", repo, "--json", "body,url")
    evidence.require(result.returncode == 0, f"gh pr view failed: {result.stderr.strip()[:300]}")
    data = json.loads(result.stdout)
    return data["body"], data["url"]


def publish(manifest, base, pr, repo, apply):
    body, url = fetch(pr, repo)
    plan = prepare(manifest, base, body)
    summary = {"pr": url, "attachments": plan["attachments"], "section": section(plan["body"])}
    if not apply:
        return dict(summary, status="ready"), 0
    with evidence.tempfile.NamedTemporaryFile("wb", suffix=".md", delete=False) as handle:
        handle.write(plan["body"].encode("utf-8"))
    try:
        command = ["pr", "edit", pr, "--repo", repo, "--body-file", handle.name]
        for path in plan["attachments"]:
            command.extend(["--attach", path])
        edit = gh(*command)
    finally:
        Path(handle.name).unlink()
    published, _ = fetch(pr, repo)
    unchanged = outside(published) == outside(plan["body"])
    unresolved = [p for p in plan["attachments"] if p in published]
    status = "published" if edit.returncode == 0 and unchanged and not unresolved else "incomplete"
    summary.update(
        status=status,
        section=section(published) if START in published and END in published else None,
        outside_unchanged=unchanged,
        unresolved=unresolved,
        gh_error=edit.stderr.strip()[:300] if edit.returncode else None,
    )
    return summary, 0 if status == "published" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--body-file", type=Path, help="Body you wrote for a new PR")
    parser.add_argument("--pr", help="Existing PR number; requires --repo")
    parser.add_argument("--repo", help="OWNER/REPO of the existing PR")
    parser.add_argument("--publish", action="store_true", help="Update the existing PR")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text())
        base = args.manifest.resolve().parent
        if args.pr or args.repo or args.publish:
            evidence.require(args.pr and args.repo, "--pr and --repo are both required")
            evidence.require(not args.body_file, "--body-file is only for new PRs")
            summary, code = publish(manifest, base, args.pr, args.repo, args.publish)
            print(json.dumps(summary, indent=2))
            return code
        body = args.body_file.read_bytes().decode("utf-8") if args.body_file else ""
        print(json.dumps(prepare(manifest, base, body), indent=2))
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
