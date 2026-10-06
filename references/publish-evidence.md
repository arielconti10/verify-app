# Prepare and publish evidence

Read this only when preparing evidence for a review or publishing an authorized PR description.
The formatter changes GitHub only when you pass `--publish`.

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

Set `SKILL_DIR`, `REPORT_DIR`, `REPO`, and `PR` to the intended skill, output folder, repository, and PR.
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

For an existing PR, run the formatter with `--pr` and `--repo`. It reads the current description itself and merges the evidence section.
The description can contain text from other people, so the formatter never prints it.
Do not fetch or read the description yourself; review only the evidence section in the formatter's output.

```sh
python3 "$SKILL_DIR/scripts/format_evidence.py" "$REPORT_DIR/comparisons.json" \
  --pr "$PR" --repo "$REPO"
```

Require exit code zero and `"status": "ready"`. The output lists `attachments` and the generated `section`.
The formatter locks and freshly validates each capture directory. It rejects unaccepted files and more than 50 attachments.
It creates image tables and puts video references on separate lines for GitHub playback.

For a new PR, write its description yourself and pass it with `--body-file` instead.
That mode prints a plan with the full `body` and `attachments`, which are your own text and files.

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
Add `--publish` to the same command. The formatter then:

1. Reads the current description again, so edits made by other people since the last run are kept.
2. Revalidates the files and merges the evidence section.
3. Runs `gh pr edit --body-file … --attach …` with an argument list, not shell evaluation.
4. Reads the result and compares the text outside the evidence markers byte for byte with what it sent.

```sh
python3 "$SKILL_DIR/scripts/format_evidence.py" "$REPORT_DIR/comparisons.json" \
  --pr "$PR" --repo "$REPO" --publish
```

Require exit code zero and `"status": "published"`. The output reports `outside_unchanged`, `unresolved` attachment paths,
any `gh_error`, and the published `section`. Keep files unchanged until it finishes; there is no atomic lock between
local validation and the remote upload.

**`"status": "incomplete"` can still mean partial publication.** Upload stops at the first failure, but earlier
successes can be saved. Report the summary, keep the local evidence, and rerun only after fixing the cause.
A rerun regenerates the whole section and uploads every file again.

For a new authorized PR, use the `--body-file` plan's body and attachments with `gh pr create`, plus its title, base, and head.
Do not treat `--dry-run` as an upload test; it is incompatible with PR attachments.

Check the published `section` for labels, image pairing, and placement. Rendering and video playback need a look
at the PR page; ask the user to check them rather than reading the whole description yourself.
Report missing access or unsupported uploads as blockers. Preserve local evidence and successful partial results.

References: [gh pr edit](https://cli.github.com/manual/gh_pr_edit), [gh pr create](https://cli.github.com/manual/gh_pr_create),
[GitHub CLI 2.99 release](https://github.com/cli/cli/releases/tag/v2.99.0).
