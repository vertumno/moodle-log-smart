"""Export module for processed event logs."""

from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CSVExporter:
    """Exports events to CSV format."""

    def export(self, events: List[Dict[str, Any]], output_path: str) -> None:
        """Export events to CSV.

        Args:
            events: List of event dictionaries
            output_path: Path to save CSV file
        """
        if not events:
            raise ValueError("Cannot export empty events list")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Get column names from first event
        if not events:
            return

        fieldnames = list(events[0].keys())

        # Simple CSV writing
        with open(output_file, "w", encoding="utf-8") as f:
            # Write header
            f.write(",".join(fieldnames) + "\n")

            # Write data rows
            for event in events:
                row = [
                    str(event.get(col, "")).replace(",", ";")  # Escape commas
                    for col in fieldnames
                ]
                f.write(",".join(row) + "\n")

        logger.info(f"Exported {len(events)} events to {output_path}")

    def export_filtered(
        self, events: List[Dict[str, Any]], output_path: str, filter_field: str, filter_value: Any
    ) -> None:
        """Export filtered events to CSV.

        Args:
            events: List of event dictionaries
            output_path: Path to save CSV file
            filter_field: Field to filter by
            filter_value: Value to match
        """
        filtered = [e for e in events if e.get(filter_field) == filter_value]
        self.export(filtered, output_path)
        logger.info(
            f"Exported {len(filtered)} filtered events (where {filter_field}={filter_value})"
        )


class EventLogExporter:
    """Main exporter orchestrating all formats."""

    def __init__(self):
        self.csv_exporter = CSVExporter()

    def export_all(self, events: List[Dict[str, Any]], output_dir: str) -> Dict[str, str]:
        """Export events in all formats.

        Args:
            events: List of event dictionaries
            output_dir: Directory to save exports

        Returns:
            Dictionary mapping format to file path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        files = {}

        # Export full CSV
        csv_path = str(output_dir / "enriched_log.csv")
        self.csv_exporter.export(events, csv_path)
        files["csv_full"] = csv_path

        # Export Bloom-only CSV
        bloom_events = [e for e in events if e.get("bloom_level") != "Unknown"]
        if bloom_events:
            csv_bloom_path = str(output_dir / "enriched_log_bloom_only.csv")
            self.csv_exporter.export(bloom_events, csv_bloom_path)
            files["csv_bloom"] = csv_bloom_path

        logger.info(f"Export complete: {len(files)} files created")
        return files

    def export_csv_only(self, events: List[Dict[str, Any]], output_dir: str) -> str:
        """Export as CSV only.

        Args:
            events: List of event dictionaries
            output_dir: Directory to save

        Returns:
            Path to exported file
        """
        output_file = Path(output_dir) / "enriched_log.csv"
        self.csv_exporter.export(events, str(output_file))
        return str(output_file)

    def export_bloom_only(self, events: List[Dict[str, Any]], output_dir: str) -> str:
        """Export only Bloom-classified events.

        Args:
            events: List of event dictionaries
            output_dir: Directory to save

        Returns:
            Path to exported file
        """
        bloom_events = [e for e in events if e.get("bloom_level") != "Unknown"]
        output_file = Path(output_dir) / "enriched_log_bloom_only.csv"
        self.csv_exporter.export(bloom_events, str(output_file))
        return str(output_file)
