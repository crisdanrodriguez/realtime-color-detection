# Real-Time Color Detection

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

A polished OpenCV project for detecting colors in real time with a webcam using the HSV color space.

## Preview

![Application demo](assets/demo.png)

This tool is useful for:

- Calibrating HSV ranges for computer vision projects
- Experimenting with masks and thresholding in real time
- Building quick prototypes for object or color-based tracking

## Features

- Live webcam capture with optional resolution settings
- Interactive HSV controls with OpenCV trackbars
- Full-range HSV startup so the feed is visible before calibration
- Three simultaneous views: original feed, binary mask, and filtered result
- Optional blur and mask cleanup for more stable detection
- On-screen overlay with current HSV values and mask coverage
- Reset shortcut for quickly returning to the initial color range

## Project Structure

```text
.
├── assets/
├── LICENSE
├── pyproject.toml
├── realtime_color_detection/
├── realtime_color_detection.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- A working webcam

## Installation

Make sure you run the following commands from the project root, the same directory that contains `pyproject.toml`.

Recommended installation:

```bash
cd realtime-color-detection
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

Development installation:

```bash
cd realtime-color-detection
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Alternative installation with `requirements.txt`:

```bash
cd realtime-color-detection
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run the application with the default webcam:

```bash
realtime-color-detection
```

The app now starts with the full HSV range enabled, so the filtered result should look like the original feed until you narrow the sliders.

Example with custom settings:

```bash
realtime-color-detection \
  --camera 0 \
  --backend auto \
  --width 1280 \
  --height 720 \
  --lower-hsv 35,80,80 \
  --upper-hsv 85,255,255 \
  --blur-kernel 5 \
  --morph-kernel 5
```

You can still run it directly as a script if you prefer:

```bash
python3 realtime_color_detection.py
```

Or as a module from the project root:

```bash
python3 -m realtime_color_detection
```

## Command-Line Options

| Option | Description |
| --- | --- |
| `--camera` | Camera index used by OpenCV. |
| `--width` | Requested capture width. |
| `--height` | Requested capture height. |
| `--backend` | Camera backend: `auto`, `any`, or `avfoundation`. |
| `--lower-hsv` | Initial lower HSV value in `H,S,V` format. |
| `--upper-hsv` | Initial upper HSV value in `H,S,V` format. |
| `--blur-kernel` | Gaussian blur kernel size before masking. |
| `--morph-kernel` | Morphological cleanup kernel size for the mask. |
| `--no-mirror` | Disables horizontal mirroring of the camera feed. |

## Controls

- `q`: quit the application
- `r`: reset the trackbars to the initial HSV values

## Notes About HSV in OpenCV

OpenCV uses the following HSV ranges:

- Hue: `0-179`
- Saturation: `0-255`
- Value: `0-255`

If your mask is not detecting the target color correctly:

- Increase the upper range gradually
- Lower the minimum saturation/value if the object is dull or poorly lit
- Adjust lighting conditions to reduce reflections and noise

## Troubleshooting

If `pip install -e .` succeeds but the command `realtime-color-detection` fails with `ModuleNotFoundError`, your virtual environment may not be resolving editable installs correctly. In that case, use a standard installation instead:

```bash
pip install .
```

If the application opens but the camera looks completely black:

- Confirm macOS camera permission in `System Settings > Privacy & Security > Camera`
- Close Zoom, Meet, Photo Booth, or any other app that may be using the webcam
- Try another camera index, for example `realtime-color-detection --camera 1`
- Try another backend, for example `realtime-color-detection --backend any`
- Press `r` to reset the HSV range if you moved the sliders into a range that hides everything

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
