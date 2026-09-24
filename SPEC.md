# Product spec

`verify-app` is a portable skill for coding agents that verify application changes through real user actions.
It helps an agent discover a codebase, prepare a repeatable procedure, exercise the requested behavior, and retain evidence.
When authorized, the agent can publish that evidence in a GitHub PR description.

The output must let a reviewer identify what was checked, what happened, and what remains untested.
A passing build, accepted screenshot, or completed upload proves only its own check.

## Boundary

| Owner | Responsibility |
| --- | --- |
| Repository | Runtime requirements, startup commands, application rules, accounts, and relevant user paths. |
| Coding agent | Scope decisions, project discovery, real interactions, visual review, and truthful reporting. |
| Browser or application tool | Navigation, authentication, input, screenshots, recordings, and observable runtime state. |
| Capture helper | Managed capture settings, file integrity, media checks, and accepted-file output. |
| Evidence formatter | Comparison markup, exact replacement of its marked section, and attachment selection. |
| GitHub CLI | Authorized uploads and replacement of local Markdown references with attachment URLs. |

The instructions must work with different coding agents and codebases.
Use an existing repository skill or ordinary Markdown when the agent has no skill system.
Do not require a particular editor, framework, package manager, or deployment provider.

Browser, CLI, API, desktop, mobile, and library checks use the relevant public interface.
The bundled capture helper has a narrower scope: agent-browser desktop captures on macOS or Linux.
It needs Python 3, agent-browser 0.38.1 or later, FFmpeg, and ffprobe.
The Python helpers require no third-party Python packages.

## Status convention

Checked items below describe features present in the instructions or helpers.
They do not mean every workflow has passed a live test.
The verification section records the current evidence and its limits.
Unchecked items are proposed work, not release commitments.

## Foundation: project setup and verification

- [x] Discover the actual application root, runtime, startup commands, readiness checks, and current address.
- [x] Reuse existing verification procedures and feature maps.
- [x] Create a project procedure when missing, using repository conventions and available tools.
- [x] Keep setup in the task report when the task is read-only.
- [x] Check startup commands for installations, migrations, workers, and shared-resource writes.
- [x] Identify shared dependencies, caches, databases, accounts, and processes before assuming isolation.
- [x] Exercise real public interfaces and inspect observable results, errors, and relevant failed requests.
- [x] Check persistence through reload or another public view when the expected behavior includes saved state.
- [x] Record mock boundaries and the claims they cannot support.
- [x] Stop only owned sessions and processes; retain evidence after cleanup.

### Project procedure

The procedure must let another agent repeat the check without prior project context.
It records preparation, startup, health checks, access, user actions, expected results, evidence commands, and cleanup.
Commands and routes must come from the codebase or observed runtime output.
Unknown steps remain explicitly unverified.

Start the feature map with the requested behavior and required primary paths.
Include relevant alternate entry points, account or data state, side effects, and persistence checks.
A setup is verified only after the agent executes one representative path and validates its evidence.
Other mapped features remain untested until exercised.

Setup does not expand task authorization.
Do not install dependencies when prohibited or repeat consequential actions merely to improve a recording.

## Evidence: capture and acceptance

- [x] Require managed screenshots and recordings for supported agent-browser desktop checks.
- [x] Use a 1440 × 900 viewport at scale 2, with 2880 × 1800 output.
- [x] Record H.264 video with yuv420p at 60 fps, without audio.
- [x] Check origin, viewport, scale, font readiness, and visible image readiness around capture.
- [x] Validate recorded hashes, decoding, dimensions, media settings, and capture completion.
- [x] Reject missing, changed, extra, empty, incomplete, or unsupported media.
- [x] Require a fresh successful validation immediately before sharing and use only accepted files.
- [x] Keep screenshot quality, video quality, and application results as separate judgments.
- [x] Require a declared capture and validation procedure for unsupported tools, devices, or formats.

### Acceptance limits

File validation establishes capture settings and integrity. It does not establish application correctness or visual quality.
Hashes detect later changes; they do not authenticate the author.
Measurements before and after capture cannot detect every temporary change during a recording.
A file marked 60 fps does not prove 60 distinct frames each second.

The agent must inspect readable text, small controls, and relevant visual detail.
For video, inspect later frames and full playback at normal speed where available.
Report unavailable review steps and remaining defects.

Keep original media unchanged. Store diagnostic derivatives outside the managed capture directory.
If an alternative validation check cannot run, report incomplete evidence validation.
Completed application checks remain distinct from that evidence gap.

## Publishing: reviewable evidence

- [x] Prepare image comparisons, after-only previews, and standalone video references.
- [x] Distinguish code changes from user actions and previews.
- [x] Freshly validate each managed capture directory before preparing the attachment plan.
- [x] Preserve text outside one reserved evidence section exactly, including whitespace.
- [x] Reject unmatched, reversed, or duplicate evidence markers.
- [x] Append safely when no evidence markers exist; permit an agent-positioned empty section near the introduction.
- [x] Keep local formatting separate from publication.
- [x] Document GitHub CLI 2.99 attachment support, access requirements, and partial-failure recovery.
- [x] Put PR evidence in the description. Do not use comments as upload storage.
- [ ] Verify the complete publication flow against a dedicated live PR fixture.

### Comparison meaning

| Type | Required meaning |
| --- | --- |
| Code change | Labels identify the source revisions or builds. Conditions match across the pair. |
| User action | Labels identify the initial and resulting states. The report names the action and expected result. |
| Preview | Only the new state exists. No invented baseline is shown. |

Match the viewport, account state, data, and relevant page region.
Place the main evidence first. Label supplemental demonstrations and disclose their limits nearby.
A screenshot pair shows two states; an action record or recording establishes the interaction between them.

The formatter accepts managed PNG and MP4 files. Other validated formats use a manual publishing procedure.
It prepares a body and a unique attachment list, with no more than 50 files.
It does not select revisions, infer comparison equivalence, or determine whether the application passed.

### Publication contract

Use installed CLI help to confirm capabilities before publishing.
Read the existing PR body and preserve its template, text, and successful attachment URLs.
If the remote body changes before publication, regenerate the plan from the current body.

Revalidate immediately before uploading and keep files unchanged until upload completes.
Local validation and remote publication do not share an atomic lock.
Repeated local formatting produces the same output. Repeated uploads can create new assets.

A nonzero upload exit can still leave successfully uploaded attachments in the PR.
Fetch the saved body after every attempt. Preserve successful URLs and retry only unresolved files.
Open the rendered PR to confirm image pairing, reading order, and video playback.
Do not report publication as verified from an upload exit code alone.

## Proposed next work: broader evidence and stronger checks

### Target discovery and comparison

- [ ] Test route selection from representative diffs, including shared components and new routes.
- [ ] Test address discovery with changed deployment URLs, base paths, locales, and query state.
- [ ] Test equivalent state across revisions, including accounts, feature flags, seeded data, and scroll position.
- [ ] Detect or explain comparisons with different framing, scale, content, or unexpected identical images.
- [ ] Repeat affected captures when later code changes invalidate their evidence.

These decisions currently rely on agent instructions and judgment. They are not automatic checks in the helpers.

### Capture coverage

- [ ] Add independent trials for a CLI, an API, and a non-Next.js application.
- [ ] Test a complete alternative capture procedure for mobile or another browser tool.
- [ ] Test video quality during real movement, including duplicate-frame and playback limits.
- [ ] Test rejected login, loading, blank, and error states against each scenario's expected result.

An error screen can be valid evidence for an error-path check. Its meaning depends on the expected result.

A recording contains the agent's idle time between actions, so its length does not match how much content it has. A watchable demo is recorded as separate gesture takes, with the recorder stopped between them, then joined by `scripts/demo_join.py` outside the managed directory. Do not cut still frames out of the evidence file. The demo is presentation material, not evidence.

### Publishing verification

- [ ] Check image pairing and standalone video playback in a rendered fixture PR.
- [ ] Verify repeated section replacement preserves unrelated remote text.
- [ ] Exercise partial upload failures and recovery without duplicate attachments.
- [ ] Run an independent agent through the complete authorized publication workflow.

### Evaluation quality

- [ ] Measure actual instruction reads and token use for representative tasks.
- [ ] Compare task outcomes before and after instruction changes using the same evaluation conditions.
- [ ] Extend behavior checks without assigning old trial results to changed skill files.

Static scores are diagnostic signals. Do not remove useful checks or tests merely to reduce a size estimate.

## Verification and completion

The current local suite contains 34 tests: 22 capture-helper tests and 12 formatter tests.
Coverage includes acceptance and rejection, capture completion, media decoding, locking, body preservation, and formatter error paths.
Media tests need FFmpeg and ffprobe; skipped tests must remain visible in the result.

A real capture set was used to check fresh validation, attachment selection, and repeated local formatting.
Earlier application trials used chatbot-2, chatbot-template, and demoapp.
Those trials have different outcomes and belong to specific earlier skill revisions.
They do not establish current success across every supported interface or coding agent.

Live GitHub attachment publication has not been tested for this formatter.
The publication procedure was checked against installed gh 2.99 help and its documented behavior.

For each verification task:

1. Define the requested behavior, permitted actions, and observable success conditions.
2. Discover or confirm the project procedure and required state.
3. Exercise the public user path and record what happened.
4. Capture and validate suitable evidence; inspect visual quality where relevant.
5. Fix problems within scope or report the exact failure or blocker.
6. Publish only when authorized, then inspect the saved and rendered result.
7. Clean up owned resources and report passed, failed, and untested checks separately.

A task is complete when each required check has a supported result and each material gap has an explicit reason.
A blocked or failed task can be reported completely without being described as verified successfully.

## Implementation references

- [Skill instructions](SKILL.md)
- [Project setup](references/project-setup.md)
- [Browser evidence](references/browser-evidence.md)
- [Video recording and review](references/natural-recording.md)
- [Evidence formatting and GitHub publishing](references/publish-evidence.md)
- [Capture helper](scripts/evidence.py)
- [Evidence formatter](scripts/format_evidence.py)
