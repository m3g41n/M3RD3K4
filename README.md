# M3RD3K4 - THE AWAKENING OF MINDS

A cinematic, fully animated ASCII experience for the terminal (~3 minutes, 9 scenes).

## Run
```
pip install -r requirements.txt     # Pillow + NumPy
python main.py
```
Windows Terminal / PowerShell, macOS and Linux terminals work. Use a window of at least 60x20
(110x36 or larger looks best).

**Keys:** `Space` / `Enter` / `->` skip to next scene - `q` / `Esc` / `Ctrl+C` quit.
The last screen stays until you press a key.

Options: `--fps 20  --speed 0.8  --duration-scale 1.5  --reduced-motion  --no-color
--no-glitch  --scene 7  --seed 42`. Permanent defaults live in `core/config.py`.

## Structure
```
main.py                  entry point / CLI
core/    config, engine (frame loop, fades, resize), renderer (Canvas + ANSI diff),
         terminal (alt screen, keys, guaranteed restore), transitions, context
animations/  digital_rain, ascii_wave, ascii_fire, particles, fractal,
             three_fingers (hand poses), anonymous_masks, glitch
scenes/  scene_01 ... scene_09
utils/   image_to_ascii, color, timing, text (big letters, wrapping)
assets/  three_fingers/three_fingers.jpg   anonymous_masks/masks.jpg
tools/preview.py         render any scene/time to a PNG (no terminal needed)
tests/smoke_test.py      headless test: all scenes, 3 sizes, motion + pose checks
```

## How the supplied images become animation
A still image has no motion data, so poses are built by *warping the real image data* each
frame and re-sampling it into characters:
- **Hand:** ink + filled silhouette extracted from the JPG. Each of the three raised fingers
  is shortened/lengthened independently, fingers sway about the palm, the thumb flexes,
  and the whole hand breathes. Poses are interpolated with easing.
- **Masks:** the two masks are separated by connected-component analysis, then each gets
  its own drift, tilt, eye squash/blink and mouth open/widen, plus a dissolve reveal.
Replace the images in `assets/` to use other art (the hand/mask feature coordinates in
`animations/` are tuned to the supplied images). Missing/corrupt files fall back to a simple
placeholder and print a warning.

## Notes
- Scene 08 text is shown exactly as specified. The small caption is set by
  `CONSTITUTION_LABEL` in `core/config.py` (set `""` to hide it).
- Scene 07 adds a quiet caption, "SOLIDARITY AND SHARED CONSEQUENCES", under the slogan.
