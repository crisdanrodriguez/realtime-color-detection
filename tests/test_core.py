"""Regression tests for the public Python API."""

import argparse

import pytest

from realtime_color_detection import (
    DEFAULT_LOWER,
    DEFAULT_UPPER,
    HSVRange,
    build_parser,
    ensure_odd,
    parse_hsv_triplet,
)


def test_hsv_range_normalized_orders_and_clamps_values() -> None:
    hsv = HSVRange(lower=(200, 300, 300), upper=(100, 200, 200))

    normalized = hsv.normalized()

    assert normalized.lower == (100, 200, 200)
    assert normalized.upper == (179, 255, 255)


def test_hsv_range_arrays_match_expected_values() -> None:
    hsv = HSVRange(lower=(10, 20, 30), upper=(40, 50, 60))

    assert hsv.lower_array().tolist() == [10, 20, 30]
    assert hsv.upper_array().tolist() == [40, 50, 60]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, 1),
        (2, 3),
        (4, 5),
        (5, 5),
    ],
)
def test_ensure_odd_returns_valid_kernel_sizes(value: int, expected: int) -> None:
    assert ensure_odd(value) == expected


def test_parse_hsv_triplet_accepts_valid_values() -> None:
    assert parse_hsv_triplet("10,20,30") == (10, 20, 30)


@pytest.mark.parametrize("value", ["10,20", "180,20,30", "10,a,30"])
def test_parse_hsv_triplet_rejects_invalid_values(value: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        parse_hsv_triplet(value)


def test_parser_defaults_match_expected_runtime_defaults() -> None:
    parser = build_parser()

    args = parser.parse_args([])

    assert args.lower_hsv == DEFAULT_LOWER
    assert args.upper_hsv == DEFAULT_UPPER
    assert args.camera == 0
    assert args.backend == "auto"
