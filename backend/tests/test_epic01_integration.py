"""Integration tests for Epic 1 - Complete pipeline validation.

Tests the complete processing pipeline from CSV to enriched output.
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime

from moodlelogsmart.core.auto_detect.csv_detector import CSVDetector
from moodlelogsmart.core.auto_detect.column_mapper import ColumnMapper
from moodlelogsmart.core.auto_detect.timestamp_detector import TimestampDetector
from moodlelogsmart.core.clean.data_cleaner import DataCleaner
from moodlelogsmart.core.rules.bloom_classifier import BloomClassifier
from moodlelogsmart.core.rules.rule_engine import RuleEngine


class TestEpic01Integration:
    """Integration tests for complete Epic 1 pipeline."""

    def test_bloom_taxonomy_yaml_exists(self):
        """Test that bloom_taxonomy.yaml exists and is valid."""
        yaml_path = Path(__file__).parent.parent / 'src' / 'moodlelogsmart' / 'core' / 'rules' / 'bloom_taxonomy.yaml'

        assert yaml_path.exists(), "bloom_taxonomy.yaml not found"

        # Should load without errors
        engine = RuleEngine(yaml_path=str(yaml_path))
        assert len(engine.rules) >= 13, "Should have at least 13 rules"

    def test_rule_engine_loads_default_yaml(self):
        """Test that RuleEngine loads default YAML when no path provided."""
        engine = RuleEngine()

        assert len(engine.rules) >= 13
        assert engine.rules[0].priority < engine.rules[-1].priority, "Rules should be sorted by priority"

    def test_bloom_classifier_initialization(self):
        """Test BloomClassifier initialization."""
        classifier = BloomClassifier()

        assert classifier.rule_engine is not None
        assert len(classifier.rule_engine.rules) >= 13

    def test_bloom_classifier_with_dataframe(self):
        """Test BloomClassifier.apply_rules() with DataFrame."""
        # Create sample DataFrame
        df = pd.DataFrame([
            {
                'time': datetime(2026, 1, 22, 23, 26, 24),
                'user_full_name': 'João Silva',
                'event_name': 'Course module viewed',
                'component': 'File',
                'event_context': 'Curso: Matemática',
                'description': 'User viewed file',
                'affected_user': None,
                'origin': 'web',
                'ip_address': '192.168.1.1',
            },
            {
                'time': datetime(2026, 1, 22, 23, 30, 0),
                'user_full_name': 'Maria Santos',
                'event_name': 'Post created',
                'component': 'Forum',
                'event_context': 'Curso: Física',
                'description': 'User created forum post',
                'affected_user': None,
                'origin': 'web',
                'ip_address': '192.168.1.2',
            },
        ])

        classifier = BloomClassifier()
        enriched_df = classifier.apply_rules(df)

        # Verify enrichment columns exist
        assert 'activity_type' in enriched_df.columns
        assert 'bloom_level' in enriched_df.columns
        assert 'is_active' in enriched_df.columns

        # Verify row count unchanged
        assert len(enriched_df) == 2

        # Verify first row (View Resource - passive)
        assert enriched_df.iloc[0]['activity_type'] == 'Study_P'
        assert enriched_df.iloc[0]['bloom_level'] == 'Remember'
        assert enriched_df.iloc[0]['is_active'] == False

        # Verify second row (Forum Post - active)
        assert enriched_df.iloc[1]['activity_type'] == 'Collab_A'
        assert enriched_df.iloc[1]['bloom_level'] == 'Create'
        assert enriched_df.iloc[1]['is_active'] == True

    def test_complete_pipeline_portuguese_csv(self):
        """Test complete pipeline with Portuguese CSV headers."""
        # Simulate DataFrame after column mapping (Portuguese → English)
        df = pd.DataFrame([
            {
                'time': '22/01/26, 23:26:24',
                'user_full_name': 'Elton Silva',
                'event_name': 'Course module viewed',
                'component': 'Page',
                'event_context': 'Curso: Tecnologias Educacionais',
                'description': 'Usuário visualizou página',
                'affected_user': '-',
                'origin': 'web',
                'ip_address': '172.26.44.11',
            },
        ])

        # Step 1: Detect timestamp format
        timestamp_detector = TimestampDetector()
        timestamps = df['time'].tolist()
        fmt = timestamp_detector.detect_format(timestamps)

        assert fmt == "%d/%m/%y, %H:%M:%S"

        # Parse timestamps
        df['time'] = pd.to_datetime(df['time'], format=fmt)

        # Step 2: Clean data
        cleaner = DataCleaner()
        events_list = df.to_dict('records')
        cleaned_events = cleaner.clean(events_list)
        cleaned_df = pd.DataFrame(cleaned_events)

        assert len(cleaned_df) > 0

        # Step 3: Apply Bloom classification
        classifier = BloomClassifier()
        enriched_df = classifier.apply_rules(cleaned_df)

        # Verify enrichment
        assert 'activity_type' in enriched_df.columns
        assert 'bloom_level' in enriched_df.columns
        assert 'is_active' in enriched_df.columns

        # Page view should be Remember level
        assert enriched_df.iloc[0]['bloom_level'] in ['Remember', 'Understand']

    def test_bloom_levels_coverage(self):
        """Test that rules cover different Bloom levels."""
        engine = RuleEngine()

        bloom_levels = set()
        for rule in engine.rules:
            bloom_levels.add(rule.action.bloom_level)

        # Should have multiple Bloom levels represented
        assert len(bloom_levels) >= 3, "Should cover at least 3 different Bloom levels"

        expected_levels = {'Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'}
        assert bloom_levels.issubset(expected_levels), "All levels should be valid Bloom levels"

    def test_rule_priority_ordering(self):
        """Test that rules are applied in correct priority order."""
        engine = RuleEngine()

        priorities = [rule.priority for rule in engine.rules]

        # Should be sorted ascending
        assert priorities == sorted(priorities), "Rules must be sorted by priority"

        # Default rule should have highest priority number
        assert priorities[-1] == 99, "Default rule should have priority 99"

    def test_classifier_statistics(self):
        """Test BloomClassifier.get_statistics() method."""
        df = pd.DataFrame([
            {
                'time': datetime(2026, 1, 22, 23, 26, 24),
                'user_full_name': 'Test User',
                'event_name': 'Course module viewed',
                'component': 'File',
                'event_context': 'Test',
                'description': 'Test',
                'activity_type': 'Study_P',
                'bloom_level': 'Remember',
                'is_active': False,
            },
            {
                'time': datetime(2026, 1, 22, 23, 30, 0),
                'user_full_name': 'Test User 2',
                'event_name': 'Submission created',
                'component': 'Assignment',
                'event_context': 'Test',
                'description': 'Test',
                'activity_type': 'Prod_A',
                'bloom_level': 'Create',
                'is_active': True,
            },
        ])

        classifier = BloomClassifier()
        stats = classifier.get_statistics(df)

        assert stats['total_events'] == 2
        assert stats['active_events'] == 1
        assert stats['passive_events'] == 1
        assert 'Remember' in stats['bloom_levels']
        assert 'Create' in stats['bloom_levels']
