"""Rule engine for event classification."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__)


@dataclass
class RuleCondition:
    """Single rule condition."""

    field: str
    operator: str  # equals, in, contains
    value: Any = None
    values: List[Any] = None


@dataclass
class RuleAction:
    """Action to apply when rule matches."""

    activity_type: str
    bloom_level: str
    is_active: bool = False


@dataclass
class Rule:
    """A classification rule."""

    id: str
    name: str
    priority: int
    conditions: List[RuleCondition]
    action: RuleAction


class RuleEngine:
    """Evaluates rules against events for classification."""

    def __init__(self, rules: Optional[List[Rule]] = None, yaml_path: Optional[str] = None):
        """Initialize RuleEngine with rules from list or YAML file.

        Args:
            rules: List of Rule objects (optional)
            yaml_path: Path to YAML file with rules (optional)

        If yaml_path is provided, rules are loaded from file.
        If neither is provided, loads from default bloom_taxonomy.yaml.
        """
        if yaml_path:
            self.rules = self._load_rules_from_yaml(yaml_path)
        elif rules:
            self.rules = sorted(rules, key=lambda r: r.priority)
        else:
            # Load default rules from bloom_taxonomy.yaml
            default_path = Path(__file__).parent / 'bloom_taxonomy.yaml'
            self.rules = self._load_rules_from_yaml(str(default_path))

    def _load_rules_from_yaml(self, yaml_path: str) -> List[Rule]:
        """Load rules from YAML file.

        Args:
            yaml_path: Path to YAML file

        Returns:
            List of Rule objects sorted by priority
        """
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        rules = []
        for rule_data in data.get('rules', []):
            # Parse conditions
            conditions = []
            for cond_data in rule_data.get('conditions', []):
                conditions.append(RuleCondition(
                    field=cond_data['field'],
                    operator=cond_data['operator'],
                    value=cond_data.get('value'),
                    values=cond_data.get('values'),
                ))

            # Parse action
            action_data = rule_data['action']
            action = RuleAction(
                activity_type=action_data['activity_type'],
                bloom_level=action_data['bloom_level'],
                is_active=action_data.get('is_active', False),
            )

            # Create rule
            rule = Rule(
                id=rule_data['id'],
                name=rule_data['name'],
                priority=rule_data['priority'],
                conditions=conditions,
                action=action,
            )
            rules.append(rule)

        # Sort by priority
        return sorted(rules, key=lambda r: r.priority)

    def evaluate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate event against rules and apply action.

        Args:
            event: Event to classify

        Returns:
            Event with added fields: activity_type, bloom_level, is_active
        """
        # Try each rule in priority order
        for rule in self.rules:
            if self._matches_all_conditions(event, rule.conditions):
                logger.debug(f"Event matched rule: {rule.name}")
                return self._apply_action(event, rule.action)

        # Default: if no rule matched
        return self._apply_default(event)

    def _matches_all_conditions(
        self, event: Dict[str, Any], conditions: List[RuleCondition]
    ) -> bool:
        """Check if event matches all conditions."""
        for condition in conditions:
            if not self._matches_condition(event, condition):
                return False
        return True

    def _matches_condition(
        self, event: Dict[str, Any], condition: RuleCondition
    ) -> bool:
        """Check if event matches single condition."""
        field_value = event.get(condition.field)

        if condition.operator == "equals":
            return field_value == condition.value

        elif condition.operator == "in":
            return field_value in (condition.values or [])

        elif condition.operator == "contains":
            if isinstance(field_value, str):
                return condition.value in field_value
            return False

        return False

    def _apply_action(
        self, event: Dict[str, Any], action: RuleAction
    ) -> Dict[str, Any]:
        """Apply rule action to event."""
        event_copy = event.copy()
        event_copy["activity_type"] = action.activity_type
        event_copy["bloom_level"] = action.bloom_level
        event_copy["is_active"] = action.is_active
        return event_copy

    def _apply_default(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default classification."""
        event_copy = event.copy()
        event_copy["activity_type"] = "Other"
        event_copy["bloom_level"] = "Unknown"
        event_copy["is_active"] = False
        return event_copy


class BloomClassifier:
    """Classifies events using Bloom taxonomy rules."""

    def __init__(self):
        # Define Bloom taxonomy rules
        self.rules = self._load_rules()
        self.engine = RuleEngine(self.rules)

    def _load_rules(self) -> List[Rule]:
        """Load Bloom taxonomy rules."""
        return [
            Rule(
                id="R01",
                name="View Resource",
                priority=1,
                conditions=[
                    RuleCondition(
                        field="component",
                        operator="in",
                        values=["resource", "mod_page", "mod_file"],
                    ),
                    RuleCondition(
                        field="event_name", operator="equals", value="Course module viewed"
                    ),
                ],
                action=RuleAction(
                    activity_type="Study_P", bloom_level="Remember", is_active=False
                ),
            ),
            Rule(
                id="R02",
                name="Complete Assignment",
                priority=2,
                conditions=[
                    RuleCondition(field="component", operator="equals", value="assignment"),
                    RuleCondition(
                        field="event_name", operator="equals", value="Assignment submitted"
                    ),
                ],
                action=RuleAction(
                    activity_type="Produce", bloom_level="Create", is_active=True
                ),
            ),
            Rule(
                id="R03",
                name="Attempt Quiz",
                priority=3,
                conditions=[
                    RuleCondition(field="component", operator="equals", value="quiz"),
                    RuleCondition(
                        field="event_name", operator="contains", value="attempted"
                    ),
                ],
                action=RuleAction(
                    activity_type="Assess", bloom_level="Understand", is_active=True
                ),
            ),
            Rule(
                id="R04",
                name="Forum Discussion",
                priority=4,
                conditions=[
                    RuleCondition(field="component", operator="equals", value="forum"),
                ],
                action=RuleAction(
                    activity_type="Discuss", bloom_level="Analyze", is_active=True
                ),
            ),
            Rule(
                id="R05",
                name="Submit Feedback",
                priority=5,
                conditions=[
                    RuleCondition(field="event_name", operator="contains", value="feedback")
                ],
                action=RuleAction(
                    activity_type="Feedback", bloom_level="Evaluate", is_active=True
                ),
            ),
        ]

    def classify(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Classify event using Bloom rules."""
        return self.engine.evaluate(event)

    def classify_batch(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify multiple events."""
        return [self.classify(event) for event in events]
