"""Export module for processed event logs."""

from typing import List, Dict, Any
from pathlib import Path
import logging
from datetime import datetime

try:
    from pm4py.objects.log.log import EventLog, Trace, Event
    from pm4py.objects.log.log import Event as PM4PYEvent
    from pm4py.export_variants import export_log as pm4py_export
    HAS_PM4PY = True
except ImportError:
    HAS_PM4PY = False

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


class XESExporter:
    """Exports events to XES (eXtensible Event Stream) format for process mining."""

    def export(self, events: List[Dict[str, Any]], output_path: str) -> None:
        """Export events to XES format.

        Args:
            events: List of event dictionaries
            output_path: Path to save XES file

        Raises:
            ImportError: If PM4Py is not installed
            ValueError: If events list is empty
        """
        if not HAS_PM4PY:
            logger.warning("PM4Py not installed, XES export skipped")
            return

        if not events:
            raise ValueError("Cannot export empty events list")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Create event log
            log = EventLog()

            # Group events by user to create traces
            traces_dict = {}
            for event_dict in events:
                user = event_dict.get("user_full_name", "Unknown")
                if user not in traces_dict:
                    traces_dict[user] = []
                traces_dict[user].append(event_dict)

            # Create traces
            for user, user_events in traces_dict.items():
                trace = Trace()
                trace.attributes["concept:name"] = str(user)

                # Add events to trace
                for event_dict in user_events:
                    event = Event()
                    event["concept:name"] = event_dict.get(
                        "activity_type", event_dict.get("event_name", "Unknown")
                    )

                    # Add timestamp
                    time_str = event_dict.get("time")
                    if time_str:
                        try:
                            if isinstance(time_str, str):
                                event["time:timestamp"] = datetime.fromisoformat(time_str)
                            else:
                                event["time:timestamp"] = time_str
                        except (ValueError, TypeError):
                            logger.debug(f"Could not parse timestamp: {time_str}")

                    # Add other attributes
                    event["lifecycle:transition"] = "complete"
                    event["org:resource"] = event_dict.get("component", "Unknown")

                    if "bloom_level" in event_dict:
                        event["bloom:level"] = str(event_dict["bloom_level"])

                    trace.append(event)

                log.append(trace)

            # Export using PM4Py
            pm4py_export.export_log(log, output_path)
            logger.info(f"Exported {len(log)} traces to {output_path}")

        except Exception as e:
            logger.error(f"XES export failed: {str(e)}")
            raise
