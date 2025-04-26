from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.data.repository import KnowledgeRepository
from src.llm.service import LLMService
from src.rag.indexing.indexes import IndexBuilder
from src.rag.domain_knowledge.context import DomainKnowledgeManager
from src.rag.analysis.analyzer import ChangeAnalyzer

class EnhancedRAGSystem:
    def __init__(self, knowledge_repo: KnowledgeRepository, llm_service: Optional[LLMService] = None):
        """Initialize the RAG system with a knowledge repository and optional LLM service."""
        self.knowledge_repo = knowledge_repo
        self.llm_service = llm_service
        
        # Initialize components
        self.index_builder = IndexBuilder(knowledge_repo)
        self.domain_manager = DomainKnowledgeManager()
        self.analyzer = ChangeAnalyzer(
            knowledge_repo,
            self.index_builder,
            self.domain_manager,
            llm_service
        )
        
        # Initialize TF-IDF components
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._build_embeddings()
    
    def _build_embeddings(self):
        """Build TF-IDF embeddings for all changes."""
        documents = [change.description for change in self.knowledge_repo.changes]
        if documents:
            self.embeddings = self.vectorizer.fit_transform(documents)
        else:
            # Handle empty repository case
            self.embeddings = None
    
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
                self.domain_manager.domain_context,  # Pass the full domain context
                context_data
            )
        else:
            # Fallback to basic insights
            return self._generate_basic_insight(intent, context_data)
    
    def _determine_query_intent(self, query: str) -> Dict[str, Any]:
        """Determine the intent of a query."""
        query_lower = query.lower()
        intent = {"type": "general_query", "params": {}}
        
        # Check for category analysis intent
        for category in set(change.category for change in self.knowledge_repo.changes):
            if category.lower() in query_lower:
                intent = {
                    "type": "category_analysis",
                    "params": {"category": category}
                }
                return intent
        
        # Check for metric trend intent
        for metric in ["revenue", "dau", "retention", "session_length", "conversion_rate"]:
            if metric in query_lower:
                intent = {
                    "type": "metric_trend",
                    "params": {"metric": metric}
                }
                return intent
        
        # Default to general query
        return intent
    
    def _retrieve_context_for_intent(self, intent: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Retrieve context data based on query intent."""
        context_data = {}
        
        if intent["type"] == "category_analysis" and "category" in intent["params"]:
            category = intent["params"]["category"]
            context_data["category_changes"] = self.search_by_category(category)
            context_data["category_performance"] = self.analyze_category_performance(category)
        
        elif intent["type"] == "metric_trend" and "metric" in intent["params"]:
            metric = intent["params"]["metric"]
            context_data["metric_trends"] = self.analyze_metric_trends(metric)
        
        # Add similar changes for any query type
        similar_changes = self.search_similar_changes(query)
        if similar_changes:
            context_data["similar_changes"] = similar_changes
        
        return context_data
    
    def _generate_basic_insight(self, intent: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Generate a basic insight without using LLM."""
        if intent["type"] == "category_analysis" and "category_performance" in context_data:
            category = intent["params"]["category"]
            performance = context_data["category_performance"]
            
            if "metrics_stats" in performance:
                metrics_text = []
                for metric, stats in performance["metrics_stats"].items():
                    direction = "increased" if stats["average"] > 0 else "decreased"
                    metrics_text.append(f"{metric} {direction} by an average of {abs(stats['average']):.2f}%")
                
                return f"Analysis of {category} changes:\n\n" + "\n".join(metrics_text)
        
        elif intent["type"] == "metric_trend" and "metric_trends" in context_data:
            metric = intent["params"]["metric"]
            trends = context_data["metric_trends"]
            
            if "trend_analysis" in trends:
                trend_text = []
                for week_data in trends["trend_analysis"]:
                    trend_text.append(f"Week {week_data['week']}: {week_data['avg_percent_change']:.2f}% change")
                
                return f"Trend analysis for {metric}:\n\n" + "\n".join(trend_text)
        
        # Default response
        return "To get detailed insights, please configure the LLM service by setting the API key."
    
    def analyze_change_impact(self, change_id: str) -> Dict:
        """Analyze the impact of a specific change."""
        return self.analyzer.analyze_change_impact(change_id)
    
    def analyze_metric_trends(self, metric_name: str, weeks: int = 4) -> Dict:
        """Analyze trends for a specific metric."""
        return self.analyzer.analyze_metric_trends(metric_name, weeks)
    
    def analyze_category_performance(self, category: str) -> Dict:
        """Analyze the performance of a category of changes."""
        return self.analyzer.analyze_category_performance(category)
    
    def search_by_category(self, category: str) -> List[Dict]:
        """Find changes by category."""
        return self.index_builder.search_by_category(category)
    
    def search_by_tag(self, tag: str) -> List[Dict]:
        """Find changes by tag."""
        return self.index_builder.search_by_tag(tag)
    
    def search_by_metric_impact(self, metric: str, impact: str) -> List[Dict]:
        """Find changes by metric impact."""
        return self.index_builder.search_by_metric_impact(metric, impact)
    
    def search_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Find changes within a date range."""
        return self.index_builder.search_by_date_range(start_date, end_date)
    
    def get_domain_context(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant domain context for a query."""
        return self.domain_manager.get_context_for_query(query, intent)
