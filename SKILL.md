---
name: verify-app
description: Verify application changes through real user actions and save evidence. Use when setting up project verification or checking browser flows, CLI commands, APIs, or PR evidence.
---

# Verify an application

Prove the requested behavior through the application's public interface. Connect each claim to an action and an observed result.
Use the repository's verification instructions when available. This skill supplies a method where those instructions need more detail.

## Set up project verification

First, look for an existing project verification procedure and feature map.
If they are missing, follow [project setup](references/project-setup.md) before the first verification run.
Use that step to discover the application, select available tools, and prepare a repeatable procedure.
Reuse a current procedure. Update only steps affected by changed commands, tools, or application behavior.
If the task is read-only, keep the setup in the task report instead of writing repository files.
Setup does not authorize external writes or actions outside the requested task.

## Find the verification path

Use the project procedure to establish runtime, startup, readiness, address, sign-in, and test data.
Confirm the checkout and existing processes. Resolve addresses from running output or the project's discovery command.
Check shared services and data stores; a worktree does not isolate them.
Ask only for unavailable information that blocks the requested check.

Choose the interface the user actually uses:

| Interface | Verification method |
| --- | --- |
| Web | Use the available browser tool. Prefer the project's existing browser procedure. |
| CLI or TUI | Run the real command. Use an isolated terminal session for interactive input. |
| API | Send requests through the public endpoint with the applicable identity. |
| Desktop or mobile | Use the available application automation tool on the intended build. |
| Library | Exercise the public API with realistic inputs and inspect its outputs. |

Use relevant automated tests as additional evidence. A passing test does not prove an untested user path.
Install missing tools only when necessary and within the task scope.

## Prepare and check

Use the documented runtime and dependency versions. Reuse a healthy instance only when it serves the intended checkout.
Use the actual checkout and its normal startup command unless the task requires isolation.
Inspect startup scripts and command wrappers for automatic installs, migrations, and worker startup before running them.
Respect installation limits. A startup command does not exempt an automatic installation from those limits.
Do not treat copied source with linked writable dependencies as isolated.
Keep process identifiers or terminal session identifiers for services you start.
Run the available health check. Check the application address, build, required services, and sign-in state.
If startup fails, inspect the failing check and logs. Fix issues within scope or report the exact blocker.
Use a separate browser or terminal session when possible. Do not take control of another task's session.
Use existing authorized test accounts. Keep credentials and saved browser state out of evidence and shared skill files.

## Exercise the behavior

Select changed entry points and observable success conditions before acting.
Use a maintained feature map if one exists. Cover applicable changed paths and report any gaps.
Use stable labels, roles, test IDs, routes, or command prompts. Refresh browser references after page changes.
Check for automatic saves and other side effects before acting on shared data.
Perform the real action. Do not substitute internal state setters or database edits for the user path.
Inspect the result, runtime errors, and relevant failed requests.
For saved changes, reload or reopen the feature. Check another public view when it can confirm the result.
For CLI work, inspect exit status, output, and changed files. For APIs, inspect status, body, and relevant side effects.
Exercise error paths when they matter to the change. Use mocks only at declared test boundaries and state their limits.
Do not assume a command named dry-run has no side effects. Check its documented and observed behavior.
Do not repeat payments, messages, destructive actions, or other consequential changes just to improve a recording.

## Capture evidence

Save evidence outside tracked source files, in a task-specific directory. Preserve it through cleanup.
Record the checkout, address or command, preconditions, action, expected result, observed result, and artifact paths.
Capture the action and result. A final screenshot alone does not prove the preceding interaction.
Use screenshots for visual details. Use video when motion or a sequence matters, or when the task requires it.
Do not require browser video for a library, backend, or documentation change without a relevant visual claim.

For supported agent-browser desktop capture, use the bundled managed commands for screenshots and videos.
Read [browser evidence](references/browser-evidence.md) before opening the capture session.
Direct screenshots and recordings do not satisfy this capture requirement, including screenshot-only checks.
Run the helper's `check` immediately before sharing. Require exit code zero and use only returned files.
A saved pass report is insufficient.

For other tools, mobile, or unsupported formats, setup must define a capture procedure and its validation checks.
Record the reason for that alternative and follow [alternative capture requirements](references/browser-evidence.md#alternative-capture).
If required validation is unavailable, report evidence validation as incomplete. Do not label those files as accepted evidence.
Keep completed application checks separate from incomplete evidence validation. Do not omit required application coverage to fit the helper.
Read [natural recording](references/natural-recording.md) only for video interaction and review.
For a demo video, make a shorter copy with `scripts/demo_cut.py` and keep it outside the managed capture directory. The demo is not evidence: never present it as a checked asset.
Execute the helper from the documented commands. Read its source or tests only for diagnosis or changes.

Keep original media. Exclude secrets and unrelated private data before capture.
File validation does not establish visual quality or application correctness. Follow the reference's visual review steps.

## Share and report

For comparison layouts or authorized PR publication, read [publish evidence](references/publish-evidence.md).

Report passed checks, failed checks, and checks not run separately. Give a reason for each material gap.
Describe the user action and observed result. Link the relevant evidence.
Do not infer deployment, merge status, or complete product correctness from a local check.
Upload only when the task authorizes it. Follow the destination's attachment rules and preserve existing content.
Check upload support before use. Inspect partial results before retrying, then confirm the saved attachment.
Do not post task results to an issue or comment without authorization.

## Clean up

Stop active recordings first. Close only sessions and processes created for this check.
Use their recorded identifiers. Do not stop a shared service or kill processes by name.
Remove temporary test state only when safe and within scope. Preserve evidence and confirm it still exists.
