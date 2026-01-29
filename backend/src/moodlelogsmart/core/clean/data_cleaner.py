"""Data cleaning module for Moodle event logs."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class CleaningConfig:
    """Configuration for data cleaning."""

    student_role_id: str = "5"
    # Non-student events to filter out
    non_student_events: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.non_student_events:
            self.non_student_events = [
                "Course section deleted",
                "Course backup created",
                "Course updated",
                "Course restored",
                "Course reset",
                "Course roleover",
            ]


class RoleFilter:
    """Filters events by user role."""

    def __init__(self, student_role_id: str = "5"):
        self.student_role_id = student_role_id

    def filter(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter events to keep only student role events."""
        # Placeholder: Would check role field in events
        return events


class EventFilter:
    """Filters out non-student events."""

    def __init__(self, non_student_events: List[str]):
        self.non_student_events = non_student_events

    def filter(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove non-student events."""
        return [
            e
            for e in events
            if e.get("event_name") not in self.non_student_events
        ]


class DataCleaner:
    """Cleans and validates Moodle event log data."""

    def __init__(self, config: Optional[CleaningConfig] = None):
        self.config = config or CleaningConfig()
        self.role_filter = RoleFilter(self.config.student_role_id)
        self.event_filter = EventFilter(self.config.non_student_events)

    def clean(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all cleaning steps."""
        # Step 1: Filter by role
        events = self.role_filter.filter(events)
        logger.info(f"After role filter: {len(events)} events")

        # Step 2: Filter by event type
        events = self.event_filter.filter(events)
        logger.info(f"After event filter: {len(events)} events")

        # Step 3: Validate timestamps
        events = self._validate_timestamps(events)
        logger.info(f"After timestamp validation: {len(events)} events")

        # Step 4: Normalize data types
        events = self._normalize_types(events)

        return events

    def _validate_timestamps(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and remove events with invalid timestamps."""
        valid = []
        for e in events:
            if e.get("time") is not None:
                valid.append(e)
        return valid

    def _normalize_types(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize data types in events."""
        return events
