# Verify App

A reusable skill for coding agents that verify application behavior through real user actions.

## What it does

- Discovers project startup commands, available tools, authentication requirements, and shared resources.
- Creates a project verification procedure when one is missing.
- Checks browser flows, CLI commands, APIs, and other public interfaces.
- Captures evidence and separates observed results from untested claims.
- Preserves evidence when test sessions and processes stop.

Start with [SKILL.md](SKILL.md). Project setup instructions are in [references/project-setup.md](references/project-setup.md).

## Use with a coding agent

Copy this repository into the skill directory supported by your coding agent. Keep the supporting files with SKILL.md.
For agents without skill support, provide SKILL.md as the task instructions and make its references available.
The optional `agents/openai.yaml` file supplies Codex display metadata. Other agents can ignore it.

Example requests:

- "Set up verification for this repository."
- "Verify the changed checkout flow without submitting an order."
- "Check this CLI command and save evidence of its output."

The procedure uses the project's existing tools and commands. It does not require a particular editor or package manager.

## Example output

This fictional example shows a report for a saved notification setting. Paths and results are illustrative.
The agent selects checks from the user's request and the actual codebase.

```text
Result: PARTIAL — saving works, but the error message check failed.

Context
- Checkout: feature/notification-settings at abc1234.
- Application: http://localhost:3000/settings/notifications.
- Account: local test account. Initial setting: email notifications off.
- Scope: save the setting and check a rejected save. Do not send email.

Passed
- Enabled email notifications and selected Save. The page showed “Saved”.
- Reloaded the page. Email notifications remained enabled.

Failed
- Rejected a save through a declared browser request mock.
- Expected: an error message and no success confirmation.
- Observed: no error message. The page continued to show “Saving”.
- This check covers the interface response, not a real server failure.

Not run
- Email delivery: excluded from the requested scope.
- Mobile layout: no mobile check was requested.

Evidence
- Directory: /tmp/verify-notifications-example/.
- Actions and results: actions.txt.
- Managed screenshots: before.png, after-reload.png, failed-save.png.
- Fresh evidence check: exit code 0; all three screenshots accepted.
- Visual review: labels and controls readable at the intended display size.
- Video: not recorded; this check makes no motion claim.

Cleanup
- Restored the initial setting and confirmed it after reload.
- Removed the request mock. Closed the test browser and owned server.
- Retained the report and evidence files.

Limit
- These results cover the listed local checks. They do not prove deployment
  status, email delivery, or complete application correctness.
```

A real report links its saved evidence. Accepted media confirms file validation; it does not turn a failed application check into a pass.

## Browser capture and validation

The bundled helper requires macOS or Linux, Python 3, agent-browser 0.38.1 or later, FFmpeg, and ffprobe.
It uses a fixed desktop profile: 1440 × 900 viewport, scale 2, and 2880 × 1800 output.
Video uses H.264 at 60 fps. Supported agent-browser desktop checks must use this helper, including screenshot-only checks.
Run its validator immediately before sharing and use only returned files.
Other tools and mobile capture need a declared procedure with validation checks. Missing validation remains incomplete.

See [browser evidence](references/browser-evidence.md) for commands and limits.
File validation checks media settings and integrity. It does not prove application correctness, sharpness, or smooth motion.

## Tests

```sh
python3 scripts/test_evidence.py
```

Media tests require FFmpeg and ffprobe. The suite reports skipped media tests if those tools are absent.

For helper coverage, install Coverage.py in a separate tool environment, then run:

```sh
python3 -m coverage run --branch --source=scripts scripts/test_evidence.py
python3 -m coverage report --include='*/evidence.py'
python3 -m coverage xml --include='*/evidence.py' -o coverage/coverage.xml
```

Coverage reports are local evaluation files. They are not part of the skill bundle.
