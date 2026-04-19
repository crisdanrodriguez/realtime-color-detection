"""Public package API for realtime-color-detection."""

from .app import (
    DEFAULT_LOWER,
    DEFAULT_UPPER,
    HSVRange,
    build_parser,
    ensure_odd,
    main,
    parse_hsv_triplet,
)

__all__ = [
    "DEFAULT_LOWER",
    "DEFAULT_UPPER",
    "HSVRange",
    "build_parser",
    "ensure_odd",
    "main",
    "parse_hsv_triplet",
]
