# Natural recording method

Use this method when a video is needed. Adjust timings to the interaction.
The commands below apply to agent-browser desktop recordings. Use equivalent supported actions with other tools.
For touch interactions, show taps and scrolling. Do not add a desktop pointer or require mouse movement.
These values are recording defaults, not measurements of human behavior.

## Pointer

Position the pointer near the first control before recording. Allow about 650 ms to read the initial screen.
Use `get box <selector> --json` to read current bounds. Recompute bounds after layout changes.
Choose a point inside the control. Use the text-entry area for inputs.
Move on a curved path for approximately 350–560 ms. Use a stable seed for repeatable takes.

```sh
agent-browser --session "$BROWSER_SESSION" mouse move "$TARGET_X" "$TARGET_Y" --human --duration 450 --seed 17
agent-browser --session "$BROWSER_SESSION" wait 135
agent-browser --session "$BROWSER_SESSION" mouse down
agent-browser --session "$BROWSER_SESSION" wait 75
agent-browser --session "$BROWSER_SESSION" mouse up
```

Release the mouse if a failed sequence stops after `mouse down`.
Keep the pointer still during typing and reading. Avoid decorative movement.

## Typing

Click the field, then wait approximately 200–260 ms before typing.
Use `type <selector> <text> --delay <ms>`. This option works in 0.38.1 although its short help omits it.
Use short groups with delays of approximately 85–150 ms per character.
Add occasional 65–155 ms pauses between meaningful groups. Do not add a pause after every group.
Do not use `fill` or insert the whole value at once in a video that demonstrates typing.

```sh
agent-browser --session "$BROWSER_SESSION" type "$FIELD" demo --delay 105
agent-browser --session "$BROWSER_SESSION" wait 100
agent-browser --session "$BROWSER_SESSION" type "$FIELD" @example.com --delay 135
```

These commands contain public example text. Do not pass real secrets through command arguments.

## Transitions and results

After typing, allow approximately 350–420 ms before moving to the submit button.
Wait for the next visible control or exact destination path. Then allow approximately 300–500 ms for reading.
Use an exact pathname check when a hostname could also match the route text.
Preserve actual application loading time. Do not replace readiness checks with fixed sleeps.
Hold the successful result for about two seconds.

Prepare the sequence before recording to avoid gaps caused by agent decisions.
Use current selectors for new screens. Do not reuse references from a previous document.
For scrolling, use short wheel movements and inspect the resulting motion.

## Review

Check the complete recording. Require readable typing, continuous pointer motion, brief pauses, and a clear final result.
Do not add fake typing errors or unrelated movement to simulate a user.
Keep the original capture. Report any playback-review limitation.

## Sharpness check

For each capture setting, inspect a small sidebar icon and its label.
Also inspect a thin colored indicator and small text beside a border.
Choose equivalent visible details when the page has no such elements. Record their locations in separate visual review notes.
Wait for fonts, relevant images, and transitions. Keep the pointer outside these detail areas.

For video, include a stable screen for about two seconds. Save a direct viewport PNG of the same state.
Extract a frame after the first screen update and another from the final stable interval.
Do not use only the initial frame. A recorder can start sharply and lose detail in later frames.
Replace `FRAME_TIME` with each selected timestamp in seconds. Use a different output filename for each frame.

```sh
REVIEW_DIR="${VERIFY_DIR}-review"
mkdir -p "$REVIEW_DIR"
ffmpeg -v error -i "$VERIFY_DIR/interaction.mp4" -ss "$FRAME_TIME" -frames:v 1 "$REVIEW_DIR/comparison-frame.png"
```

Compare the direct PNG and extracted frame at original pixel dimensions and at the intended display size.
Check for missing strokes, blurred text edges, color spread, compression blocks, and halos.
Use the original files or unscaled detail crops. Do not use enlarged images or contact-sheet cells to establish sharpness.
Do not compare different page states, moving controls, or a frame during scrolling.

Mark screenshot and video sharpness separately as `pass`, `fail`, or `not checked`, with a short reason.
Pass only when the selected details remain clear at the intended display size, without material capture defects.
A sharp PNG does not establish video sharpness. Report remaining compression loss even when resolution checks pass.
If the direct PNG is also unclear, compare the browser rendering before assigning the cause to recording.

For a separate capture diagnostic, compare the same page at device scale factors 1 and 2.
Keep diagnostic media outside the managed evidence directory. Do not change the managed capture settings.
Keep the CSS viewport, browser zoom, and page state unchanged. Check actual screenshot and video dimensions.
Check pointer targeting, successful decoding, and motion at both settings. Record any playback-review limitation.
Use integer coordinates when the installed mouse command requires them. Recheck the target bounds after layout changes.
Do not lower capture resolution silently when recording fails or motion becomes uneven.
