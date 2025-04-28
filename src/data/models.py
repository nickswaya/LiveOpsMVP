from datetime import datetime
from typing import List, Dict, Optional, Any

class LiveOpsChange:
    def __init__(
        self,
        change_id: str,
        timestamp: datetime,
        category: str,
        description: str,
        expected_impact: Dict[str, str],
        config_diff: Optional[Dict] = None,
        tags: List[str] = []
    ):
        self.change_id = change_id
        self.timestamp = timestamp
        self.category = category  # e.g., "Sale", "Event", "Feature Update"
        self.description = description
        self.expected_impact = expected_impact  # e.g., {"revenue": "increase", "retention": "neutral"}
        self.config_diff = config_diff  # Will store actual diff when available
        self.tags = tags
        self.vector_embedding = None  # Will be populated by the embedding model
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the change to a dictionary for serialization."""
        return {
            "change_id": self.change_id,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "description": self.description,
            "expected_impact": self.expected_impact,
            "config_diff": self.config_diff,
            "tags": self.tags
        }

class MetricMeasurement:
    def __init__(
        self,
        change_id: str,
        metric_name: str,
        before_value: float,
        after_value: float,
        timestamp: Optional[datetime] = None,
        time_window: str = "24h"  # Time window for before/after comparison
    ):
        self.change_id = change_id
        self.metric_name = metric_name
        self.before_value = before_value
        self.after_value = after_value
        self.timestamp = timestamp or datetime.now()
        self.time_window = time_window
        self.value = after_value  # Current value for trend analysis
        self.percent_change = self._calculate_percent_change()
        
    def _calculate_percent_change(self) -> float:
        if self.before_value == 0:
            return float('inf') if self.after_value > 0 else 0
        return ((self.after_value - self.before_value) / self.before_value) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the measurement to a dictionary for serialization."""
        return {
            "change_id": self.change_id,
            "metric_name": self.metric_name,
            "before_value": self.before_value,
            "after_value": self.after_value,
            "timestamp": self.timestamp.isoformat(),
            "time_window": self.time_window,
            "value": self.value,
            "percent_change": self.percent_change
        }
