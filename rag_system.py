# rag_system.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from llm_service import LLMService

class RAGSystem:
    def __init__(self, knowledge_repo, llm_service=None):
        self.knowledge_repo = knowledge_repo
        self.vectorizer = TfidfVectorizer()
        # Create text representations of changes for embedding
        self.change_texts = [
            f"{change.category} {change.description} " + 
            " ".join([f"expected {k} {v}" for k, v in change.expected_impact.items()]) + 
            " " + " ".join(change.tags)
            for change in knowledge_repo.changes
        ]
        # Create the vector embeddings
        self.embeddings = self.vectorizer.fit_transform(self.change_texts)
        
        # Initialize LLM service if provided
        self.llm_service = llm_service
        
        
    def search_similar_changes(self, query: str, top_k: int = 5):
        """Find changes similar to the query."""
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
    
    def analyze_change_impact(self, change_id: str):
        """Analyze the impact of a specific change."""
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
        
        # Use LLM for enhanced analysis if available
        if self.llm_service and self.llm_service.is_enabled:
            metrics_data = {
                "expected_impact": change.expected_impact,
                "actual_impact": {
                    k: {
                        "percent_change": v["percent_change"],
                        "actual": v["actual"],
                        "matched_expectation": v["matched_expectation"]
                    } for k, v in impact_analysis.items()
                }
            }
            
            llm_analysis = self.llm_service.analyze_change_impact(
                change.description,
                json.dumps(metrics_data, indent=2)
            )
            
            return {
                "change": change,
                "impact_analysis": impact_analysis,
                "llm_analysis": llm_analysis
            }
        else:
            return {
                "change": change,
                "impact_analysis": impact_analysis
            }
    
    def generate_insight(self, query: str):
        """Generate an insight based on a natural language query."""
        # First, find relevant changes based on the query
        relevant_results = self.search_similar_changes(query, top_k=10)
        
        # If LLM is available, use it for enhanced insights
        if self.llm_service and self.llm_service.is_enabled:
            # Format data for the LLM
            changes_data = []
            for result in relevant_results:
                change = result["change"]
                metrics = result["metrics"]
                
                change_data = {
                    "change_id": change.change_id,
                    "category": change.category,
                    "description": change.description,
                    "timestamp": change.timestamp.strftime("%Y-%m-%d"),
                    "metrics": {}
                }
                
                for metric in metrics:
                    change_data["metrics"][metric.metric_name] = {
                        "before": metric.before_value,
                        "after": metric.after_value,
                        "percent_change": metric.percent_change
                    }
                
                changes_data.append(change_data)
            
            # Get insights from LLM
            return self.llm_service.generate_insight_from_query(query, json.dumps(changes_data, indent=2))
        else:
            # Fallback to rule-based insights if LLM is not available
            if "similar" in query.lower():
                # Extract key terms from query
                terms = query.lower().replace("similar", "").replace("like", "").strip()
                similar_changes = self.search_similar_changes(terms)
                
                insight = f"Found {len(similar_changes)} changes similar to '{terms}'.\n\n"
                for i, result in enumerate(similar_changes):
                    change = result["change"]
                    metrics = result["metrics"]
                    
                    # Find the most impacted metric
                    most_impacted = max(metrics, key=lambda m: abs(m.percent_change))
                    
                    insight += f"{i+1}. {change.description} ({change.category}) on {change.timestamp.strftime('%Y-%m-%d')}\n"
                    insight += f"   Impact: {most_impacted.metric_name} {'+' if most_impacted.percent_change > 0 else ''}{most_impacted.percent_change:.2f}%\n\n"
                
                return insight
            
            elif "impact" in query.lower():
                # Extract metric name from query
                metric_terms = ["revenue", "dau", "retention", "session", "conversion"]
                target_metric = next((m for m in metric_terms if m in query.lower()), None)
                
                if not target_metric:
                    return "Please specify which metric you're interested in (revenue, DAU, retention, session length, conversion rate)"
                
                # Map partial terms to full metric names
                metric_mapping = {
                    "revenue": "revenue",
                    "dau": "dau",
                    "retention": "retention",
                    "session": "session_length",
                    "conversion": "conversion_rate"
                }
                
                full_metric = metric_mapping[target_metric]
                
                # Find changes with the biggest positive impact on this metric
                top_changes = []
                for change in self.knowledge_repo.changes:
                    metrics = self.knowledge_repo.get_metrics_for_change(change.change_id)
                    for metric in metrics:
                        if metric.metric_name == full_metric:
                            top_changes.append((change, metric.percent_change))
                
                # Sort by impact
                top_changes.sort(key=lambda x: x[1], reverse=True)
                
                insight = f"Top changes impacting {full_metric}:\n\n"
                for change, impact in top_changes[:5]:
                    insight += f"- {change.description} ({change.category}): {'+' if impact > 0 else ''}{impact:.2f}%\n"
                
                return insight
            
            else:
                return "I can answer questions about similar changes or metric impacts. Try asking something like 'What changes are similar to BOGO sale?' or 'What changes had the biggest impact on revenue?'"