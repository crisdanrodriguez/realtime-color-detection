"""Real-time HSV color detection using a webcam feed.

This utility opens a live camera stream, exposes HSV controls via OpenCV
trackbars, and shows the original frame, the generated mask, and the filtered
result. It is intended as a small but reusable computer-vision demo that can
also serve as a quick color calibration tool.
"""

from __future__ import annotations

import argparse
import platform
import sys
from dataclasses import dataclass

try:
    import cv2
except ModuleNotFoundError:
    cv2 = None

try:
    import numpy as np
except ModuleNotFoundError:
    np = None

TRACKBAR_WINDOW = "HSV Controls"
FRAME_WINDOW = "Original Feed"
MASK_WINDOW = "Mask"
RESULT_WINDOW = "Filtered Result"
CONTROL_PANEL_WIDTH = 520
CONTROL_PANEL_HEIGHT = 180

HUE_MAX = 179
SATURATION_MAX = 255
VALUE_MAX = 255

DEFAULT_LOWER = (0, 0, 0)
DEFAULT_UPPER = (HUE_MAX, SATURATION_MAX, VALUE_MAX)


@dataclass(slots=True)
class HSVRange:
    """Container for HSV lower and upper bounds."""

    lower: tuple[int, int, int]
    upper: tuple[int, int, int]

    def normalized(self) -> "HSVRange":
        """Clamp values to valid HSV limits and keep lower <= upper."""
        clamped_lower = (
            max(0, min(self.lower[0], HUE_MAX)),
            max(0, min(self.lower[1], SATURATION_MAX)),
            max(0, min(self.lower[2], VALUE_MAX)),
        )
        clamped_upper = (
            max(0, min(self.upper[0], HUE_MAX)),
            max(0, min(self.upper[1], SATURATION_MAX)),
            max(0, min(self.upper[2], VALUE_MAX)),
        )

        return HSVRange(
            lower=tuple(min(low, high) for low, high in zip(clamped_lower, clamped_upper)),
            upper=tuple(max(low, high) for low, high in zip(clamped_lower, clamped_upper)),
        )

    def lower_array(self) -> np.ndarray:
        return np.array(self.lower, dtype=np.uint8)

    def upper_array(self) -> np.ndarray:
        return np.array(self.upper, dtype=np.uint8)


def noop(_: int) -> None:
    """Trackbar callback placeholder required by OpenCV."""


def ensure_runtime_dependencies() -> None:
    """Fail with a friendly message when required packages are missing."""
    missing_packages: list[str] = []
    if cv2 is None:
        missing_packages.append("opencv-python")
    if np is None:
        missing_packages.append("numpy")

    if missing_packages:
        package_list = ", ".join(missing_packages)
        raise RuntimeError(
            "Missing required dependencies: "
            f"{package_list}. Install them with `pip install -r requirements.txt`."
        )


def parse_hsv_triplet(value: str) -> tuple[int, int, int]:
    """Parse a comma-separated HSV triplet from the command line."""
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("HSV values must use the format H,S,V.")

    try:
        triplet = tuple(int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("HSV values must be integers.") from exc

    limits = (HUE_MAX, SATURATION_MAX, VALUE_MAX)
    for component, maximum in zip(triplet, limits):
        if component < 0 or component > maximum:
            raise argparse.ArgumentTypeError(
                f"HSV values must be within 0-{HUE_MAX}, 0-{SATURATION_MAX}, 0-{VALUE_MAX}."
            )

    return triplet


def ensure_odd(value: int) -> int:
    """Return the nearest valid odd kernel size accepted by OpenCV filters."""
    if value <= 1:
        return 1
    return value if value % 2 == 1 else value + 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="realtime-color-detection",
        description="Detect a color range in real time using HSV controls and a webcam feed."
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera index used by OpenCV. Default: 0.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Requested capture width in pixels.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Requested capture height in pixels.",
    )
    parser.add_argument(
        "--lower-hsv",
        type=parse_hsv_triplet,
        default=DEFAULT_LOWER,
        metavar="H,S,V",
        help="Initial lower HSV bound. Default: 0,0,0.",
    )
    parser.add_argument(
        "--upper-hsv",
        type=parse_hsv_triplet,
        default=DEFAULT_UPPER,
        metavar="H,S,V",
        help="Initial upper HSV bound. Default: 179,255,255.",
    )
    parser.add_argument(
        "--blur-kernel",
        type=int,
        default=5,
        help="Gaussian blur kernel used before masking. Values <= 1 disable blur. Default: 5.",
    )
    parser.add_argument(
        "--morph-kernel",
        type=int,
        default=5,
        help="Morphological cleanup kernel for the mask. Values <= 1 disable cleanup. Default: 5.",
    )
    parser.add_argument(
        "--no-mirror",
        action="store_true",
        help="Disable horizontal mirroring of the webcam feed.",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "any", "avfoundation"),
        default="auto",
        help="Preferred OpenCV camera backend. Default: auto.",
    )
    return parser


def resolve_backends(backend_name: str) -> list[tuple[int, str]]:
    """Return the candidate OpenCV backends to try for this platform."""
    if backend_name == "avfoundation":
        return [(cv2.CAP_AVFOUNDATION, "AVFoundation")]
    if backend_name == "any":
        return [(cv2.CAP_ANY, "Default")]

    candidates: list[tuple[int, str]] = []
    if platform.system() == "Darwin" and hasattr(cv2, "CAP_AVFOUNDATION"):
        candidates.append((cv2.CAP_AVFOUNDATION, "AVFoundation"))
    candidates.append((cv2.CAP_ANY, "Default"))
    return candidates


def camera_delivers_frames(camera: cv2.VideoCapture, attempts: int = 20) -> bool:
    """Warm up the camera and confirm that at least one frame arrives."""
    for _ in range(attempts):
        success, frame = camera.read()
        if success and frame is not None and frame.size > 0:
            return True
    return False


def open_camera(
    camera_index: int,
    width: int | None,
    height: int | None,
    backend_name: str,
) -> tuple[cv2.VideoCapture, str]:
    for backend_id, backend_label in resolve_backends(backend_name):
        camera = cv2.VideoCapture(camera_index, backend_id)
        if not camera.isOpened():
            camera.release()
            continue

        if width is not None:
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if camera_delivers_frames(camera):
            return camera, backend_label

        camera.release()

    raise RuntimeError(
        f"Unable to read frames from camera index {camera_index}. "
        "On macOS, also confirm camera permissions in System Settings > "
        "Privacy & Security > Camera and try `--camera 1` or `--backend any`."
    )


def create_trackbars(bounds: HSVRange) -> None:
    cv2.namedWindow(TRACKBAR_WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(TRACKBAR_WINDOW, CONTROL_PANEL_WIDTH, CONTROL_PANEL_HEIGHT)
    cv2.createTrackbar("Low H", TRACKBAR_WINDOW, bounds.lower[0], HUE_MAX, noop)
    cv2.createTrackbar("High H", TRACKBAR_WINDOW, bounds.upper[0], HUE_MAX, noop)
    cv2.createTrackbar("Low S", TRACKBAR_WINDOW, bounds.lower[1], SATURATION_MAX, noop)
    cv2.createTrackbar("High S", TRACKBAR_WINDOW, bounds.upper[1], SATURATION_MAX, noop)
    cv2.createTrackbar("Low V", TRACKBAR_WINDOW, bounds.lower[2], VALUE_MAX, noop)
    cv2.createTrackbar("High V", TRACKBAR_WINDOW, bounds.upper[2], VALUE_MAX, noop)


def render_control_panel(bounds: HSVRange, backend_label: str) -> np.ndarray:
    """Render a visible panel so the trackbar window reliably appears."""
    panel = np.full((CONTROL_PANEL_HEIGHT, CONTROL_PANEL_WIDTH, 3), 245, dtype=np.uint8)
    info_lines = (
        "Adjust the HSV sliders below to isolate a target color.",
        f"Current lower: {bounds.lower}",
        f"Current upper: {bounds.upper}",
        f"Camera backend: {backend_label}",
    )

    for index, text in enumerate(info_lines):
        y_position = 28 + index * 24
        cv2.putText(
            panel,
            text,
            (12, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (35, 35, 35),
            1,
            cv2.LINE_AA,
        )

    return panel


def set_trackbars(bounds: HSVRange) -> None:
    cv2.setTrackbarPos("Low H", TRACKBAR_WINDOW, bounds.lower[0])
    cv2.setTrackbarPos("High H", TRACKBAR_WINDOW, bounds.upper[0])
    cv2.setTrackbarPos("Low S", TRACKBAR_WINDOW, bounds.lower[1])
    cv2.setTrackbarPos("High S", TRACKBAR_WINDOW, bounds.upper[1])
    cv2.setTrackbarPos("Low V", TRACKBAR_WINDOW, bounds.lower[2])
    cv2.setTrackbarPos("High V", TRACKBAR_WINDOW, bounds.upper[2])


def read_trackbars() -> HSVRange:
    bounds = HSVRange(
        lower=(
            cv2.getTrackbarPos("Low H", TRACKBAR_WINDOW),
            cv2.getTrackbarPos("Low S", TRACKBAR_WINDOW),
            cv2.getTrackbarPos("Low V", TRACKBAR_WINDOW),
        ),
        upper=(
            cv2.getTrackbarPos("High H", TRACKBAR_WINDOW),
            cv2.getTrackbarPos("High S", TRACKBAR_WINDOW),
            cv2.getTrackbarPos("High V", TRACKBAR_WINDOW),
        ),
    ).normalized()

    set_trackbars(bounds)
    return bounds


def preprocess_frame(frame: np.ndarray, blur_kernel: int) -> np.ndarray:
    if blur_kernel <= 1:
        return frame
    return cv2.GaussianBlur(frame, (blur_kernel, blur_kernel), 0)


def build_mask(hsv_frame: np.ndarray, bounds: HSVRange, morph_kernel: int) -> np.ndarray:
    mask = cv2.inRange(hsv_frame, bounds.lower_array(), bounds.upper_array())
    if morph_kernel <= 1:
        return mask

    kernel = np.ones((morph_kernel, morph_kernel), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)


def frame_looks_black(frame: np.ndarray) -> bool:
    """Heuristic for detecting frames that are almost entirely black."""
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(grayscale.mean()) < 8.0 and float(grayscale.std()) < 8.0


def add_overlay(
    frame: np.ndarray,
    bounds: HSVRange,
    mask: np.ndarray,
    backend_label: str,
    black_frame_warning: bool,
) -> np.ndarray:
    coverage = float(np.count_nonzero(mask)) / mask.size * 100
    overlay_lines = (
        f"Lower HSV: {bounds.lower}",
        f"Upper HSV: {bounds.upper}",
        f"Mask coverage: {coverage:.2f}%",
        f"Camera backend: {backend_label}",
        "Keys: q=quit | r=reset full range",
    )

    annotated = frame.copy()
    for index, text in enumerate(overlay_lines):
        y_position = 28 + index * 28
        cv2.putText(
            annotated,
            text,
            (12, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated,
            text,
            (12, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (20, 20, 20),
            1,
            cv2.LINE_AA,
        )

    if black_frame_warning:
        warning_lines = (
            "Camera feed looks black.",
            "Check camera permissions or try --camera 1 / --backend any.",
        )
        for index, text in enumerate(warning_lines):
            y_position = frame.shape[0] - 36 - index * 24
            cv2.putText(
                annotated,
                text,
                (12, y_position),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
    return annotated


def run_detection(args: argparse.Namespace) -> int:
    ensure_runtime_dependencies()
    initial_bounds = HSVRange(args.lower_hsv, args.upper_hsv).normalized()
    blur_kernel = ensure_odd(args.blur_kernel)
    morph_kernel = ensure_odd(args.morph_kernel)
    camera, backend_label = open_camera(args.camera, args.width, args.height, args.backend)

    create_trackbars(initial_bounds)
    black_frame_streak = 0
    warned_black_frames = False

    try:
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                print(
                    "Camera frame could not be read. "
                    "Try reconnecting the camera or using a different index.",
                    file=sys.stderr,
                )
                return 1

            if not args.no_mirror:
                frame = cv2.flip(frame, 1)

            if frame_looks_black(frame):
                black_frame_streak += 1
            else:
                black_frame_streak = 0

            bounds = read_trackbars()
            processed_frame = preprocess_frame(frame, blur_kernel)
            hsv_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2HSV)
            mask = build_mask(hsv_frame, bounds, morph_kernel)
            result = cv2.bitwise_and(frame, frame, mask=mask)
            show_black_warning = black_frame_streak >= 10
            if show_black_warning and not warned_black_frames:
                print(
                    "The camera is returning very dark frames. "
                    "Check camera permissions and try `--camera 1` or `--backend any`.",
                    file=sys.stderr,
                )
                warned_black_frames = True
            annotated_frame = add_overlay(
                frame,
                bounds,
                mask,
                backend_label,
                show_black_warning,
            )

            cv2.imshow(TRACKBAR_WINDOW, render_control_panel(bounds, backend_label))
            cv2.imshow(FRAME_WINDOW, annotated_frame)
            cv2.imshow(MASK_WINDOW, mask)
            cv2.imshow(RESULT_WINDOW, result)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("r"):
                set_trackbars(initial_bounds)
    finally:
        camera.release()
        cv2.destroyAllWindows()

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run_detection(args)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
