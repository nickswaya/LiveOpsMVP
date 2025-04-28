from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import LiveOpsChange, MetricMeasurement

class KnowledgeRepository:
    def __init__(self):
        self.changes = []
        self.metrics = []
        
    def add_change(self, change: LiveOpsChange):
        """Add a change to the repository."""
        self.changes.append(change)
        
    def add_metric(self, metric: MetricMeasurement):
        """Add a metric measurement to the repository."""
        self.metrics.append(metric)
        
    def get_changes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all changes in a specific category."""
        changes = [change for change in self.changes if change.category == category]
        return [change.to_dict() for change in changes]
    
    def get_metrics_for_change(self, change_id: str) -> List[Dict[str, Any]]:
        """Get all metrics associated with a specific change."""
        metrics = [metric for metric in self.metrics if metric.change_id == change_id]
        return [metric.to_dict() for metric in metrics]
    
    def get_metric_history(
        self,
        metric_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get historical data for a specific metric within a date range.
        
        Args:
            metric_name: Name of the metric to get history for
            start_date: Start of the time period
            end_date: End of the time period
            
        Returns:
            Dictionary containing:
            - values: List of metric values
            - timestamps: List of measurement timestamps
            - trend_analysis: Basic trend analysis
        """
        # Get metrics within the time range
        metrics = [
            m for m in self.metrics
            if (
                m.metric_name == metric_name and
                start_date <= m.timestamp <= end_date
            )
        ]
        
        # Sort by timestamp
        metrics.sort(key=lambda x: x.timestamp)
        
        # Extract values and timestamps
        values = [m.value for m in metrics]
        timestamps = [m.timestamp.isoformat() for m in metrics]
        
        # Calculate basic trend analysis
        if values:
            first_value = values[0]
            last_value = values[-1]
            percent_change = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
            
            trend_analysis = {
                "start_value": first_value,
                "end_value": last_value,
                "percent_change": percent_change,
                "num_measurements": len(values)
            }
        else:
            trend_analysis = {
                "start_value": 0,
                "end_value": 0,
                "percent_change": 0,
                "num_measurements": 0
            }
        
        return {
            "values": values,
            "timestamps": timestamps,
            "trend_analysis": trend_analysis
        }
    
    def get_metrics_by_name(
        self,
        metric_name: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all measurements for a specific metric.
        
        Args:
            metric_name: Name of the metric to get
            limit: Optional limit on number of measurements to return
            
        Returns:
            List of metric measurement dictionaries
        """
        metrics = [m for m in self.metrics if m.metric_name == metric_name]
        metrics.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            metrics = metrics[:limit]
        return [metric.to_dict() for metric in metrics]
    
    def get_metrics_in_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get all metrics within a date range.
        
        Args:
            start_date: Start of the time period
            end_date: End of the time period
            
        Returns:
            List of metric measurement dictionaries
        """
        metrics = [
            m for m in self.metrics
            if start_date <= m.timestamp <= end_date
        ]
        return [metric.to_dict() for metric in metrics]
