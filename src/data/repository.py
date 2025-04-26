from typing import List
from .models import LiveOpsChange, MetricMeasurement

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
