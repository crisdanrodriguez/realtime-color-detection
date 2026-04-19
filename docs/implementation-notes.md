# Implementation Notes

## Purpose

This project provides a small OpenCV-based command-line application for tuning HSV thresholds against a live webcam feed.

## Runtime Flow

1. Parse CLI arguments for camera selection, optional resolution, HSV bounds, blur, and mask cleanup.
2. Open the webcam using the preferred backend for the current platform.
3. Render OpenCV trackbars for interactive HSV calibration.
4. Convert each frame to HSV, build a binary mask, and display:
   - Original feed with overlay
   - Mask
   - Filtered result

## Code Layout

- `realtime_color_detection/app.py`: core application, CLI parser, camera setup, frame processing, and UI.
- `realtime_color_detection/__main__.py`: module entry point for `python -m realtime_color_detection`.
- `tests/test_core.py`: lightweight regression tests for non-GUI behavior.

## Scope

The repository is intentionally minimal. It does not include model training, dataset handling, or object tracking pipelines.
