"""Test for TimestampDetector method name fix.

Validates that detect_format() method works correctly with Portuguese CSV data.
"""

import pytest
from moodlelogsmart.core.auto_detect.timestamp_detector import TimestampDetector


class TestTimestampDetectorFix:
    """Test TimestampDetector.detect_format() method."""

    def test_detect_format_brazilian_format(self):
        """Test detection of Brazilian timestamp format (dd/mm/yy, HH:MM:SS)."""
        # Sample from user's CSV: "22/01/26, 23:26:24"
        timestamps = [
            "22/01/26, 23:26:24",
            "22/01/26, 23:26:16",
            "22/01/26, 23:26:10",
            "21/01/26, 13:00:32",
        ]

        detector = TimestampDetector()
        detected_format = detector.detect_format(timestamps)

        # Should detect Brazilian format (most common in Moodle BR exports)
        assert detected_format == "%d/%m/%y, %H:%M:%S"

    def test_detect_format_method_exists(self):
        """Test that detect_format method exists (not 'detect')."""
        detector = TimestampDetector()

        # Should have detect_format method
        assert hasattr(detector, 'detect_format')
        assert callable(detector.detect_format)

        # Should NOT have detect method (this was the bug)
        assert not hasattr(detector, 'detect')

    def test_parse_timestamps_with_detected_format(self):
        """Test parsing timestamps with auto-detected format."""
        timestamps = [
            "22/01/26, 23:26:24",
            "21/01/26, 13:00:32",
        ]

        detector = TimestampDetector()

        # Detect format
        fmt = detector.detect_format(timestamps)
        assert fmt is not None

        # Parse timestamps
        parsed = detector.parse_timestamps(timestamps, fmt)

        assert len(parsed) == 2
        assert parsed[0].day == 22
        assert parsed[0].month == 1
        assert parsed[0].year == 2026  # %y = 26 → 2026
        assert parsed[0].hour == 23
        assert parsed[0].minute == 26
        assert parsed[0].second == 24

    def test_detect_format_with_multiple_formats(self):
        """Test detection with various timestamp formats."""
        test_cases = [
            # Brazilian format
            (
                ["22/01/26, 23:26:24", "21/01/26, 13:00:32"],
                "%d/%m/%y, %H:%M:%S"
            ),
            # ISO format
            (
                ["2024-08-22 13:43:23", "2024-08-21 12:30:45"],
                "%Y-%m-%d %H:%M:%S"
            ),
            # European format
            (
                ["22-08-2024 13:43:23", "21-08-2024 12:30:45"],
                "%d-%m-%Y %H:%M:%S"
            ),
        ]

        detector = TimestampDetector()

        for timestamps, expected_format in test_cases:
            detected = detector.detect_format(timestamps)
            assert detected == expected_format, f"Failed for {timestamps}"

    def test_detect_format_handles_empty_list(self):
        """Test that detect_format raises ValueError for empty list."""
        detector = TimestampDetector()

        with pytest.raises(ValueError, match="Lista de timestamps está vazia"):
            detector.detect_format([])

    def test_detect_format_handles_none_values(self):
        """Test that detect_format filters out None values."""
        timestamps = [
            "22/01/26, 23:26:24",
            None,
            "21/01/26, 13:00:32",
            None,
        ]

        detector = TimestampDetector()
        detected = detector.detect_format(timestamps)

        # Should still detect format ignoring None values
        assert detected == "%d/%m/%y, %H:%M:%S"
