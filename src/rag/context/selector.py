"""
Context selection module for the enhanced RAG system.
Selects and prioritizes context based on intent analysis and configuration rules.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.data.repository import KnowledgeRepository
from src.rag.indexing.indexes import IndexBuilder
from src.rag.domain_knowledge.context import DomainKnowledgeManager
from src.llm.token_counter import TokenCounter

class ContextSelector:
    """Selects and prioritizes context based on intent analysis."""
    
    def __init__(
        self,
        knowledge_repo: KnowledgeRepository,
        index_builder: IndexBuilder,
        domain_manager: DomainKnowledgeManager,
        config_dir: str = "config",
        token_counter: Optional[TokenCounter] = None
    ):
        """Initialize the context selector.
        
        Args:
            knowledge_repo: Repository containing changes and metrics
            index_builder: Index builder for searching changes
            domain_manager: Domain knowledge manager
            config_dir: Directory containing configuration files
            token_counter: Optional token counter for managing context size
        """
        self.knowledge_repo = knowledge_repo
        self.index_builder = index_builder
        self.domain_manager = domain_manager
        self.token_counter = token_counter or TokenCounter()
        
        # Load configuration
        config_path = Path(config_dir) / "context/selection_rules.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def select_context(
        self,
        query: str,
        intent_analysis: Dict[str, Any],
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Select context based on intent analysis and configuration rules.
        
        Args:
            query: Original query
            intent_analysis: Intent analysis results
            max_tokens: Optional maximum tokens for context
            
        Returns:
            Selected and prioritized context
        """
        intent_type = intent_analysis["intent_type"]
        entities = intent_analysis["entities"]
        complexity = intent_analysis["complexity"]
        
        # Get rules for this intent type
        intent_rules = self.config["context_rules"].get(
            intent_type,
            self.config["context_rules"]["general_query"]  # Fallback to general query rules
        )
        
        # Get default settings
        settings = self.config["default_settings"]
        max_tokens = max_tokens or settings["token_limits"]["max_total_tokens"]
        reserved_tokens = settings["token_limits"]["reserved_tokens"]
        available_tokens = max_tokens - reserved_tokens
        
        # Select context following priority order
        context = {}
        used_tokens = 0
        
        for context_type in intent_rules["priority_order"]:
            # Find the rule for this context type
            rule = next(r for r in intent_rules["rules"] if r["type"] == context_type)
            
            # Get context based on rule type
            context_data = self._get_context_for_rule(rule, intent_analysis)
            
            if context_data:
                # Estimate tokens for this context
                context_tokens = self._estimate_context_tokens(context_data)
                
                # Check if we can add this context
                if used_tokens + context_tokens <= available_tokens or rule["required"]:
                    context[context_type] = context_data
                    used_tokens += context_tokens
                
                # If we're over token limit and this isn't required, trim it
                if used_tokens > available_tokens and not rule["required"]:
                    context[context_type] = self._trim_context(
                        context_data,
                        available_tokens - (used_tokens - context_tokens)
                    )
                    used_tokens = available_tokens
        
        return context
    
    def _get_context_for_rule(
        self,
        rule: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> Any:
        """Get context data based on a specific rule.
        
        Args:
            rule: Rule configuration
            intent_analysis: Intent analysis results
            
        Returns:
            Context data for the rule
        """
        rule_type = rule["type"]
        entities = intent_analysis["entities"]
        
        if rule_type == "category_changes":
            return self._get_category_changes(rule, entities)
        
        elif rule_type == "metric_history":
            return self._get_metric_history(rule, entities)
        
        elif rule_type == "temporal_data":
            return self._get_temporal_data(rule, entities)
        
        elif rule_type == "comparison_data":
            return self._get_comparison_data(rule, entities)
        
        elif rule_type == "confounding_factors":
            return self._get_confounding_factors(rule, entities)
        
        elif rule_type == "domain_knowledge":
            return self._get_domain_knowledge(intent_analysis)
        
        elif rule_type == "similar_changes":
            return self._get_similar_changes(rule, intent_analysis)
        
        return None
    
    def _get_category_changes(
        self,
        rule: Dict[str, Any],
        entities: Dict[str, List[str]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Get recent changes for a category."""
        if "category" not in entities:
            return None
            
        category = entities["category"][0]
        time_window = self._parse_time_window(rule["time_window"])
        max_items = rule.get("max_items", 10)
        
        changes = self.index_builder.search_by_category(category)
        
        # Filter by time window and limit
        recent_changes = [
            change for change in changes
            if (change["change"].timestamp if isinstance(change, dict) else change.timestamp) >= time_window["start"]
        ][:max_items]
        
        # Convert changes to dictionaries for serialization
        serializable_changes = []
        for change in recent_changes:
            if isinstance(change, dict):
                # If it's already a dict with a LiveOpsChange object
                change_dict = change.copy()
                change_dict["change"] = change["change"].to_dict()
                serializable_changes.append(change_dict)
            else:
                # If it's a LiveOpsChange object directly
                serializable_changes.append({"change": change.to_dict()})
        
        return serializable_changes if serializable_changes else None
    
    def _get_metric_history(
        self,
        rule: Dict[str, Any],
        entities: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Get historical data for a metric."""
        if "metric" not in entities:
            return None
            
        metric = entities["metric"][0]
        time_window = self._parse_time_window(rule["time_window"])
        
        # Get metric data from repository
        metric_data = self.knowledge_repo.get_metric_history(
            metric,
            time_window["start"],
            time_window["end"]
        )
        
        return metric_data if metric_data else None
    
    def _get_temporal_data(
        self,
        rule: Dict[str, Any],
        entities: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Get data around a specific time period."""
        if "time_period" not in entities:
            return None
            
        # Parse time windows
        before_window = self._parse_time_window(rule["time_window_before"])
        after_window = self._parse_time_window(rule["time_window_after"])
        
        # Get changes and metrics for the period
        changes = self.index_builder.search_by_date_range(
            before_window["start"],
            after_window["end"]
        )
        
        if changes:
            # Convert changes to dictionaries for serialization
            serializable_changes = []
            for change in changes:
                if isinstance(change, dict):
                    change_dict = change.copy()
                    change_dict["change"] = change["change"].to_dict()
                    serializable_changes.append(change_dict)
                else:
                    serializable_changes.append({"change": change.to_dict()})
            
            return {"changes": serializable_changes}
        
        return None
    
    def _get_comparison_data(
        self,
        rule: Dict[str, Any],
        entities: Dict[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """Get data for comparing different items."""
        if "comparison_targets" not in entities:
            return None
            
        targets = entities["comparison_targets"]
        time_window = self._parse_time_window(rule["time_window"])
        metrics = rule.get("metrics", ["revenue", "dau", "retention"])
        
        comparison_data = {}
        for target in targets:
            # Get changes and metrics for this target
            changes = self.index_builder.search_by_category(target)
            
            # Convert changes to dictionaries for serialization
            serializable_changes = []
            for change in changes:
                if isinstance(change, dict):
                    change_dict = change.copy()
                    change_dict["change"] = change["change"].to_dict()
                    serializable_changes.append(change_dict)
                else:
                    serializable_changes.append({"change": change.to_dict()})
            
            metrics_data = {
                metric: self.knowledge_repo.get_metric_history(
                    metric,
                    time_window["start"],
                    time_window["end"]
                )
                for metric in metrics
            }
            comparison_data[target] = {
                "changes": serializable_changes,
                "metrics": metrics_data
            }
        
        return comparison_data if any(comparison_data.values()) else None
    
    def _get_confounding_factors(
        self,
        rule: Dict[str, Any],
        entities: Dict[str, List[str]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Get potential confounding factors."""
        time_window = self._parse_time_window(rule["time_window"])
        max_items = rule.get("max_items", 5)
        
        # Get all changes in the time window
        changes = self.index_builder.search_by_date_range(
            time_window["start"],
            time_window["end"]
        )
        
        # Filter to most impactful changes
        if changes:
            # Sort by the number of impacted metrics as a simple impact score
            changes.sort(
                key=lambda x: len(x["change"].expected_impact if isinstance(x, dict) else x.expected_impact),
                reverse=True
            )
            
            # Convert changes to dictionaries for serialization
            serializable_changes = []
            for change in changes[:max_items]:
                if isinstance(change, dict):
                    change_dict = change.copy()
                    change_dict["change"] = change["change"].to_dict()
                    serializable_changes.append(change_dict)
                else:
                    serializable_changes.append({"change": change.to_dict()})
            
            return serializable_changes
        
        return None
    
    def _get_domain_knowledge(
        self,
        intent_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get relevant domain knowledge."""
        return self.domain_manager.get_context_for_query(
            intent_analysis.get("query", ""),
            {
                "type": intent_analysis["intent_type"],
                "params": intent_analysis.get("entities", {})
            }
        )
    
    def _get_similar_changes(
        self,
        rule: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """Get similar changes based on the query."""
        max_items = rule.get("max_items", 5)
        similarity_threshold = rule.get("similarity_threshold", 0.7)
        
        # Use the RAG system's search_similar_changes method
        # Note: We'll need to pass this in from the RAG system
        if hasattr(self, "rag_system"):
            similar = self.rag_system.search_similar_changes(
                intent_analysis.get("query", ""),
                max_items
            )
        else:
            # Fallback to basic category search if RAG system not available
            category = next(
                (cat for cat in intent_analysis.get("entities", {}).get("category", []))
                if "category" in intent_analysis.get("entities", {})
                else None
            )
            if category:
                similar = self.index_builder.search_by_category(category)[:max_items]
            else:
                similar = []
        
        return similar if similar else None
    
    def _parse_time_window(self, window_spec: str) -> Dict[str, datetime]:
        """Parse a time window specification into start and end dates."""
        now = datetime.now()
        
        # Parse the number and unit from spec (e.g., "3 months")
        parts = window_spec.split()
        if len(parts) != 2:
            raise ValueError(f"Invalid time window specification: {window_spec}")
            
        number = int(parts[0])
        unit = parts[1].lower()
        
        # Calculate timedelta
        if unit in ["day", "days"]:
            delta = timedelta(days=number)
        elif unit in ["week", "weeks"]:
            delta = timedelta(weeks=number)
        elif unit in ["month", "months"]:
            # Approximate months as 30 days
            delta = timedelta(days=number * 30)
        elif unit in ["year", "years"]:
            # Approximate years as 365 days
            delta = timedelta(days=number * 365)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")
        
        return {
            "start": now - delta,
            "end": now
        }
    
    def _estimate_context_tokens(self, context_data: Any) -> int:
        """Estimate the number of tokens in a context item."""
        if isinstance(context_data, (str, int, float, bool)):
            return self.token_counter.estimate_tokens(str(context_data))
        elif isinstance(context_data, (list, tuple)):
            return sum(self._estimate_context_tokens(item) for item in context_data)
        elif isinstance(context_data, dict):
            return sum(
                self._estimate_context_tokens(key) + self._estimate_context_tokens(value)
                for key, value in context_data.items()
            )
        elif context_data is None:
            return 0
        else:
            # For other types, convert to string and estimate
            return self.token_counter.estimate_tokens(str(context_data))
    
    def _trim_context(self, context_data: Any, max_tokens: int) -> Any:
        """Trim context data to fit within token limit."""
        if isinstance(context_data, (str, int, float, bool)):
            return context_data
        elif isinstance(context_data, (list, tuple)):
            trimmed = []
            tokens = 0
            for item in context_data:
                item_tokens = self._estimate_context_tokens(item)
                if tokens + item_tokens <= max_tokens:
                    trimmed.append(item)
                    tokens += item_tokens
                else:
                    break
            return trimmed
        elif isinstance(context_data, dict):
            trimmed = {}
            tokens = 0
            for key, value in context_data.items():
                item_tokens = (
                    self._estimate_context_tokens(key) +
                    self._estimate_context_tokens(value)
                )
                if tokens + item_tokens <= max_tokens:
                    trimmed[key] = value
                    tokens += item_tokens
                else:
                    break
            return trimmed
        else:
            return context_data
