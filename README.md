# Real-Time Color Detection

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV 4.x](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/crisdanrodriguez/realtime-color-detection/workflows/Tests/badge.svg)](https://github.com/crisdanrodriguez/realtime-color-detection/actions/workflows/tests.yml)

A polished OpenCV project for detecting colors in real time with a webcam using the HSV color space. Perfect for computer vision prototyping, HSV calibration, and educational purposes.

## Table of Contents

- [Preview](#preview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Command-Line Options](#command-line-options)
- [Controls](#controls)
- [Notes About HSV](#notes-about-hsv)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Preview

![Application demo](assets/demo.png)

This tool is useful for:

- Calibrating HSV ranges for computer vision projects
- Experimenting with masks and thresholding in real time
- Building quick prototypes for object or color-based tracking
- Educational demonstrations of computer vision concepts

## Features

- **Live webcam capture** with optional resolution settings
- **Interactive HSV controls** with OpenCV trackbars
- **Full-range HSV startup** so the feed is visible before calibration
- **Three simultaneous views**: original feed, binary mask, and filtered result
- **Optional blur and mask cleanup** for more stable detection
- **On-screen overlay** with current HSV values and mask coverage
- **Reset shortcut** for quickly returning to the initial color range
- **Cross-platform support** (Windows, macOS, Linux)
- **Camera backend selection** for better compatibility

## Project Structure

```
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── pull_request_template.md
│   └── workflows/
│       └── tests.yml
├── assets/
│   └── demo.png
├── realtime_color_detection/
│   ├── __init__.py
│   └── __main__.py
├── test_basic.py
├── .editorconfig
├── .gitattributes
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
├── realtime_color_detection.py
└── requirements.txt
```

## Requirements

- Python 3.10 or higher
- A working webcam
- Dependencies: NumPy, OpenCV

## Installation

Make sure you run the following commands from the project root, the same directory that contains `pyproject.toml`.

### Recommended Installation

```bash
cd realtime-color-detection
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install .
```

### Development Installation

```bash
cd realtime-color-detection
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Alternative Installation

```bash
cd realtime-color-detection
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run the application with the default webcam:

```bash
realtime-color-detection
```

The app starts with the full HSV range enabled, so the filtered result should look like the original feed until you narrow the sliders.

### Example with Custom Settings

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

### Alternative Ways to Run

As a script:

```bash
python3 realtime_color_detection.py
```

As a module:

```bash
python3 -m realtime_color_detection
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--camera` | Camera index used by OpenCV | 0 |
| `--width` | Requested capture width in pixels | None |
| `--height` | Requested capture height in pixels | None |
| `--backend` | Preferred OpenCV camera backend (`auto`, `any`, `avfoundation`) | auto |
| `--lower-hsv` | Initial lower HSV bound (format: H,S,V) | 0,0,0 |
| `--upper-hsv` | Initial upper HSV bound (format: H,S,V) | 179,255,255 |
| `--blur-kernel` | Gaussian blur kernel size before masking | 5 |
| `--morph-kernel` | Morphological cleanup kernel size for the mask | 5 |
| `--no-mirror` | Disable horizontal mirroring of the webcam feed | False |

## Controls

- **`q`**: Quit the application
- **`r`**: Reset the trackbars to the initial HSV values

## Notes About HSV in OpenCV

OpenCV uses the following HSV ranges:

- **Hue**: `0-179` (not 0-360 like some other systems)
- **Saturation**: `0-255`
- **Value**: `0-255`

### Tips for Better Detection

If your mask is not detecting the target color correctly:

- Gradually increase the upper range
- Lower the minimum saturation/value if the object is dull or poorly lit
- Adjust lighting conditions to reduce reflections and noise
- Use the blur kernel to reduce noise in the mask
- Apply morphological operations for cleaner masks

## Troubleshooting

### ModuleNotFoundError After Installation

If `pip install -e .` succeeds but `realtime-color-detection` fails with `ModuleNotFoundError`, your virtual environment may not be resolving editable installs correctly. Use standard installation instead:

```bash
pip install .
```

### Camera Issues

- **Black frames**: Check camera permissions in your OS settings
- **Camera not found**: Try different camera indices (`--camera 1`, `--camera 2`)
- **Backend issues**: Try `--backend any` or `--backend avfoundation` (on macOS)

### Permission Issues on macOS

Ensure camera permissions are granted in System Settings > Privacy & Security > Camera.

## Development

### Running Tests

```bash
pip install pytest
pytest test_basic.py -v
```

### Building the Package

```bash
python -m build
```

### Code Quality

This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

### AI-Enhanced Development

This repository was significantly improved and documented using AI assistance. GitHub Copilot and similar AI tools were used to:
- Generate comprehensive unit tests and CI/CD pipelines
- Create professional documentation and README structure
- Implement best practices for Python packaging and project organization
- Add configuration files for consistent code formatting and Git attributes
- Develop GitHub templates for issues and pull requests

AI tools helped accelerate the professionalization process while ensuring adherence to modern development standards and community best practices.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
