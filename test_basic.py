"""Basic tests for realtime-color-detection."""

import argparse
import pytest
from realtime_color_detection import HSVRange, ensure_odd, parse_hsv_triplet


class TestHSVRange:
    """Test HSVRange class."""

    def test_normalized(self):
        """Test normalization of HSV ranges."""
        hsv = HSVRange(lower=(200, 300, 300), upper=(100, 200, 200))
        normalized = hsv.normalized()
        assert normalized.lower == (100, 200, 200)
        assert normalized.upper == (179, 255, 255)

    def test_lower_array(self):
        """Test lower array conversion."""
        hsv = HSVRange(lower=(10, 20, 30), upper=(40, 50, 60))
        array = hsv.lower_array()
        assert array.tolist() == [10, 20, 30]

    def test_upper_array(self):
        """Test upper array conversion."""
        hsv = HSVRange(lower=(10, 20, 30), upper=(40, 50, 60))
        array = hsv.upper_array()
        assert array.tolist() == [40, 50, 60]


class TestUtilityFunctions:
    """Test utility functions."""

    def test_ensure_odd(self):
        """Test ensure_odd function."""
        assert ensure_odd(1) == 1
        assert ensure_odd(2) == 3
        assert ensure_odd(4) == 5
        assert ensure_odd(5) == 5

    def test_parse_hsv_triplet_valid(self):
        """Test parsing valid HSV triplet."""
        result = parse_hsv_triplet("10,20,30")
        assert result == (10, 20, 30)

    def test_parse_hsv_triplet_invalid_format(self):
        """Test parsing invalid HSV triplet format."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_hsv_triplet("10,20")

    def test_parse_hsv_triplet_invalid_values(self):
        """Test parsing HSV triplet with invalid values."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_hsv_triplet("180,20,30")  # H > 179