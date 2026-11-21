# readscroll

Headless, privacy-first, hands-free scrolling for Linux (KDE Plasma Wayland and
X11 alike) using a webcam, MediaPipe Hand Landmarker, and a kernel-level
`uinput` virtual mouse. Hold your hand above or below its resting anchor to
scroll smoothly — like a trackpad — with tiny finger movements from a reclined
chair.

## Features

- **No GUI, no disk writes, no network after first run.** Frames are 320×240 @
  30 FPS in volatile RAM only. The MediaPipe model is downloaded once on first
  run and then cached locally.
- **Smooth hi-res scrolling.** A dedicated 120 Hz thread eases target velocity
  and emits fractional `REL_WHEEL_HI_RES` deltas (one legacy `REL_WHEEL` notch
  per 120 units), so scrolling glides instead of stepping.
- **Wayland-native.** Scroll events come from a real kernel virtual mouse
  (`/dev/uinput`), which libinput/KWin treats exactly like physical hardware —
  works in Brave, Zathura, Konsole, and everywhere else.
- **Forgiving gestures.** Deadzone, EMA-smoothed tracking, dynamic anchor,
  auto re-anchor while resting, and a directional return guard that blocks
  only the opposite direction on your way back — same-direction waves work
  instantly, with no pause required.
- **Clean exits.** Ctrl+C / SIGTERM / 5-minute no-hand idle timeout all release
  the webcam (LED off) and remove the virtual mouse.

## Requirements

- Linux with `/dev/uinput` (works as a normal user on Fedora; no root — the
  script refuses to run as root).
- A webcam at `/dev/video0`.
- **Python 3.12** — MediaPipe does not support Python 3.15 yet.
- `python3.12-devel` (Fedora: `sudo dnf install -y python3.12-devel`) — the
  `evdev` package has no prebuilt Linux wheels and must compile a small C
  extension.

## Install

```bash
git clone <your-repo-url>
cd readscroll
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Optionally add an alias to `~/.bashrc`:

```bash
alias readscroll='~/path/to/readscroll/.venv/bin/python ~/path/to/readscroll/readscroll.py'
```

## Usage

```bash
readscroll                       # normal mode
readscroll --calibrate            # live anchor / y / offset / target speed, no scrolling
readscroll --deadzone 0.05        # require a larger hand excursion before scrolling
readscroll --return-guard 300     # longer return-direction suppression (ms)
readscroll --max-speed 3000       # faster top speed (hi-res units/sec; 120 = 1 notch)
readscroll --smoothing 0.3        # steadier tracking (1.0 disables smoothing)
readscroll --point palm           # track wrist/knuckle instead of fingertips
readscroll --idle-timeout 600     # auto-exit after 10 min with no hand
```

### Gestures

1. Put your hand in frame. It takes ~200 ms to arm (so raising your hand
   doesn't scroll). Your entry position becomes the anchor.
2. Move your hand **below** the anchor + deadzone → scroll **down**; **above**
   it → scroll **up**. Distance past the deadzone sets the speed: ~150 u/s at
   the edge up to `--max-speed` at full deflection. No fast swipes needed.
3. To stop, return your hand to within the deadzone (or lower it out of frame).
   Only the opposite (return) direction is briefly suppressed until your hand
   settles in the deadzone for `--return-guard` ms (default 200). Same-direction
   waves work instantly — no pause or extra hand rotation needed.
4. Hold still in the inner half of the deadzone for ~1.2 s to re-anchor if your
   posture drifts. Taking your hand out of frame and back in also re-anchors.

## Layout

```
readscroll.py            thin launcher (keeps the `readscroll` alias working)
readscroll_lib/
  config.py              constants + smoothstep speed curve
  cli.py                 CLI flags
  model.py               one-time model download
  camera.py              V4L2 capture (320x240 @ 30 FPS, 1-frame buffer)
  tracker.py             MediaPipe HandLandmarker wrapper
  injector.py            uinput virtual mouse + hi-res wheel events
  scroller.py            120 Hz easing/accumulator thread
  app.py                 main loop, signal handling, shutdown
```

The `hand_landmarker.task` model is **not** committed (it is fetched from
Google's official URL on first run).

## Troubleshooting

- **`Cannot open /dev/video0`** — another app (Brave, OBS, another readscroll
  instance) holds the webcam. Close it and retry.
- **No scrolling in an app** — some apps ignore synthetic input? Verify the
  virtual device exists with `cat /proc/bus/input/devices | grep -A4 readscroll`;
  it should show handlers like `mouse3 event19`. If permission errors occur on
  your distro, add your user to the `input` group or install the appropriate
  udev rule for `/dev/uinput`.
- **Too sensitive / not sensitive enough** — tune `--deadzone` and `--smoothing`;
  `--calibrate` shows exactly where your offsets land.
