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

## Demo cut

The recording is continuous on purpose. It proves the action→result sequence. But the agent
thinks between tool calls, and that time is recorded too — one measured run had 43 s of video and
about 4.5 s of content.

For a demo, make a shorter copy:

```sh
python3 scripts/demo_cut.py "$VERIFY_DIR/interaction.mp4" -o "$DEMO_DIR/demo.mp4" --report
```

- Never change the original, and write the demo outside the capture folder. The script refuses to
  write inside it.
- The demo is not evidence. `check` only validates the original.
- Every still part is cut to `--keep` seconds (default 0.6), keeping its start, so the result on
  screen is still readable.
- Still parts shorter than `--min-freeze` (default 1.0 s) stay. They are normal reading pauses.

Check the cut against a fake video with known timings (15 s in, 7.8 s out):

```sh
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=navy:s=640x360:d=2:r=60" \
  -f lavfi -i "testsrc=s=640x360:d=3:r=60" \
  -f lavfi -i "color=c=navy:s=640x360:d=4:r=60" \
  -f lavfi -i "testsrc=s=640x360:d=3:r=60" \
  -f lavfi -i "color=c=navy:s=640x360:d=3:r=60" \
  -filter_complex "[0:v][1:v][2:v][3:v][4:v]concat=n=5:v=1:a=0[v]" -map "[v]" \
  -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p /tmp/synth.mp4
python3 scripts/demo_cut.py /tmp/synth.mp4 -o /tmp/synth-demo.mp4 --report
```
