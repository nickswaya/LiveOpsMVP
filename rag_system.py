from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any, Optional

class EnhancedRAGSystem:
    def __init__(self, knowledge_repo, llm_service=None):
        self.knowledge_repo = knowledge_repo
        self.llm_service = llm_service
        
        # Initialize basic TF-IDF for simple retrieval
        self.vectorizer = TfidfVectorizer()
        self.change_texts = [
            f"{change.category} {change.description} " + 
            " ".join([f"expected {k} {v}" for k, v in change.expected_impact.items()]) + 
            " " + " ".join(change.tags)
            for change in knowledge_repo.changes
        ]
        self.embeddings = self.vectorizer.fit_transform(self.change_texts)
        
        # Create additional indexing structures
        self._build_category_index()
        self._build_metric_impact_index()
        self._build_temporal_index()
        self._build_tag_index()
        
        # Build domain knowledge context
        self._build_domain_context()
        
    def _build_category_index(self):
        """Build index for fast retrieval by category."""
        self.category_index = {}
        for i, change in enumerate(self.knowledge_repo.changes):
            if change.category not in self.category_index:
                self.category_index[change.category] = []
            self.category_index[change.category].append(i)
    
    def _build_metric_impact_index(self):
        """Build index for fast retrieval by metric impact."""
        self.metric_impact_index = {
            "increase": {metric: [] for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]},
            "decrease": {metric: [] for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]},
            "neutral": {metric: [] for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]}
        }
        
        for i, change in enumerate(self.knowledge_repo.changes):
            for metric, impact in change.expected_impact.items():
                self.metric_impact_index[impact][metric].append(i)
    
    def _build_temporal_index(self):
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
    
    def _build_tag_index(self):
        """Build index for tag-based retrieval."""
        self.tag_index = {}
        for i, change in enumerate(self.knowledge_repo.changes):
            for tag in change.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                self.tag_index[tag].append(i)
    
    def _build_domain_context(self):
        """Build domain context to improve LLM understanding."""
        # Define domain-specific concepts and their impacts
        self.domain_context = {
            "concepts": {
                "BOGO": "Buy One Get One Free offers typically drive higher conversion rates and immediate revenue but may decrease long-term ARPU.",
                "RTP": "Return To Player adjustments directly impact player win rates and session length. Increasing RTP typically improves retention at the cost of revenue per session.",
                "Cooldown": "Cooldown periods affect engagement frequency. Shorter cooldowns typically increase DAU but may decrease long-term retention.",
                "Featured Placement": "Moving content to featured positions typically increases visibility and short-term engagement.",
                "Sneek Peek": "Preview content that drives curiosity and short-term engagement, often used to test new concepts.",
                "Limited Time Event": "Creates urgency and typically drives strong short-term engagement and revenue spikes.",
                "VIP": "Features targeted at high-value players with strong monetization potential.",
                "A/B Test": "Experimental changes to measure impact before full deployment."
            },
            "category_contexts": {
                "Add Slot": "Adding new slot machines typically drives short-term engagement and can increase revenue if the theme and mechanics are appealing.",
                "Remove Slot": "Removing underperforming content can improve overall metrics by directing players to better performing games.",
                "RTP Adjustments": "RTP (Return To Player) is the percentage of wagers that are returned to players over time. Higher RTP is player-friendly but reduces margin.",
                "BOGO": "BOGO (Buy One Get One Free) offers are powerful conversion drivers but may reduce the perceived value of regular-priced items.",
                "Pearly Rush Event": "Collection-based event that drives engagement through completionist mechanics.",
                "Dealers Edge Event": "Table game focused event that appeals to a specific player segment interested in skill-based games."
            },
            "metric_contexts": {
                "revenue": "Direct monetization through in-app purchases. Primary business metric.",
                "dau": "Daily Active Users - measure of overall engagement and reach.",
                "retention": "Percentage of users who return after their first session. Critical for long-term success.",
                "session_length": "Time spent in-app per session. Indicator of engagement depth.",
                "conversion_rate": "Percentage of users who make a purchase. Key monetization efficiency metric."
            }
        }
    
    def search_similar_changes(self, query: str, top_k: int = 5) -> List[Dict]:
        """Find changes similar to the query using TF-IDF similarity."""
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.embeddings)[0]
        top_indices = np.argsort(-similarities)[:top_k]
        
        results = []
        for idx in top_indices:
            change = self.knowledge_repo.changes[idx]
            metrics = self.knowledge_repo.get_metrics_for_change(change.change_id)
            results.append({
                "change": change,
                "metrics": metrics,
                "similarity_score": similarities[idx]
            })
        
        return results
    
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
    
    def analyze_change_impact(self, change_id: str) -> Dict:
        """Analyze the impact of a specific change with enhanced context."""
        # Find the change
        change = next((c for c in self.knowledge_repo.changes if c.change_id == change_id), None)
        if not change:
            return {"error": "Change not found"}
        
        # Get metrics for this change
        metrics = self.knowledge_repo.get_metrics_for_change(change_id)
        
        # Analyze if expected impacts were achieved
        impact_analysis = {}
        for metric in metrics:
            expected = change.expected_impact.get(metric.metric_name, "neutral")
            
            # Determine if the actual change matched expectations
            actual = "neutral"
            if metric.percent_change > 5:
                actual = "increase"
            elif metric.percent_change < -5:
                actual = "decrease"
                
            impact_analysis[metric.metric_name] = {
                "expected": expected,
                "actual": actual,
                "percent_change": metric.percent_change,
                "before": metric.before_value,
                "after": metric.after_value,
                "matched_expectation": expected == actual or (expected == "neutral" and -5 <= metric.percent_change <= 5)
            }
        
        # Find changes made within 3 days before this change
        change_date = change.timestamp
        start_date = change_date - timedelta(days=3)
        end_date = change_date - timedelta(minutes=5)  # Just before this change
        recent_changes = self.search_by_date_range(start_date, end_date)
        
        # Find similar changes by category
        similar_category_changes = self.search_by_category(change.category)
        # Filter out the current change
        similar_category_changes = [r for r in similar_category_changes if r["change"].change_id != change_id]
        
        # Use LLM for enhanced analysis if available
        if self.llm_service and self.llm_service.is_enabled:
            # Prepare change data
            change_data = {
                "category": change.category,
                "description": change.description,
                "timestamp": change.timestamp.strftime("%Y-%m-%d %H:%M"),
                "tags": change.tags,
                "expected_impact": change.expected_impact,
                "metrics_data": {
                    m.metric_name: {
                        "before": m.before_value,
                        "after": m.after_value,
                        "percent_change": m.percent_change
                    } for m in metrics
                }
            }
            
            # Prepare domain context
            domain_context = {
                "category_context": self.domain_context["category_contexts"].get(change.category, ""),
                "relevant_concepts": {},
                "metric_contexts": self.domain_context["metric_contexts"]
            }
            
            # Add relevant concepts from domain knowledge
            for concept, description in self.domain_context["concepts"].items():
                if concept.lower() in change.description.lower() or concept.lower() in change.category.lower():
                    domain_context["relevant_concepts"][concept] = description
            
            # Prepare confounding factors information
            confounding_factors = []
            
            # Add recent changes as potential confounding factors
            if recent_changes:
                confounding_factors.append({
                    "type": "recent_changes",
                    "description": f"There were {len(recent_changes)} other changes made within 3 days before this change",
                    "changes": [{
                        "category": r["change"].category,
                        "description": r["change"].description,
                        "timestamp": r["change"].timestamp.strftime("%Y-%m-%d %H:%M")
                    } for r in recent_changes[:3]]
                })
            
            # Add historical performance data
            if similar_category_changes:
                # Calculate average metric impacts for similar changes
                avg_impacts = {}
                for metric_name in ["revenue", "dau", "retention", "session_length", "conversion_rate"]:
                    values = []
                    for r in similar_category_changes:
                        for m in r["metrics"]:
                            if m.metric_name == metric_name:
                                values.append(m.percent_change)
                    
                    if values:
                        avg_impacts[metric_name] = sum(values) / len(values)
                
                confounding_factors.append({
                    "type": "historical_performance",
                    "description": f"Found {len(similar_category_changes)} previous similar changes of category '{change.category}'",
                    "average_impacts": avg_impacts
                })
            
            # Get analysis from LLM
            llm_analysis = self.llm_service.analyze_change_impact(
                change_data,
                domain_context,
                confounding_factors
            )
            
            return {
                "change": change,
                "impact_analysis": impact_analysis,
                "recent_changes": [r["change"] for r in recent_changes],
                "similar_changes": [r["change"] for r in similar_category_changes[:5]],
                "llm_analysis": llm_analysis
            }
        else:

            return {
                "change": change,
                "impact_analysis": impact_analysis,
                "recent_changes": [r["change"] for r in recent_changes],
                "similar_changes": [r["change"] for r in similar_category_changes[:5]]
            }
    
    def analyze_metric_trends(self, metric_name: str, weeks: int = 4) -> Dict:
        """Analyze trends for a specific metric over time."""
        # Get all changes sorted by time
        all_changes = [(i, self.knowledge_repo.changes[i]) for i in self.temporal_index]
        
        # Group by week
        weekly_data = {}
        for i, change in all_changes:
            week = change.timestamp.strftime("%Y-%U")
            if week not in weekly_data:
                weekly_data[week] = {
                    "changes": [],
                    "metric_values": [],
                    "percent_changes": []
                }
            
            # Get metrics for this change
            metrics = self.knowledge_repo.get_metrics_for_change(change.change_id)
            metric = next((m for m in metrics if m.metric_name == metric_name), None)
            
            if metric:
                weekly_data[week]["changes"].append(change)
                weekly_data[week]["metric_values"].append(metric.after_value)
                weekly_data[week]["percent_changes"].append(metric.percent_change)
        
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
                        "category": top_change.category,
                        "description": top_change.description,
                        "percent_change": data["percent_changes"][top_change_idx]
                    }
                })
        
        # Use LLM to generate insights if available
        if self.llm_service and self.llm_service.is_enabled:
            prompt = {
                "metric_name": metric_name,
                "metric_context": self.domain_context["metric_contexts"].get(metric_name, ""),
                "trend_data": trend_analysis,
                "analysis_request": f"Analyze trends in {metric_name} over the past {weeks} weeks. Identify patterns, correlations with specific change types, and provide actionable insights."
            }
            
            trend_insight = self.llm_service.generate_response(
                prompt=json.dumps(prompt, indent=2),
                system_prompt=f"You are an analytics expert for a mobile gaming company. Analyze {metric_name} trends and provide insights."
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
        category_changes = self.search_by_category(category)
        
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
                metrics_impact[metric.metric_name].append(metric.percent_change)
        
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
                "category_context": self.domain_context["category_contexts"].get(category, ""),
                "metrics_stats": metrics_stats,
                "sample_changes": [
                    {
                        "description": r["change"].description,
                        "metrics": {m.metric_name: m.percent_change for m in r["metrics"]}
                    } for r in category_changes[:5]
                ],
                "analysis_request": f"Analyze the overall performance of '{category}' changes. Identify which metrics are most impacted, any patterns in successful vs unsuccessful changes, and provide recommendations."
            }
            
            category_insight = self.llm_service.generate_response(
                prompt=json.dumps(prompt, indent=2),
                system_prompt=f"You are an analytics expert for a mobile gaming company. Analyze the performance of {category} changes and provide insights."
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
    
    def generate_insight(self, query: str) -> str:
        """Generate an insight based on a natural language query with enhanced context."""
        # Determine query intent
        intent = self._determine_query_intent(query)
        
        # Retrieve relevant data based on intent
        context_data = self._retrieve_context_for_intent(intent, query)
        
        # Use LLM if available
        if self.llm_service and self.llm_service.is_enabled:
            # Get answer from LLM using our structured prompt
            return self.llm_service.answer_query(
                query,
                intent,
                self.domain_context,  # Pass the full domain context
                context_data
            )
        else:
            # Fallback to basic insights
            return self._generate_basic_insight(intent, context_data)
    
    def _determine_query_intent(self, query: str) -> Dict:
        """Determine the intent of a natural language query."""
        # Simple rule-based intent detection
        intent = {
            "type": "unknown",
            "params": {}
        }
        
        query_lower = query.lower()
        
        # Check for category analysis intent
        for category in self.category_index.keys():
            if category.lower() in query_lower:
                intent["type"] = "category_analysis"
                intent["params"]["category"] = category
                break
        
        # Check for metric analysis intent
        for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]:
            if metric.lower() in query_lower or metric.lower().replace("_", " ") in query_lower:
                if "trend" in query_lower or "over time" in query_lower:
                    intent["type"] = "metric_trend"
                    intent["params"]["metric"] = metric
                else:
                    intent["type"] = "metric_impact"
                    intent["params"]["metric"] = metric
                break
        
        # Check for similarity search intent
        if "similar" in query_lower or "like" in query_lower:
            intent["type"] = "similarity_search"
            # Extract the search term (simple approach)
            if "similar to" in query_lower:
                intent["params"]["term"] = query_lower.split("similar to")[1].strip()
            elif "like" in query_lower:
                intent["params"]["term"] = query_lower.split("like")[1].strip()
            else:
                intent["params"]["term"] = query_lower
        
        # Check for time-based intent
        time_indicators = ["yesterday", "last week", "recent", "latest", "this month"]
        if any(indicator in query_lower for indicator in time_indicators):
            intent["type"] = "recent_changes"
            # Determine time range (simple approach)
            if "yesterday" in query_lower:
                intent["params"]["days"] = 1
            elif "last week" in query_lower:
                intent["params"]["days"] = 7
            elif "this month" in query_lower:
                intent["params"]["days"] = 30
            else:
                intent["params"]["days"] = 7  # Default
        
        return intent
    
    def _retrieve_context_for_intent(self, intent: Dict, query: str) -> Dict:
        """Retrieve context data based on query intent."""
        context_data = {}
        
        if intent["type"] == "category_analysis" and "category" in intent["params"]:
            category = intent["params"]["category"]
            results = self.search_by_category(category)
            
            # Build metrics summary
            metrics_impact = {metric: [] for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]}
            for result in results:
                for metric in result["metrics"]:
                    metrics_impact[metric.metric_name].append(metric.percent_change)
            
            context_data["category"] = category
            context_data["change_count"] = len(results)
            context_data["metrics_summary"] = {
                metric: {
                    "average": sum(impacts) / len(impacts) if impacts else 0,
                    "positive_rate": sum(1 for i in impacts if i > 0) / len(impacts) if impacts else 0
                } for metric, impacts in metrics_impact.items()
            }
            context_data["samples"] = [{
                "description": r["change"].description,
                "timestamp": r["change"].timestamp.strftime("%Y-%m-%d"),
                "metrics": {m.metric_name: m.percent_change for m in r["metrics"]}
            } for r in results[:5]]
        
        elif intent["type"] == "metric_impact" and "metric" in intent["params"]:
            metric = intent["params"]["metric"]
            
            # Find top performing changes for this metric
            all_metric_impacts = []
            for i, change in enumerate(self.knowledge_repo.changes):
                metrics = self.knowledge_repo.get_metrics_for_change(change.change_id)
                metric_obj = next((m for m in metrics if m.metric_name == metric), None)
                if metric_obj:
                    all_metric_impacts.append({
                        "change": change,
                        "impact": metric_obj.percent_change
                    })
            
            # Sort by impact
            all_metric_impacts.sort(key=lambda x: x["impact"], reverse=True)
            
            context_data["metric"] = metric
            context_data["top_performers"] = [{
                "category": item["change"].category,
                "description": item["change"].description,
                "impact": item["impact"]
            } for item in all_metric_impacts[:10]]
            
            # Group by category
            category_impacts = {}
            for item in all_metric_impacts:
                category = item["change"].category
                if category not in category_impacts:
                    category_impacts[category] = []
                category_impacts[category].append(item["impact"])
            
            # Calculate average by category
            context_data["category_performance"] = {
                category: sum(impacts) / len(impacts)
                for category, impacts in category_impacts.items()
            }
        
        elif intent["type"] == "metric_trend" and "metric" in intent["params"]:
            metric = intent["params"]["metric"]
            trend_data = self.analyze_metric_trends(metric)
            context_data = trend_data
        
        elif intent["type"] == "similarity_search" and "term" in intent["params"]:
            term = intent["params"]["term"]
            results = self.search_similar_changes(term)
            
            context_data["query_term"] = term
            context_data["results"] = [{
                "category": r["change"].category,
                "description": r["change"].description,
                "timestamp": r["change"].timestamp.strftime("%Y-%m-%d"),
                "metrics": {m.metric_name: m.percent_change for m in r["metrics"]},
                "similarity": r["similarity_score"]
            } for r in results]
        
        elif intent["type"] == "recent_changes" and "days" in intent["params"]:
            days = intent["params"]["days"]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            results = self.search_by_date_range(start_date, end_date)
            
            context_data["time_range"] = f"Last {days} days"
            context_data["change_count"] = len(results)
            context_data["changes"] = [{
                "category": r["change"].category,
                "description": r["change"].description,
                "timestamp": r["change"].timestamp.strftime("%Y-%m-%d"),
                "metrics": {m.metric_name: m.percent_change for m in r["metrics"]}
            } for r in results]
        
        else:
            # Default: basic similarity search
            results = self.search_similar_changes(query)
            
            context_data["query"] = query
            context_data["results"] = [{
                "category": r["change"].category,
                "description": r["change"].description,
                "timestamp": r["change"].timestamp.strftime("%Y-%m-%d"),
                "metrics": {m.metric_name: m.percent_change for m in r["metrics"]},
                "similarity": r["similarity_score"]
            } for r in results]
        
        return context_data
    
    def _generate_basic_insight(self, intent: Dict, context_data: Dict) -> str:
        """Generate a basic insight without LLM."""
        if intent["type"] == "category_analysis":
            category = context_data["category"]
            change_count = context_data["change_count"]
            
            insight = f"Analysis of {change_count} changes in category '{category}':\n\n"
            
            # Top metrics
            metrics_summary = context_data["metrics_summary"]
            top_metrics = sorted(metrics_summary.keys(), key=lambda m: metrics_summary[m]["average"], reverse=True)
            
            insight += "Top impacted metrics:\n"
            for metric in top_metrics[:3]:
                avg_impact = metrics_summary[metric]["average"]
                insight += f"- {metric}: {'+' if avg_impact > 0 else ''}{avg_impact:.2f}% on average\n"
            
            # Sample changes
            insight += "\nSample changes:\n"
            for sample in context_data["samples"][:3]:
                insight += f"- {sample['description']} ({sample['timestamp']})\n"
            
            return insight
        
        elif intent["type"] == "metric_impact":
            metric = context_data["metric"]
            top_performers = context_data["top_performers"]
            
            insight = f"Top changes impacting {metric}:\n\n"
            
            for i, performer in enumerate(top_performers[:5]):
                insight += f"{i+1}. {performer['category']}: {performer['description']}\n"
                insight += f"   Impact: {'+' if performer['impact'] > 0 else ''}{performer['impact']:.2f}%\n"
            
            # Add category insights
            category_performance = context_data["category_performance"]
            top_categories = sorted(category_performance.keys(), key=lambda c: category_performance[c], reverse=True)
            
            insight += "\nBest performing categories for this metric:\n"
            for category in top_categories[:3]:
                avg_impact = category_performance[category]
                insight += f"- {category}: {'+' if avg_impact > 0 else ''}{avg_impact:.2f}% on average\n"
            
            return insight
        
        elif intent["type"] == "metric_trend":
            metric = context_data["metric_name"]
            trend_analysis = context_data["trend_analysis"]
            
            insight = f"Trend analysis for {metric} over the past {len(trend_analysis)} weeks:\n\n"
            
            # Show trend data
            for week_data in trend_analysis:
                week = week_data["week"]
                avg_change = week_data["avg_percent_change"]
                top_change = week_data["top_change"]
                
                insight += f"Week {week}: {'+' if avg_change > 0 else ''}{avg_change:.2f}% average change\n"
                insight += f"  Top performer: {top_change['category']} - {top_change['description']}\n"
                insight += f"  Impact: {'+' if top_change['percent_change'] > 0 else ''}{top_change['percent_change']:.2f}%\n\n"
            
            return insight
        
        elif intent["type"] == "similarity_search":
            query_term = context_data["query_term"]
            results = context_data["results"]
            
            insight = f"Found {len(results)} changes similar to '{query_term}':\n\n"
            
            for i, result in enumerate(results[:5]):
                # Find the highest impact metric
                metrics = result["metrics"]
                if metrics:
                    top_metric = max(metrics.items(), key=lambda x: abs(x[1]))
                    metric_name, impact = top_metric
                else:
                    metric_name, impact = "unknown", 0
                    
                insight += f"{i+1}. {result['category']}: {result['description']} ({result['timestamp']})\n"
                insight += f"   Top impact: {metric_name} {'+' if impact > 0 else ''}{impact:.2f}%\n"
                insight += f"   Similarity score: {result['similarity']:.2f}\n\n"
            
            return insight
        
        elif intent["type"] == "recent_changes":
            time_range = context_data["time_range"]
            change_count = context_data["change_count"]
            changes = context_data["changes"]
            
            insight = f"Analysis of {change_count} changes in the {time_range}:\n\n"
            
            # Group by category
            category_counts = {}
            for change in changes:
                category = change["category"]
                if category not in category_counts:
                    category_counts[category] = 0
                category_counts[category] += 1
            
            # Top categories
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            
            insight += "Most frequent change types:\n"
            for category, count in top_categories[:3]:
                insight += f"- {category}: {count} changes\n"
            
            # Recent changes
            insight += "\nMost recent changes:\n"
            # Sort by timestamp (assuming they're strings in YYYY-MM-DD format)
            recent = sorted(changes, key=lambda x: x["timestamp"], reverse=True)
            for change in recent[:5]:
                # Find highest impact metric
                metrics = change["metrics"]
                if metrics:
                    top_metric = max(metrics.items(), key=lambda x: abs(x[1]))
                    metric_name, impact = top_metric
                    metric_info = f" ({metric_name} {'+' if impact > 0 else ''}{impact:.2f}%)"
                else:
                    metric_info = ""
                    
                insight += f"- {change['timestamp']}: {change['category']} - {change['description']}{metric_info}\n"
            
            return insight
        
        else:
            # Default for unknown intent
            query = context_data.get("query", "")
            results = context_data.get("results", [])
            
            insight = f"Results for '{query}':\n\n"
            
            for i, result in enumerate(results[:5]):
                insight += f"{i+1}. {result['category']}: {result['description']} ({result['timestamp']})\n"
                
                # Show top metrics
                metrics = result["metrics"]
                if metrics:
                    top_metrics = sorted(metrics.items(), key=lambda x: abs(x[1]), reverse=True)
                    insight += "   Top impacts:\n"
                    for metric, impact in top_metrics[:2]:
                        insight += f"   - {metric}: {'+' if impact > 0 else ''}{impact:.2f}%\n"
                
                insight += "\n"
            
            return insight