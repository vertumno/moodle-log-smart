"""Column mapping module for Moodle CSV.

Automatically maps Moodle column name variations to standardized internal schema.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from rapidfuzz import fuzz
except ImportError:
    # Fallback if rapidfuzz not available
    from difflib import SequenceMatcher

    class FuzzFallback:
        @staticmethod
        def ratio(a: str, b: str) -> float:
            """Calculate similarity ratio (0-100) between two strings."""
            return SequenceMatcher(None, a, b).ratio() * 100

    fuzz = FuzzFallback()


@dataclass
class ColumnMapping:
    """Mapping of Moodle CSV columns to internal schema."""

    time: Optional[str] = None
    """Timestamp column (e.g., 'Time', 'Timestamp', 'Date/Time')"""

    user_full_name: Optional[str] = None
    """User full name column"""

    event_name: Optional[str] = None
    """Event name column (e.g., 'Event name', 'Action')"""

    component: Optional[str] = None
    """Component/Module column"""

    event_context: Optional[str] = None
    """Event context column"""

    description: Optional[str] = None
    """Description/Details column"""

    affected_user: Optional[str] = None
    """Affected user column (optional)"""

    origin: Optional[str] = None
    """Origin/Source column (optional)"""

    ip_address: Optional[str] = None
    """IP address column (optional)"""


class ColumnMapper:
    """Maps Moodle CSV columns to standardized internal schema.

    Supports column name variations through:
    - Exact matching (case-insensitive)
    - Fuzzy matching for slight variations
    - Common aliases for known Moodle columns
    """

    # Dictionary of known aliases for each internal column
    COLUMN_ALIASES = {
        'time': [
            'Time',
            'Timestamp',
            'Date/Time',
            'Event time',
            'DateTime',
            'Date and time',
        ],
        'user_full_name': [
            'User full name',
            'Full name',
            'User name',
            'Name',
            'Username',
            'User',
        ],
        'event_name': [
            'Event name',
            'Event',
            'Action',
            'Event type',
            'Activity',
        ],
        'component': [
            'Component',
            'Event component',
            'Module',
            'Component name',
        ],
        'event_context': [
            'Event context',
            'Context',
            'Course',
            'Resource',
            'Activity context',
        ],
        'description': [
            'Description',
            'Details',
            'Info',
            'Information',
            'Event description',
        ],
        'affected_user': [
            'Affected user',
            'Related user',
            'Target user',
        ],
        'origin': [
            'Origin',
            'Source',
            'Event origin',
        ],
        'ip_address': [
            'IP address',
            'IP',
            'User IP',
            'Client IP',
        ],
    }

    FUZZY_THRESHOLD = 80  # Minimum similarity for fuzzy match (0-100)

    def map_columns(self, csv_columns: List[str]) -> ColumnMapping:
        """Map CSV columns to internal schema.

        Args:
            csv_columns: List of column names from CSV

        Returns:
            ColumnMapping with matched column names

        Raises:
            ValueError: If required columns are not found
        """
        mapping = {}

        # Map each internal column
        for internal_name, aliases in self.COLUMN_ALIASES.items():
            matched_column = self._find_best_match(csv_columns, aliases)

            # Required columns
            if internal_name in [
                'time',
                'user_full_name',
                'event_name',
                'component',
                'event_context',
                'description',
            ]:
                if matched_column is None:
                    raise ValueError(
                        f"Coluna obrigatória não encontrada: {internal_name}. "
                        f"Esperado um dos: {', '.join(aliases)}"
                    )

            mapping[internal_name] = matched_column

        return ColumnMapping(**mapping)

    def _find_best_match(
        self, csv_columns: List[str], aliases: List[str]
    ) -> Optional[str]:
        """Find best match between CSV columns and known aliases.

        Tries exact match first (case-insensitive), then fuzzy matching.

        Args:
            csv_columns: List of CSV column names
            aliases: List of known aliases for this column

        Returns:
            CSV column name that best matches, or None
        """
        # First try exact match (case-insensitive)
        for alias in aliases:
            for csv_col in csv_columns:
                if csv_col.lower() == alias.lower():
                    return csv_col

        # If no exact match, use fuzzy matching
        best_match = None
        best_score = 0

        for alias in aliases:
            for csv_col in csv_columns:
                # Calculate similarity (0-100)
                if hasattr(fuzz, 'ratio'):
                    score = fuzz.ratio(csv_col.lower(), alias.lower())
                else:
                    # Fallback implementation
                    score = fuzz.ratio(csv_col.lower(), alias.lower())

                if score > best_score and score >= self.FUZZY_THRESHOLD:
                    best_score = score
                    best_match = csv_col

        return best_match

    def rename_dataframe_columns(
        self, columns: List[str], mapping: ColumnMapping
    ) -> Dict[str, str]:
        """Generate column rename mapping for DataFrame.

        Args:
            columns: Original column names
            mapping: ColumnMapping with matched columns

        Returns:
            Dictionary mapping original to internal names
        """
        rename_dict = {}

        for internal_name, csv_column in mapping.__dict__.items():
            if csv_column is not None:
                rename_dict[csv_column] = internal_name

        return rename_dict
