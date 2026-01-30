"""Domain models for Moodle event processing."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RawMoodleEvent:
    """Raw Moodle event from CSV (after column mapping)."""

    time: datetime
    user_full_name: str
    event_name: str
    component: str
    event_context: str
    description: str
    affected_user: Optional[str] = None
    origin: Optional[str] = None
    ip_address: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for DataFrame conversion."""
        return {
            'time': self.time,
            'user_full_name': self.user_full_name,
            'event_name': self.event_name,
            'component': self.component,
            'event_context': self.event_context,
            'description': self.description,
            'affected_user': self.affected_user,
            'origin': self.origin,
            'ip_address': self.ip_address,
        }


@dataclass
class EnrichedActivity(RawMoodleEvent):
    """Enriched activity with Bloom's Taxonomy classification."""

    activity_type: str = "Others"
    bloom_level: str = "Remember"
    is_active: bool = False

    def to_dict(self):
        """Convert to dictionary including enrichment fields."""
        base_dict = super().to_dict()
        base_dict.update({
            'activity_type': self.activity_type,
            'bloom_level': self.bloom_level,
            'is_active': self.is_active,
        })
        return base_dict
