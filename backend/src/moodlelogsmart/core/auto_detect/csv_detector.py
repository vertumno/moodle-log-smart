"""CSV format detection module.

Automatically detects encoding, delimiter, and structure of CSV files.
"""

from dataclasses import dataclass
import chardet
import csv
from pathlib import Path
from typing import Tuple


@dataclass
class CSVFormat:
    """Detected CSV format information."""

    encoding: str
    """Detected character encoding (e.g., 'utf-8', 'iso-8859-1')"""

    delimiter: str
    """Detected field delimiter (e.g., ',', ';', '\t', '|')"""

    has_header: bool
    """Whether CSV contains header row"""

    line_count: int
    """Total number of lines in CSV (including header)"""


class CSVDetector:
    """Detects format of CSV files automatically.

    Analyzes CSV files to determine:
    - Character encoding (UTF-8, Latin-1, CP1252, etc.)
    - Field delimiter (comma, semicolon, tab, pipe)
    - Presence of header row
    - Basic structure validity
    """

    COMMON_DELIMITERS = [',', ';', '\t', '|']

    def detect(self, file_path: str) -> CSVFormat:
        """Detect encoding, delimiter and structure of CSV.

        Args:
            file_path: Path to CSV file

        Returns:
            CSVFormat with detected information

        Raises:
            ValueError: If file is invalid or unreadable
        """
        path = Path(file_path)

        # Validate file exists
        if not path.exists():
            raise ValueError(f"Arquivo não encontrado: {file_path}")

        # Validate file is not empty
        if path.stat().st_size == 0:
            raise ValueError("Arquivo CSV está vazio")

        # Detect encoding
        encoding = self._detect_encoding(file_path)

        # Detect delimiter
        delimiter = self._detect_delimiter(file_path, encoding)

        # Validate structure
        has_header, line_count = self._validate_structure(
            file_path, encoding, delimiter
        )

        return CSVFormat(
            encoding=encoding,
            delimiter=delimiter,
            has_header=has_header,
            line_count=line_count,
        )

    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet.

        Args:
            file_path: Path to CSV file

        Returns:
            Detected encoding name (lowercase)

        Raises:
            ValueError: If encoding cannot be detected with confidence
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)

            if result['confidence'] < 0.7:
                raise ValueError(
                    "Não foi possível detectar encoding do arquivo. "
                    f"Confiança: {result['confidence']:.2f}"
                )

            return result['encoding'].lower()

    def _detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Detect delimiter by testing common formats.

        Args:
            file_path: Path to CSV file
            encoding: File encoding

        Returns:
            Detected delimiter character

        Raises:
            ValueError: If no valid delimiter is found
        """
        with open(file_path, 'r', encoding=encoding) as f:
            sample = f.read(1024)  # Sample first lines

            # Test each common delimiter
            delimiter_counts = {}
            for delim in self.COMMON_DELIMITERS:
                count = sample.count(delim)
                delimiter_counts[delim] = count

            # Return most frequent delimiter
            best_delim = max(delimiter_counts, key=delimiter_counts.get)

            if delimiter_counts[best_delim] == 0:
                raise ValueError(
                    "Não foi possível detectar delimiter. "
                    f"Testados: {self.COMMON_DELIMITERS}"
                )

            return best_delim

    def _validate_structure(
        self,
        file_path: str,
        encoding: str,
        delimiter: str,
    ) -> Tuple[bool, int]:
        """Validate basic CSV structure.

        Args:
            file_path: Path to CSV file
            encoding: File encoding
            delimiter: Field delimiter

        Returns:
            Tuple of (has_header, line_count)

        Raises:
            ValueError: If CSV structure is invalid
        """
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)

            try:
                # Read header
                header = next(reader)
                has_header = len(header) > 0

                # Count lines
                line_count = 1 + sum(1 for _ in reader)

                if line_count < 2:
                    raise ValueError(
                        "CSV deve ter pelo menos 2 linhas (header + dados)"
                    )

                return has_header, line_count

            except StopIteration:
                raise ValueError("CSV não contém dados")
