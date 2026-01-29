"""Timestamp format detection module.

Automatically detects timestamp format and parses to datetime objects.
"""

from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class TimestampDetector:
    """Detects timestamp format automatically.

    Supports multiple timestamp formats common to Moodle exports:
    - Brazilian format (dd/mm/yy)
    - ISO format (yyyy-mm-dd)
    - US format (mm/dd/yyyy)
    - European format (dd-mm-yyyy)
    - And more...
    """

    # Common formats ordered by probability (Moodle typical first)
    COMMON_FORMATS = [
        "%d/%m/%y, %H:%M:%S",  # BR: 22/08/24, 13:43:23 (MOST COMMON)
        "%d/%m/%Y %H:%M:%S",  # BR: 22/08/2024 13:43:23
        "%Y-%m-%d %H:%M:%S",  # ISO: 2024-08-22 13:43:23
        "%d-%m-%Y %H:%M:%S",  # EU: 22-08-2024 13:43:23
        "%m/%d/%Y %I:%M:%S %p",  # US 12h: 08/22/2024 01:43:23 PM
        "%m/%d/%Y %H:%M:%S",  # US 24h: 08/22/2024 13:43:23
        "%m/%d/%y %H:%M:%S",  # US short: 08/22/24 13:43:23
        "%Y/%m/%d %H:%M:%S",  # Asia: 2024/08/22 13:43:23
        "%d.%m.%Y %H:%M:%S",  # DE: 22.08.2024 13:43:23
        "%Y-%m-%dT%H:%M:%S",  # ISO-8601: 2024-08-22T13:43:23
        "%Y-%m-%dT%H:%M:%S.%f",  # ISO with ms: 2024-08-22T13:43:23.000
        "%d %b %Y %H:%M:%S",  # UK: 22 Aug 2024 13:43:23
    ]

    def detect_format(self, timestamps: List[str]) -> Optional[str]:
        """Detect timestamp format by testing common formats.

        Args:
            timestamps: List of timestamp strings

        Returns:
            Format string (strptime) or None (use pandas inference)

        Raises:
            ValueError: If timestamps are empty or invalid
        """
        if len(timestamps) == 0:
            raise ValueError("Lista de timestamps está vazia")

        # Remove None values
        timestamps_clean = [ts for ts in timestamps if ts is not None and str(ts).strip()]

        if len(timestamps_clean) == 0:
            raise ValueError("Todos os timestamps são nulos")

        # Use sample (first 100 for performance)
        sample = timestamps_clean[:100]

        # Test each common format
        for fmt in self.COMMON_FORMATS:
            if self._test_format(sample, fmt):
                logger.info(f"Formato detectado: {fmt}")
                return fmt

        # Fallback: let pandas decide
        logger.warning(
            "Formato de timestamp não reconhecido. "
            "Usando pandas auto-inference."
        )
        return None

    def _test_format(self, timestamps: List[str], fmt: str) -> bool:
        """Test if format works for timestamps.

        Args:
            timestamps: Sample of timestamp strings
            fmt: strptime format to test

        Returns:
            True if format works for >90% of sample
        """
        successful_parses = 0
        total = len(timestamps)

        for ts_str in timestamps:
            try:
                # Try to parse with format
                datetime.strptime(str(ts_str).strip(), fmt)
                successful_parses += 1
            except (ValueError, TypeError):
                # Format doesn't match
                continue

        # Format accepted if >90% of timestamps parse successfully
        success_rate = successful_parses / total if total > 0 else 0
        return success_rate > 0.9

    def parse_timestamps(
        self, timestamps: List[str], fmt: Optional[str] = None
    ) -> List[datetime]:
        """Parse timestamps to datetime objects.

        Args:
            timestamps: List of timestamp strings
            fmt: Format string (auto-detect if None)

        Returns:
            List of datetime objects

        Raises:
            ValueError: If parsing fails
        """
        if fmt is None:
            fmt = self.detect_format(timestamps)

        result = []

        for ts_str in timestamps:
            try:
                if fmt:
                    dt = datetime.strptime(str(ts_str).strip(), fmt)
                else:
                    # Fallback: try multiple formats
                    dt = None
                    for fallback_fmt in self.COMMON_FORMATS:
                        try:
                            dt = datetime.strptime(str(ts_str).strip(), fallback_fmt)
                            break
                        except ValueError:
                            continue

                    if dt is None:
                        raise ValueError(f"Não conseguiu parsear: {ts_str}")

                result.append(dt)
            except Exception as e:
                raise ValueError(f"Erro ao parsear timestamp '{ts_str}': {e}")

        return result
