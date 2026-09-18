# Browser evidence

## Choose the capture path

Read the installed browser tool's instructions. Supported agent-browser desktop captures must use the bundled helper, including screenshot-only runs.
Requirements: macOS or Linux, Python 3, agent-browser 0.38.1+, FFmpeg, and ffprobe on PATH.
Run `agent-browser doctor` before video capture. Do not modify the installed browser package.

The fixed profile uses a 1440 × 900 viewport, scale/DPR 2, and 2880 × 1800 output.
Video is H.264, yuv420p, 60 fps, without audio. These are helper settings, not universal application requirements.
Do not resize managed media, change its settings, or edit its record to pass validation.

## Alternative capture

Use an alternative only when the desktop profile cannot serve the required tool, environment, or format.
Missing dependencies require an authorized installation or an explicit blocker, not a silent fallback.
Before capture, document the reason, tool, application, session, settings, and checks for:

- Intended application and account; a task-owned session where supported.
- Declared viewport/device settings, output dimensions, fonts, and completed image loading.
- Original files, complete capture, decoding, and actual format.
- Video duration, frame rate, and dimensions throughout the recording.
- File hashes after capture and fresh integrity validation immediately before sharing.
- An explicit accepted-file list that excludes missing, changed, or failed files.

Use tool metadata and file inspection. Never invent unavailable measurements.
For full-page images, derive expected dimensions from page extent.
If a required check cannot run, name it and report incomplete validation. Such files are diagnostic material, not accepted evidence.
Visual review remains separate from file checks.

## Initialize

Set `SKILL_DIR` to this skill's folder and `APP_URL` to the verified HTTP/HTTPS application address.
Set `VERIFY_DIR` to a new directory outside tracked source. Confirm checkout ownership first; the helper does not establish it.

```sh
python3 "$SKILL_DIR/scripts/evidence.py" init "$VERIFY_DIR" "$APP_URL"
```

For saved authentication, add `--state "$STATE_FILE"`; keep credentials outside evidence.
Use the returned session as `BROWSER_SESSION`. The helper creates a fresh session with isolated launch configuration.
It checks origin, viewport, scale, fonts, and visible images before and after capture.
Sign in before capturing protected features. After cross-origin sign-in, return to the application origin.

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

Omit `start` and `stop` for screenshot-only runs. Video includes the pointer option; confirm its visibility during review.
Keep viewport, zoom, launch settings, and origin unchanged during capture.
For video interaction and review, read [natural recording](natural-recording.md).

## Validate and review

Do not edit `capture.json`, which stores measurements, settings, and hashes.
Immediately before sharing, run `check`; require exit code zero and share only returned files.
It rejects missing, extra, changed, incomplete, empty, or unsupported media.
It checks codecs, decoding, dimensions, frame rate, duration, and later-frame dimensions.
Videos must last more than zero seconds and at most five minutes.
Keep extracted frames and alternative media outside the managed directory. Logs and snapshots may accompany evidence.

Inspect screenshot text, icons, and edges at original dimensions and intended display size.
Use [video review](natural-recording.md#review) for playback and frame comparisons. Report visual review separately.
File checks do not prove sharpness, smooth motion, or application correctness.
Hashes detect later changes; they do not authenticate the author. This local check is not a security boundary.
Measurements before and after capture cannot detect every temporary setting change.

## Failed captures

Preserve the failed directory. Fix the cause and start a new run; do not clear records or remove failures to obtain a pass.
For an active recording, stop and close only its named session:

```sh
agent-browser --session "$BROWSER_SESSION" record stop
agent-browser --session "$BROWSER_SESSION" close
```

Failed initialization stores the session name in `capture.json` for cleanup.

## Helper tests

```sh
python3 "$SKILL_DIR/scripts/test_evidence.py"
```

FFmpeg enables media tests. This suite checks the helper, not application behavior.
