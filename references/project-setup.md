# Set up project verification

Create a repeatable way to start the application, exercise a real user path, and retain evidence.
Write for another coding agent that has no prior project context.
Use the current agent's available tools and the repository's conventions. Do not assume a particular editor, model, or package manager.

## Inspect the project

Find these facts in repository instructions, startup scripts, routes, tests, and runtime output:

| Area | Find |
| --- | --- |
| Interface | What the user operates: browser, terminal, API, desktop, mobile, or library. |
| Startup | Runtime versions, dependency commands, service commands, configuration, and readiness signals. |
| Access | Application address, sign-in method, test account source, and required data. |
| Control | Available browser tools, terminal sessions, public endpoints, or application automation. |
| Observation | Screenshots, recordings, logs, response bodies, exit codes, and saved outputs. |
| Isolation | Shared services, ports, accounts, databases, profiles, and session ownership. |

Ask only for missing facts that prevent the requested verification.
Check existing tool support before choosing new dependencies. Prefer the project's working verification tools.
Resolve the current address from the running instance or project command. Do not invent ports or branch URLs.
Check automatic saves and other side effects before using shared data.
Keep credentials in the approved local store. Record how to obtain access, not secret values.

## Choose where to save the procedure

Reuse an existing verification procedure when possible.
If the agent supports repository skills, use the repository's established skill directory and a SKILL.md entry file.
Include a name and description that identify the application, interface, and intended use.
If skills are unsupported, use a normal Markdown procedure in the repository's documentation directory.
Link it from an existing agent instruction file when that file supports such references.
Do not create an editor-specific directory or modify unrelated agent settings.
For a read-only task, provide the procedure in the task report and continue permitted verification.

Keep references relative to the procedure. Do not depend on the author's home directory or global skill installation.
When copying helper files, include their required references and show the exact invocation.
If a helper is optional, describe the supported alternative and its evidence limits.

## Write executable steps

Include only commands, routes, and selectors established from the project.
The procedure must cover:

- Launch: dependency preparation, startup commands, readiness signal, and ownership of each started process.
- Doctor: a read-only check for the intended build, address, required services, and sign-in state.
- Drive: real user actions through the selected tool, with stable selectors or command prompts.
- Evidence: actions, expected results, observed results, saved outputs, and the evidence directory.
- Cleanup: shutdown of owned processes and sessions, with evidence retained.

For short-lived commands, launch means preparation followed by a separate command or terminal session for each check.
For shared instances, state which actions are safe and which resources the agent must leave running.
Use dry-run or test modes only after checking what they actually skip.
Do not replace real interaction with internal state changes or test-only endpoints.
State any mocked boundary and the claims it cannot support.
Mark unresolved steps as unverified. Do not fill them with plausible commands.

## Map the relevant features

Start with the requested feature and the primary user paths needed for verification.
For several workflows, create a small index and a separate file for each substantial feature.
For a small application, keep the map in the procedure.

For each feature, record:

- User entry points and required account or data state.
- Relevant sub-features and alternate entry points.
- Actions through the selected tool.
- Observable results and checks for saved changes.
- Known limits, side effects, and cleanup requirements.

Use stable labels, roles, routes, command flags, and prompt strings where possible.
Link the map from the procedure. Keep shared startup and capture instructions in one place.

## Test the setup

Run the written procedure on one representative feature within the authorized task scope.
Check startup, health, the user action, its result, evidence capture, and cleanup.
Confirm that evidence remains after cleanup. Record which feature passed and which mapped features remain untested.
Do not repeat consequential actions only to test the procedure.
If startup fails, inspect the actual error. Repair only faults within scope, then repeat the affected check.
Clean up owned resources after failed attempts too.
If a required tool, account, or runtime is unavailable, report the exact blocker and mark runtime verification incomplete.
Do not present an unexecuted procedure as verified.

## Keep it current

When an observed change invalidates a command or user path, update that part of the procedure.
Check the changed path again. Do not add scheduled maintenance unless requested.
