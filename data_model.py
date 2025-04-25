from datetime import datetime
import pandas as pd
import numpy as np
from typing import List, Dict, Optional

# Define the core data structures
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

class MetricMeasurement:
    def __init__(
        self,
        change_id: str,
        metric_name: str,
        before_value: float,
        after_value: float,
        time_window: str = "24h"  # Time window for before/after comparison
    ):
        self.change_id = change_id
        self.metric_name = metric_name
        self.before_value = before_value
        self.after_value = after_value
        self.time_window = time_window
        self.percent_change = self._calculate_percent_change()
        
    def _calculate_percent_change(self) -> float:
        if self.before_value == 0:
            return float('inf') if self.after_value > 0 else 0
        return ((self.after_value - self.before_value) / self.before_value) * 100

class KnowledgeRepository:
    def __init__(self):
        self.changes = []
        self.metrics = []
        
    def add_change(self, change: LiveOpsChange):
        self.changes.append(change)
        
    def add_metric(self, metric: MetricMeasurement):
        self.metrics.append(metric)
        
    def get_changes_by_category(self, category: str) -> List[LiveOpsChange]:
        return [change for change in self.changes if change.category == category]
    
    def get_metrics_for_change(self, change_id: str) -> List[MetricMeasurement]:
        return [metric for metric in self.metrics if metric.change_id == change_id]