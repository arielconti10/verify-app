# Prepare and publish evidence

Read this only when preparing evidence for a review or publishing an authorized PR description.
The local formatter does not upload files or change GitHub.

## Select comparable evidence

Use the same viewport, data, account state, and relevant page region for each pair.
Identify the comparison explicitly:

- **Code change:** before and after labels identify the source revisions or builds.
- **User action:** labels identify the initial and resulting states. Name the action.
- **Preview:** only the new state exists. Do not invent a baseline.

Put the main proof first. Label supplemental demonstrations and their limits separately.
Keep original captures unchanged. Full-page or alternative formats need the validation procedure from browser-evidence.md.
The formatter accepts managed PNG and MP4 files only. Format other validated media manually.
File acceptance does not establish application success; report observed outcomes and untested scope beside the evidence.

## Prepare locally

Set `SKILL_DIR`, `VERIFY_DIR`, `REPORT_DIR`, `REPO`, and `PR` to the intended skill, capture folder, output folder, repository, and PR.
Keep the output folder outside the capture directory. Use media paths without whitespace or Markdown delimiters.
Relative media paths resolve from the manifest directory; output uses absolute paths for reliable attachment matching.

Create `comparisons.json` in `REPORT_DIR`. This example assumes captures are in a sibling `capture` directory:

```json
{
  "comparisons": [
    {
      "kind": "action",
      "label": "Select a model",
      "before": "../capture/before.png",
      "after": "../capture/after.png",
      "before_label": "Default model",
      "after_label": "Selected model"
    }
  ]
}
```

Add objects for other comparisons, in display order. For `change`, supply revision/build labels.
For `preview`, omit `before` and `before_label`. Use matching media types within pairs.
Different capture directories can supply the before and after files; each must contain its managed capture record.

Read the current PR body as JSON to preserve its exact string, including trailing whitespace:

```sh
gh pr view "$PR" --repo "$REPO" --json body > "$REPORT_DIR/pr.json"
python3 - "$REPORT_DIR" <<'PY'
import json, sys
from pathlib import Path
folder = Path(sys.argv[1])
body = json.loads((folder / "pr.json").read_text())["body"]
(folder / "body.md").write_bytes(body.encode("utf-8"))
PY
python3 "$SKILL_DIR/scripts/format_evidence.py" \
  "$REPORT_DIR/comparisons.json" --body-file "$REPORT_DIR/body.md" \
  > "$REPORT_DIR/plan.json"
```

Require exit code zero before using the plan. It contains `body` and a deduplicated `attachments` list.
The formatter locks and freshly validates each capture directory. It rejects unaccepted files and more than 50 attachments.
It creates image tables and puts video references on separate lines for GitHub playback.

The reserved markers are `<!-- verify-app:evidence:start -->` and `<!-- verify-app:evidence:end -->`.
An existing pair is replaced without changing bytes outside it. Unmatched, reversed, or duplicate markers cause an error.
If neither marker exists, the formatter appends the section without changing existing text.
For placement near the top, put an empty marker pair after the introduction or preview link before formatting.
Keep markers outside paragraphs, lists, tables, and code fences. Never replace unrelated PR sections.

## GitHub CLI 2.99 and later: how attach works

Check `gh --version`, `gh pr edit --help`, and `gh auth status` before publishing.
Version 2.99 supports `--attach`; check installed help again after upgrades.
Supported commands include PR and issue create, edit, and comment commands.
For this skill, put PR evidence only in the description with `gh pr create` or `gh pr edit`.
Do not use comments as attachment storage.

- Repeat `--attach PATH` for each file, up to 50 per invocation.
- Supported formats: PNG, JPG/JPEG, GIF, WebP, SVG, MP4, MOV, and WebM.
- Local paths can be absolute or relative to the directory where `gh` runs.
- Matching Markdown destinations are replaced with uploaded URLs. Unreferenced attachments are appended to the body.
- Images can use `--attach './screen.png#Image description'`. Existing Markdown alt text takes precedence.
- Videos cannot use `#alt text`. A standalone `![Recording](./take.mp4)` becomes a player URL.
- Inline video images become links. Reference-style video images are rejected; use reference-style links instead.
- HTML `<video src>` is not the local-path upload workflow. Prefer standalone video references.

Uploads require GitHub.com or a GHE.com tenant, a supported user token, and WRITE, MAINTAIN, or ADMIN repository permission.
OAuth tokens, classic PATs, and fine-grained PATs are supported. GitHub App tokens and GitHub Enterprise Server are unsupported.
PR creation cannot combine attachments with `--web` or `--dry-run`; issue creation cannot combine them with `--web`.
An issue edit with attachments must target one issue.

## Publish and confirm

Run publication only when the task authorizes editing this PR description.
Review the prepared body. Preserve template sections and existing attachment URLs.
Re-read the remote body before publication; if another person changed it, regenerate the plan from that body.
Re-run the formatter immediately before uploading to refresh file validation. Keep files unchanged until upload completes.
There is no atomic lock between local validation and a remote upload.

This Python command uses an argument list, not shell evaluation:

```sh
python3 - "$REPORT_DIR" "$PR" "$REPO" <<'PY'
import json, subprocess, sys
from pathlib import Path
folder, pr, repo = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
plan = json.loads((folder / "plan.json").read_text())
body = folder / "body-next.md"
body.write_bytes(plan["body"].encode("utf-8"))
command = ["gh", "pr", "edit", pr, "--repo", repo, "--body-file", str(body)]
for path in plan["attachments"]:
    command.extend(["--attach", path])
subprocess.run(command, check=True)
PY
```

For a new authorized PR, use the same body and attachments with `gh pr create`, plus its title, base, and head.
Do not treat `--dry-run` as an upload test; it is incompatible with PR attachments.

**A nonzero exit can still mean partial publication.** Upload stops at the first failure, but earlier successes can be saved.
Fetch the body after every attempt. Keep successful URLs and retry only unresolved files; do not resend the entire plan blindly.
Repeated local formatting is stable. Repeated uploads are not guaranteed to reuse existing assets.

```sh
gh pr view "$PR" --repo "$REPO" --json body,url > "$REPORT_DIR/published.json"
```

Check that unrelated text remains intact and that intended assets replaced their local references.
Open the rendered PR. Confirm labels, image pairing, placement, and playable video controls.
Report missing access or unsupported uploads as blockers. Preserve local evidence and successful partial results.

References: [gh pr edit](https://cli.github.com/manual/gh_pr_edit), [gh pr create](https://cli.github.com/manual/gh_pr_create),
[GitHub CLI 2.99 release](https://github.com/cli/cli/releases/tag/v2.99.0).
