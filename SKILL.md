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

Read repository instructions, startup scripts, relevant tests, and the changed entry points.
Determine the runtime version, startup command, readiness check, application address, sign-in method, and test data.
Confirm the checkout and existing processes before starting another instance.
Use the repository's address discovery command when one exists. Do not guess a branch URL or port.
Check which services and data stores are shared. Do not assume a worktree isolates the database.
Ask only for information that cannot be found and blocks the requested check.

Choose the interface the user actually uses:

| Interface | Verification method |
| --- | --- |
| Web | Use the available browser tool. Prefer the project's existing browser procedure. |
| CLI or TUI | Run the real command. Use an isolated terminal session for interactive input. |
| API | Send requests through the public endpoint with the applicable identity. |
| Desktop or mobile | Use the available application automation tool on the intended build. |
| Library | Exercise the public API with realistic inputs and inspect its outputs. |

Use relevant automated tests as additional evidence. A passing test does not prove an untested user path.
Use the setup procedure and feature map to select the required checks.
Install missing tools only when necessary and within the task scope.

## Prepare and check

Use the documented runtime and dependency versions. Reuse a healthy instance only when it serves the intended checkout.
Start required services with the repository's commands. Keep their process identifiers or terminal session identifiers.
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

For agent-browser desktop capture, read [browser evidence](references/browser-evidence.md).
It includes a managed capture helper and file validation. It requires Python 3, agent-browser, FFmpeg, and ffprobe.
The helper supports macOS and Linux. Other browser tools can follow the same evidence principles without this helper.
Use [natural recording](references/natural-recording.md) for pointer movement, typing, and visual review when recording video.
Mobile, full-page, and other capture formats need a suitable tool and declared settings. Do not omit required coverage to fit the helper.

Keep original media. Exclude secrets and unrelated private data before capture.
Check actual dimensions and decoding. Review small text, thin icons, and later video frames at their intended display size.
Review the complete video at normal speed when possible. Report unavailable playback review.
File validation does not prove sharpness, smooth motion, or application correctness.

## Share and report

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
