# Set up project verification

Write for an agent without project context. Use repository conventions and available tools.

## Discover

Read repository instructions, startup scripts, routes, tests, and runtime output. Establish:

| Area | Required facts |
| --- | --- |
| Interface | Browser, terminal, API, desktop, mobile, or library entry points. |
| Startup | Runtime versions, dependency and service commands, configuration, readiness signals. |
| Access | Address discovery, sign-in method, test account source, required data. |
| Tools | Available interaction tools and evidence outputs. |
| Isolation | Shared services, dependencies, caches, databases, accounts, and session ownership. |

Check startup scripts and wrappers for automatic installations, migrations, and worker activity.
Use the real checkout and normal startup. Record deviations and verification limits.
Symbolic links can share writes. Git status does not establish unchanged dependencies.
When installation is prohibited, establish a startup path that cannot install dependencies or report the blocker.
Stop the owned process if unexpected installation begins. Report what the logs establish.
Check automatic saves before using shared data. Record credential access methods, never secret values.

## Save the procedure

Reuse an existing procedure. Otherwise, use the repository skill directory or ordinary Markdown documentation.
For SKILL.md, name and describe the application and interface. Link the procedure from existing instructions where supported.
Do not create editor-specific settings. For read-only tasks, put the procedure in the task report.

Keep references relative. A portable procedure must not depend on the author's home directory or global skill installation.
If it must work without this skill, copy the helper and required references.
Use the project runner or Python. Preserve working validation commands.

## Write executable steps

Use commands, routes, and selectors established from the project. Mark unresolved steps as unverified.

- **Launch:** preparation, startup, readiness, and ownership of started processes.
- **Health:** read-only checks for the intended build, address, services, and sign-in state.
- **Actions:** public user paths with stable selectors, routes, flags, or terminal prompts.
- **Evidence:** expected and observed results, output paths, capture and validation commands.
- **Cleanup:** stop owned resources and retain evidence. Identify shared resources that must remain running.

For short-lived commands, document preparation and each invocation.

For supported agent-browser desktop evidence, include managed initialization, capture, fresh validation, and cleanup commands.
This includes screenshot-only checks. For other tools, use [alternative capture requirements](browser-evidence.md#alternative-capture).
Missing validation remains incomplete; setup cannot make it optional.

## Map features

Map the requested feature and required primary paths in the procedure. Split substantial workflows into linked feature files.
Each feature needs entry points, account/data state, actions, observable results, persistence checks, side effects, and cleanup.
Include relevant alternate entry points. Keep shared startup and capture commands in one place.

## Test and maintain

Execute the procedure on one representative feature within the authorized scope.
Check startup, health, interaction, result, evidence validation, and cleanup. Confirm that evidence remains afterward.
For managed media, require a fresh successful `check` before accepting files.
Record the tested feature and remaining gaps. Never present an unexecuted procedure as verified.
Follow the scope and cleanup rules in SKILL.md after failures.
Update invalid steps and repeat affected checks. Schedule maintenance only when requested.
