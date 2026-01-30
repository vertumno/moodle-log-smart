"""Bloom's Taxonomy Classifier - Wrapper for RuleEngine with DataFrame support."""

from typing import Optional
from pathlib import Path
import pandas as pd
import logging

from .rule_engine import RuleEngine
from moodlelogsmart.domain.models import RawMoodleEvent, EnrichedActivity

logger = logging.getLogger(__name__)


class BloomClassifier:
    """High-level wrapper for Bloom's Taxonomy classification.

    Provides convenient interface for classifying Moodle events
    using pandas DataFrames.
    """

    def __init__(self, yaml_path: Optional[str] = None):
        """Initialize classifier with rules from YAML file.

        Args:
            yaml_path: Path to YAML file with rules (optional)
                      If not provided, uses default bloom_taxonomy.yaml
        """
        self.rule_engine = RuleEngine(yaml_path=yaml_path)
        logger.info(f"BloomClassifier initialized with {len(self.rule_engine.rules)} rules")

    def apply_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply Bloom classification rules to DataFrame.

        Args:
            df: DataFrame with columns: time, user_full_name, event_name,
                component, event_context, description

        Returns:
            DataFrame with added columns: activity_type, bloom_level, is_active
        """
        logger.info(f"Classifying {len(df)} events with Bloom taxonomy")

        enriched_events = []

        for _, row in df.iterrows():
            # Convert row to dict for event creation
            event_dict = row.to_dict()

            # Apply rules
            enriched = self.rule_engine.evaluate(event_dict)

            enriched_events.append(enriched)

        # Convert to DataFrame
        result_df = pd.DataFrame(enriched_events)

        logger.info(
            f"Classification complete. "
            f"Active events: {result_df['is_active'].sum()}/{len(result_df)}"
        )

        return result_df

    def get_statistics(self, df: pd.DataFrame) -> dict:
        """Get statistics about classified events.

        Args:
            df: DataFrame with classification columns

        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_events': len(df),
            'active_events': int(df['is_active'].sum()),
            'passive_events': int((~df['is_active']).sum()),
            'bloom_levels': df['bloom_level'].value_counts().to_dict(),
            'activity_types': df['activity_type'].value_counts().to_dict(),
        }
        return stats
