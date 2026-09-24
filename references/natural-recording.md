# Record and review video

For video tasks, use these agent-browser commands or supported equivalents.
For touch, show taps and scrolling without a pointer. Adjust timings to the interaction.

## Interaction

Prepare the sequence. Place the pointer near the first control; allow about 650 ms for initial reading.
Get bounds with `get box <selector> --json`. Recompute after layout changes; use integer coordinates where required.
Target the control interior or input text area.

```sh
agent-browser --session "$BROWSER_SESSION" mouse move "$TARGET_X" "$TARGET_Y" --human --duration 450 --seed 17
agent-browser --session "$BROWSER_SESSION" wait 135
agent-browser --session "$BROWSER_SESSION" mouse down
agent-browser --session "$BROWSER_SESSION" wait 75
agent-browser --session "$BROWSER_SESSION" mouse up
```

Release held buttons after failure. Keep the pointer still during typing and reading.
After focusing a field, allow about 200–260 ms before typing. Use short groups with 85–150 ms character delays.
The `type --delay` option works in 0.38.1 despite its omission from short help.

```sh
agent-browser --session "$BROWSER_SESSION" type "$FIELD" demo --delay 105
agent-browser --session "$BROWSER_SESSION" wait 100
agent-browser --session "$BROWSER_SESSION" type "$FIELD" @example.com --delay 135
```

Do not pass secrets in command arguments. Do not use `fill` for a demonstration of typing.
Avoid artificial errors, decorative movement, and pauses after every group.
Allow about 350–420 ms before moving to submit. Wait for the next control or exact pathname, then allow reading time.
Fixed sleeps do not replace readiness checks. Preserve real loading time and refresh selectors after document changes.
Use short wheel movements for scrolling. Hold the final result for about two seconds.
Stop on unexpected behavior and inspect it outside the take. Never repeat consequential actions for a better recording.

## Review

Review the complete video at normal speed. Check typing, pointer visibility and motion, transitions, scrolling, and the final result.
A 60 fps file can repeat frames. Judge cadence during movement; static holds are normal.
Record available playback completion, errors, and `getVideoPlaybackQuality()` counts.
Report unavailable playback checks; statistics cannot replace visual review.

For sharpness, select small text, thin icons, and a colored edge or border. Record their locations in review notes.
Wait for fonts, images, and transitions. Keep the pointer outside these details.
Save a managed viewport PNG and include a stable video interval of the same state.
Extract one frame after the first update and another from the final stable interval. The initial frame alone is insufficient.

```sh
REVIEW_DIR="${VERIFY_DIR}-review"
mkdir -p "$REVIEW_DIR"
ffmpeg -v error -i "$VERIFY_DIR/interaction.mp4" -ss "$FRAME_TIME" -frames:v 1 "$REVIEW_DIR/comparison-frame.png"
```

Set `FRAME_TIME` in seconds and use a different filename for each frame. Extract frames after capture, outside the managed directory.
Compare matching stable states at original dimensions and intended display size. Use original files or unscaled detail crops.
Do not use enlarged images or contact sheets as sharpness proof. Check missing strokes, blurred edges, color spread, blocks, and halos.
Mark screenshot and video sharpness separately: `pass`, `fail`, or `not checked`, with a reason.
A pass requires clear details without material capture defects. Report compression loss even when dimensions pass.
If the PNG is unclear too, inspect browser rendering before attributing the problem to recording.

For a separate diagnostic, compare device scales 1 and 2 with identical CSS viewport, zoom, and page state.
Keep diagnostic files outside managed evidence. Check actual dimensions, decoding, pointer targeting, and motion.
Preserve original media. Do not change managed settings or silently lower resolution after failure.

## Demo recording

The evidence recording stays continuous. It proves the action then the result, including the wait
between them. Do not shorten that file by cutting still frames. On a full-resolution capture, a
pointer move changes too few pixels to count as motion, so a freeze cut removes the gesture and
the join looks like a jump.

For a watchable demo, leave the recorder stopped while choosing the next action. Start it when the
gesture begins. Keep the whole pointer path. Stop after the result has been readable for about 0.6 s.

```sh
DEMO_DIR="${VERIFY_DIR}-demo"
mkdir -p "$DEMO_DIR/takes"
agent-browser --session "$BROWSER_SESSION" record start "$DEMO_DIR/takes/01.mp4" --fps 60 --cursor
# Perform one prepared gesture, then hold the result briefly.
agent-browser --session "$BROWSER_SESSION" record stop
# Choose the next action here. The recorder is stopped, so this wait is not in the demo.
agent-browser --session "$BROWSER_SESSION" record start "$DEMO_DIR/takes/02.mp4" --fps 60 --cursor
# Perform the next gesture and hold its result.
agent-browser --session "$BROWSER_SESSION" record stop
python3 scripts/demo_join.py "$DEMO_DIR/takes/01.mp4" "$DEMO_DIR/takes/02.mp4" -o "$DEMO_DIR/demo.mp4"
```

The join only places the takes in order. It does not trim frames or re-encode them.
Write the demo outside the capture folder. The script refuses to write inside a directory that
contains `capture.json`. The demo is not evidence. `check` only validates the original recording.
