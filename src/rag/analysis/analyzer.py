from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from src.data.repository import KnowledgeRepository
from src.llm.service import LLMService
from src.rag.indexing.indexes import IndexBuilder
from src.rag.domain_knowledge.context import DomainKnowledgeManager

class ChangeAnalyzer:
    def __init__(
        self,
        knowledge_repo: KnowledgeRepository,
        index_builder: IndexBuilder,
        domain_manager: DomainKnowledgeManager,
        llm_service: Optional[LLMService] = None
    ):
        self.knowledge_repo = knowledge_repo
        self.index_builder = index_builder
        self.domain_manager = domain_manager
        self.llm_service = llm_service
    
    def analyze_change_impact(self, change_id: str) -> Dict:
        """Analyze the impact of a specific change with enhanced context."""
        # Find the change and convert to dictionary
        change = next((c for c in self.knowledge_repo.changes if c.change_id == change_id), None)
        if not change:
            return {"error": "Change not found"}
        
        # Convert change to dictionary
        change_dict = change.to_dict()
        
        # Get metrics for this change as dictionaries
        metrics = self.knowledge_repo.get_metrics_for_change(change_id)
        
        # Analyze if expected impacts were achieved
        impact_analysis = {}
        for metric in metrics:
            expected = change_dict["expected_impact"].get(metric["metric_name"], "neutral")
            
            # Determine if the actual change matched expectations
            actual = "neutral"
            if metric["percent_change"] > 5:
                actual = "increase"
            elif metric["percent_change"] < -5:
                actual = "decrease"
                
            impact_analysis[metric["metric_name"]] = {
                "expected": expected,
                "actual": actual,
                "percent_change": metric["percent_change"],
                "before": metric["before_value"],
                "after": metric["after_value"],
                "matched_expectation": expected == actual or (expected == "neutral" and -5 <= metric["percent_change"] <= 5)
            }
        
        # Find changes made within 3 days before this change
        change_date = datetime.fromisoformat(change_dict["timestamp"])
        start_date = change_date - timedelta(days=3)
        end_date = change_date - timedelta(minutes=5)  # Just before this change
        recent_changes = self.index_builder.search_by_date_range(start_date, end_date)
        
        # Find similar changes by category
        category_changes = self.index_builder.search_by_category(change_dict["category"])
        # Filter out the current change and ensure changes and metrics are dictionaries
        similar_category_changes = []
        for r in category_changes:
            # Skip the current change
            if (r["change"].change_id if hasattr(r["change"], "change_id") else r["change"]["change_id"]) == change_id:
                continue
            
            # Convert change to dictionary if needed
            similar_change_dict = r["change"].to_dict() if hasattr(r["change"], "to_dict") else r["change"]
            
            # Convert metrics to dictionaries if needed
            metrics_dicts = []
            for m in r["metrics"]:
                if hasattr(m, "to_dict"):
                    metrics_dicts.append(m.to_dict())
                else:
                    metrics_dicts.append(m)
            
            similar_category_changes.append({
                "change": similar_change_dict,
                "metrics": metrics_dicts
            })
        
        # Use LLM for enhanced analysis if available
        if self.llm_service and self.llm_service.is_enabled:
            # Change data is already in dictionary format
            change_data = {
                "category": change_dict["category"],
                "description": change_dict["description"],
                "timestamp": datetime.fromisoformat(change_dict["timestamp"]).strftime("%Y-%m-%d %H:%M"),
                "tags": change_dict["tags"],
                "expected_impact": change_dict["expected_impact"],
                "metrics_data": {
                    m["metric_name"]: {
                        "before": m["before_value"],
                        "after": m["after_value"],
                        "percent_change": m["percent_change"]
                    } for m in metrics
                }
            }
            
            # Get domain context
            domain_context = {
                "category_context": self.domain_manager.get_relevant_category_context(change_dict["category"]),
                "relevant_concepts": self.domain_manager.get_relevant_concepts(change_dict["description"]),
                "metric_contexts": self.domain_manager.domain_context["metric_contexts"]
            }
            
            # Prepare confounding factors information
            confounding_factors = []
            
            # Add recent changes as potential confounding factors
            if recent_changes:
                # Convert recent changes to dictionaries
                recent_changes_dicts = []
                for r in recent_changes[:3]:
                    if hasattr(r["change"], "to_dict"):
                        recent_change_dict = r["change"].to_dict()
                    else:
                        recent_change_dict = r["change"]
                    recent_changes_dicts.append({
                        "category": recent_change_dict["category"],
                        "description": recent_change_dict["description"],
                        "timestamp": datetime.fromisoformat(recent_change_dict["timestamp"]).strftime("%Y-%m-%d %H:%M")
                    })
                
                confounding_factors.append({
                    "type": "recent_changes",
                    "description": f"There were {len(recent_changes)} other changes made within 3 days before this change",
                    "changes": recent_changes_dicts
                })
            
            # Add historical performance data
            if similar_category_changes:
                # Calculate average metric impacts for similar changes
                avg_impacts = {}
                for metric_name in ["revenue", "dau", "retention", "session_length", "conversion_rate"]:
                    values = []
                    for r in similar_category_changes:
                        for m in r["metrics"]:
                            if m["metric_name"] == metric_name:
                                values.append(m["percent_change"])
                    
                    if values:
                        avg_impacts[metric_name] = sum(values) / len(values)
                
                confounding_factors.append({
                    "type": "historical_performance",
                    "description": f"Found {len(similar_category_changes)} previous similar changes of category '{change_dict['category']}'",
                    "average_impacts": avg_impacts
                })
            
            # Get analysis from LLM
            llm_analysis = self.llm_service.analyze_change_impact(
                change_data,
                domain_context,
                confounding_factors
            )
            
            return {
                "change": change_dict,
                "impact_analysis": impact_analysis,
                "recent_changes": [r["change"].to_dict() if hasattr(r["change"], "to_dict") else r["change"] for r in recent_changes],
                "similar_changes": [r["change"] for r in similar_category_changes[:5]],
                "llm_analysis": llm_analysis
            }
        else:
            return {
                "change": change_dict,
                "impact_analysis": impact_analysis,
                "recent_changes": [r["change"].to_dict() if hasattr(r["change"], "to_dict") else r["change"] for r in recent_changes],
                "similar_changes": [r["change"] for r in similar_category_changes[:5]]
            }
    
    def analyze_metric_trends(self, metric_name: str, weeks: int = 4) -> Dict:
        """Analyze trends for a specific metric over time."""
        # Get all changes sorted by time
        all_changes = [(i, self.knowledge_repo.changes[i]) for i in self.index_builder.temporal_index]
        
        # Group by week
        weekly_data = {}
        for i, change in all_changes:
            # Convert change to dictionary
            change_dict = change.to_dict()
            timestamp = datetime.fromisoformat(change_dict["timestamp"])
            week = timestamp.strftime("%Y-%U")
            if week not in weekly_data:
                weekly_data[week] = {
                    "changes": [],
                    "metric_values": [],
                    "percent_changes": []
                }
            
            # Get metrics as dictionaries
            metrics = self.knowledge_repo.get_metrics_for_change(change_dict["change_id"])
            metric = next((m for m in metrics if m["metric_name"] == metric_name), None)
            
            if metric:
                weekly_data[week]["changes"].append(change_dict)
                weekly_data[week]["metric_values"].append(metric["after_value"])
                weekly_data[week]["percent_changes"].append(metric["percent_change"])
        
        # Calculate weekly averages and identify top performing changes
        trend_analysis = []
        for week, data in sorted(weekly_data.items(), key=lambda x: x[0], reverse=True)[:weeks]:
            if data["metric_values"]:
                avg_value = sum(data["metric_values"]) / len(data["metric_values"])
                avg_percent_change = sum(data["percent_changes"]) / len(data["percent_changes"])
                
                # Find top performing change this week
                top_change_idx = data["percent_changes"].index(max(data["percent_changes"]))
                top_change = data["changes"][top_change_idx]
                
                trend_analysis.append({
                    "week": week,
                    "avg_value": avg_value,
                    "avg_percent_change": avg_percent_change,
                    "change_count": len(data["changes"]),
                    "top_change": {
                        "category": top_change["category"],
                        "description": top_change["description"],
                        "percent_change": data["percent_changes"][top_change_idx]
                    }
                })
        
        # Use LLM to generate insights if available
        if self.llm_service and self.llm_service.is_enabled:
            prompt = {
                "metric_name": metric_name,
                "metric_context": self.domain_manager.get_relevant_metric_context(metric_name),
                "trend_data": trend_analysis,
                "analysis_request": f"Analyze trends in {metric_name} over the past {weeks} weeks. Identify patterns, correlations with specific change types, and provide actionable insights."
            }
            
            trend_insight = self.llm_service.analyze_metric_trend(
                metric_name,
                trend_analysis,
                self.domain_manager.domain_context
            )
            
            return {
                "metric_name": metric_name,
                "trend_analysis": trend_analysis,
                "insight": trend_insight
            }
        else:
            return {
                "metric_name": metric_name,
                "trend_analysis": trend_analysis
            }
    
    def analyze_category_performance(self, category: str) -> Dict:
        """Analyze the overall performance of a specific category of changes."""
        # Get all changes of this category
        category_changes = self.index_builder.search_by_category(category)
        
        if not category_changes:
            return {"error": f"No changes found in category '{category}'"}
        
        # Calculate metrics impact statistics
        metrics_impact = {
            "revenue": [],
            "dau": [],
            "retention": [],
            "session_length": [],
            "conversion_rate": []
        }
        
        for result in category_changes:
            for metric in result["metrics"]:
                metrics_impact[metric["metric_name"]].append(metric["percent_change"])
        
        # Calculate statistics
        metrics_stats = {}
        for metric_name, impacts in metrics_impact.items():
            if impacts:
                metrics_stats[metric_name] = {
                    "average": sum(impacts) / len(impacts),
                    "min": min(impacts),
                    "max": max(impacts),
                    "positive_count": sum(1 for i in impacts if i > 0),
                    "negative_count": sum(1 for i in impacts if i < 0),
                    "neutral_count": sum(1 for i in impacts if -1 <= i <= 1),
                    "total_count": len(impacts)
                }
        
        # Use LLM to generate insights if available
        if self.llm_service and self.llm_service.is_enabled:
            prompt = {
                "category": category,
                "category_context": self.domain_manager.get_relevant_category_context(category),
                "metrics_stats": metrics_stats,
                "sample_changes": [
                    {
                        "description": r["change"]["description"] if isinstance(r["change"], dict) else r["change"].to_dict()["description"],
                        "metrics": {m["metric_name"]: m["percent_change"] for m in r["metrics"]}
                    } for r in category_changes[:5]
                ],
                "analysis_request": f"Analyze the overall performance of '{category}' changes. Identify which metrics are most impacted, any patterns in successful vs unsuccessful changes, and provide recommendations."
            }
            
            category_insight = self.llm_service.analyze_category(
                category,
                metrics_stats,
                prompt["sample_changes"],
                self.domain_manager.domain_context
            )
            
            return {
                "category": category,
                "metrics_stats": metrics_stats,
                "change_count": len(category_changes),
                "insight": category_insight
            }
        else:
            return {
                "category": category,
                "metrics_stats": metrics_stats,
                "change_count": len(category_changes)
            }
