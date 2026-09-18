# Browser evidence

## Choose the capture path

Use the browser tool available in the current environment. Check its installed documentation before driving the page.
Use the bundled helper for supported agent-browser desktop captures, including screenshots without video.
It uses agent-browser 0.38.1 or later and a fixed desktop profile.
It needs Python 3, FFmpeg, and ffprobe on PATH. Its file lock requires macOS or Linux.
When using the helper, run `agent-browser doctor` before video capture. Do not modify the installed browser package.

This profile uses a 1440 × 900 viewport, native scale 2, and device pixel ratio 2.
PNG and MP4 dimensions are 2880 × 1800. Video uses H.264, yuv420p, and 60 fps, without audio.
These are helper settings, not universal application requirements.
For unsupported environments or formats, follow the alternative capture requirements below.
Do not select an alternative merely to skip managed capture or its checks.
Do not resize managed media or edit its record to pass validation.

## Alternative capture

Use an alternative when the bundled desktop profile cannot serve the required tool, environment, or capture format.
Before capture, record the reason, selected tool, target application, session, capture settings, and validation procedure.
The procedure must check:

- The intended application and account, with a separate task-owned session where supported.
- Declared viewport or device settings, output dimensions, and completed image loading.
- Original files, complete capture, successful decoding, and the actual media format.
- For video, duration, frame rate, and frame dimensions throughout the recording.
- File hashes after capture, with a fresh integrity check immediately before sharing.
- An explicit list of accepted files. Missing, changed, or failed files cannot pass.

Use available tool metadata, commands, and file inspection. Do not fabricate measurements unavailable from the tool.
For full-page images, declare expected dimensions from the page extent instead of the viewport.
Keep visual review separate. File checks cannot prove readability, smooth motion, or correct application behavior.
If a required check cannot run, mark evidence validation incomplete and name the missing check.
Unvalidated files may remain as diagnostic material. Do not present them as accepted verification evidence.
Missing dependencies do not justify a silent fallback. Use an authorized installation or report the missing capture capability.

## Initialize

Set `SKILL_DIR` to the installed skill folder. Set `APP_URL` to the verified address for the intended checkout.
Use a new evidence directory outside tracked source files. The examples assume these shell variables are set.
The helper accepts HTTP and HTTPS addresses. It does not verify checkout ownership; check that before initialization.

```sh
python3 "$SKILL_DIR/scripts/evidence.py" init "$VERIFY_DIR" "$APP_URL"
```

For saved authentication, add `--state "$STATE_FILE"`. Keep that file outside the evidence directory.
Use the returned session value as `BROWSER_SESSION` for all subsequent actions.
The helper isolates launch configuration from agent-browser defaults and creates a fresh named session.
It checks origin, viewport, scale, fonts, and visible images before and after capture.
An unauthenticated landing page can initialize the session; complete sign-in before capturing protected features.
For cross-origin sign-in, return to the application origin before capture. The helper rejects captures on another origin.

## Capture

```sh
agent-browser --session "$BROWSER_SESSION" snapshot -i
python3 "$SKILL_DIR/scripts/evidence.py" screenshot "$VERIFY_DIR" before.png
python3 "$SKILL_DIR/scripts/evidence.py" start "$VERIFY_DIR" interaction.mp4
# Perform the authorized interaction in the returned session.
python3 "$SKILL_DIR/scripts/evidence.py" stop "$VERIFY_DIR"
python3 "$SKILL_DIR/scripts/evidence.py" screenshot "$VERIFY_DIR" after.png
agent-browser --session "$BROWSER_SESSION" errors
agent-browser --session "$BROWSER_SESSION" console
python3 "$SKILL_DIR/scripts/evidence.py" check "$VERIFY_DIR"
python3 "$SKILL_DIR/scripts/evidence.py" close "$VERIFY_DIR"
```

Record only when a video is needed. A screenshot-only run can pass validation.
The wrapper starts recording with the visible pointer option. Confirm pointer visibility during review.
Keep viewport, zoom, launch settings, and origin unchanged during a managed take.
Prepare the action sequence before recording. Use readiness checks between actions; stop on unexpected behavior.
Do not pause to plan during a take. Inspect unexpected states after stopping it.
Keep contact-sheet processing off during capture. Extract review frames afterward into a separate directory.

## Validate and review

`capture.json` records measurements, file hashes, and capture settings. Do not edit it.
Run `check` immediately before sharing; require exit code zero and share only the returned files.
The validator rejects missing, extra, changed, incomplete, empty, or unsupported media.
It checks actual codecs, dimensions, frame rate, duration, and decoding, including dimensions of later frames.
Recordings must last more than zero seconds and no more than five minutes.
Snapshots and logs may accompany evidence. Keep extracted frames and alternate captures outside the managed directory.

Review screenshots and video separately. A sharp screenshot does not prove sharp video.
Compare a validated screenshot with a later stable video frame showing the same state.
A 60 fps file can contain repeated frames. Static holds are normal; judge cadence during actual movement.
Check full playback, transitions, scrolling, pointer movement, and the final result at normal speed.
If available, record playback completion, errors, and `getVideoPlaybackQuality()` frame counts.
Decoded frames and playback statistics cannot replace visual review. State which checks were possible.

This is a local error check, not a signed attestation or security boundary.
Hashes detect changes after capture. They do not authenticate the author or establish that the feature works.
Before-and-after measurements cannot detect every temporary setting change during recording.

## Failed captures

Keep the failed directory for diagnosis. Start another run after fixing the cause.
If capture fails with an active recording, stop only its named session:

```sh
agent-browser --session "$BROWSER_SESSION" record stop
agent-browser --session "$BROWSER_SESSION" close
```

Do not erase failed media or clear the record to make validation pass.
A failed initialization also saves its session name in `capture.json` for scoped cleanup.

## Test the helper

```sh
python3 "$SKILL_DIR/scripts/test_evidence.py"
```

The suite tests acceptance, rejection, URL handling, locking, and actual media decoding when FFmpeg is installed.
It does not verify a project's application behavior.
