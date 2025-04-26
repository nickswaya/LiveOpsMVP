from typing import List, Dict, Any
from datetime import datetime
from src.data.repository import KnowledgeRepository

class IndexBuilder:
    def __init__(self, knowledge_repo: KnowledgeRepository):
        self.knowledge_repo = knowledge_repo
        self.category_index = {}
        self.metric_impact_index = {}
        self.temporal_index = []
        self.tag_index = {}
        
        # Build all indexes
        self.build_all_indexes()
    
    def build_all_indexes(self):
        """Build all indexes for the knowledge repository."""
        self.build_category_index()
        self.build_metric_impact_index()
        self.build_temporal_index()
        self.build_tag_index()
    
    def build_category_index(self):
        """Build index for fast retrieval by category."""
        self.category_index = {}
        for i, change in enumerate(self.knowledge_repo.changes):
            if change.category not in self.category_index:
                self.category_index[change.category] = []
            self.category_index[change.category].append(i)
    
    def build_metric_impact_index(self):
        """Build index for fast retrieval by metric impact."""
        self.metric_impact_index = {
            "increase": {metric: [] for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]},
            "decrease": {metric: [] for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]},
            "neutral": {metric: [] for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]}
        }
        
        for i, change in enumerate(self.knowledge_repo.changes):
            for metric, impact in change.expected_impact.items():
                self.metric_impact_index[impact][metric].append(i)
    
    def build_temporal_index(self):
        """Build index for temporal analysis."""
        # Sort changes by timestamp
        self.temporal_index = sorted(
            range(len(self.knowledge_repo.changes)),
            key=lambda i: self.knowledge_repo.changes[i].timestamp
        )
        
        # Create weekly buckets for time-series analysis
        self.weekly_buckets = {}
        for i, change in enumerate(self.knowledge_repo.changes):
            # Get year and week number
            year_week = change.timestamp.strftime("%Y-%U")
            if year_week not in self.weekly_buckets:
                self.weekly_buckets[year_week] = []
            self.weekly_buckets[year_week].append(i)
    
    def build_tag_index(self):
        """Build index for tag-based retrieval."""
        self.tag_index = {}
        for i, change in enumerate(self.knowledge_repo.changes):
            for tag in change.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                self.tag_index[tag].append(i)
    
    def search_by_category(self, category: str) -> List[Dict]:
        """Find changes by exact category match."""
        if category not in self.category_index:
            return []
        
        results = []
        for idx in self.category_index[category]:
            change = self.knowledge_repo.changes[idx]
            metrics = self.knowledge_repo.get_metrics_for_change(change.change_id)
            results.append({
                "change": change,
                "metrics": metrics
            })
        
        return results
    
    def search_by_tag(self, tag: str) -> List[Dict]:
        """Find changes by tag."""
        if tag not in self.tag_index:
            return []
        
        results = []
        for idx in self.tag_index[tag]:
            change = self.knowledge_repo.changes[idx]
            metrics = self.knowledge_repo.get_metrics_for_change(change.change_id)
            results.append({
                "change": change,
                "metrics": metrics
            })
        
        return results
    
    def search_by_metric_impact(self, metric: str, impact: str) -> List[Dict]:
        """Find changes by expected impact on a specific metric."""
        if impact not in self.metric_impact_index or metric not in self.metric_impact_index[impact]:
            return []
        
        results = []
        for idx in self.metric_impact_index[impact][metric]:
            change = self.knowledge_repo.changes[idx]
            metrics = self.knowledge_repo.get_metrics_for_change(change.change_id)
            results.append({
                "change": change,
                "metrics": metrics
            })
        
        return results
    
    def search_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Find changes within a date range."""
        results = []
        for idx in self.temporal_index:
            change = self.knowledge_repo.changes[idx]
            if start_date <= change.timestamp <= end_date:
                metrics = self.knowledge_repo.get_metrics_for_change(change.change_id)
                results.append({
                    "change": change,
                    "metrics": metrics
                })
            elif change.timestamp > end_date:
                # Since temporal_index is sorted, we can break early
                break
        
        return results
