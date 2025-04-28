from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from src.data.repository import KnowledgeRepository
from src.llm.service import LLMService
from src.llm.token_counter import TokenCounter
from src.rag.indexing.indexes import IndexBuilder
from src.rag.domain_knowledge.context import DomainKnowledgeManager
from src.rag.analysis.analyzer import ChangeAnalyzer
from src.rag.intent.analyzer import IntentAnalyzer
from src.rag.context.selector import ContextSelector
from src.rag.embeddings.models import create_embedding_model

class EnhancedRAGSystem:
    def __init__(
        self,
        knowledge_repo: KnowledgeRepository,
        llm_service: Optional[LLMService] = None,
        config_dir: str = "config"
    ):
        """Initialize the RAG system with a knowledge repository and optional LLM service.
        
        Args:
            knowledge_repo: Repository containing changes and metrics
            llm_service: Optional LLM service for generating insights
            config_dir: Directory containing configuration files
        """
        self.knowledge_repo = knowledge_repo
        self.llm_service = llm_service
        self.config_dir = config_dir
        
        # Initialize embedding model
        self.embedding_model = create_embedding_model("local", "all-MiniLM-L6-v2")
        
        # Initialize components
        self.index_builder = IndexBuilder(knowledge_repo)
        self.domain_manager = DomainKnowledgeManager()
        self.analyzer = ChangeAnalyzer(
            knowledge_repo,
            self.index_builder,
            self.domain_manager,
            llm_service
        )
        
        # Initialize Phase 2 components
        self.intent_analyzer = IntentAnalyzer(
            config_dir=config_dir,
            embedding_model=self.embedding_model
        )
        # Initialize context selector with reference to self
        context_selector = ContextSelector(
            knowledge_repo=knowledge_repo,
            index_builder=self.index_builder,
            domain_manager=self.domain_manager,
            config_dir=config_dir,
            token_counter=llm_service.token_counter if llm_service else None
        )
        context_selector.rag_system = self
        self.context_selector = context_selector
    
    def generate_insight(self, query: str) -> str:
        """Generate an insight based on a natural language query with enhanced context.
        
        Args:
            query: The query to analyze
            
        Returns:
            Generated insight based on the query and context
        """
        # Analyze query intent
        intent_analysis = self.intent_analyzer.analyze(query)
        
        # Select relevant context based on intent
        context = self.context_selector.select_context(query, intent_analysis)
        
        # Use LLM if available
        if self.llm_service and self.llm_service.is_enabled:
            return self.llm_service.answer_query(
                query=query,
                intent_analysis=intent_analysis,
                context=context
            )
        else:
            return self._generate_basic_insight(intent_analysis, context)
    
    def _generate_basic_insight(
        self,
        intent_analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate a basic insight without using LLM.
        
        Args:
            intent_analysis: Results of intent analysis
            context: Selected context data
            
        Returns:
            Basic insight based on available data
        """
        intent_type = intent_analysis["intent_type"]
        
        if intent_type == "category_analysis" and "category_performance" in context:
            category = intent_analysis["entities"].get("category", [""])[0]
            performance = context["category_performance"]
            
            if "metrics_stats" in performance:
                metrics_text = []
                for metric, stats in performance["metrics_stats"].items():
                    direction = "increased" if stats["average"] > 0 else "decreased"
                    metrics_text.append(f"{metric} {direction} by an average of {abs(stats['average']):.2f}%")
                
                return f"Analysis of {category} changes:\n\n" + "\n".join(metrics_text)
        
        elif intent_type == "metric_trend" and "metric_history" in context:
            metric = intent_analysis["entities"].get("metric", [""])[0]
            history = context["metric_history"]
            
            if "trend_analysis" in history:
                trend_text = []
                for period in history["trend_analysis"]:
                    trend_text.append(f"{period['period']}: {period['percent_change']:.2f}% change")
                
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
    
    def search_similar_changes(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find changes similar to the query using semantic search.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of similar changes with their similarity scores
        """
        # Get query embedding
        query_embedding = self.embedding_model.embed(query)
        
        # Get embeddings for all changes
        changes = []
        for change in self.knowledge_repo.changes:
            if not hasattr(change, 'vector_embedding') or change.vector_embedding is None:
                # Generate embedding if not already present
                change.vector_embedding = self.embedding_model.embed(change.description)
            
            # Calculate similarity
            similarity = float(np.dot(query_embedding, change.vector_embedding))
            
            # Convert change to dictionary and get metrics
            change_dict = change.to_dict()
            metrics = self.knowledge_repo.get_metrics_for_change(change_dict["change_id"])
            
            changes.append({
                "change": {"change": change_dict},  # Match the expected structure in search.py
                "metrics": metrics,
                "similarity_score": similarity
            })
        
        # Sort by similarity and return top_k
        changes.sort(key=lambda x: x["similarity_score"], reverse=True)
        return changes[:top_k]
