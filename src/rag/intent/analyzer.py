"""
Intent analysis module for the enhanced RAG system.
Determines query intent and extracts relevant entities based on configuration.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from src.rag.embeddings.models import EmbeddingModel

class IntentAnalyzer:
    """Analyzes queries to determine intent and extract entities."""
    
    def __init__(
        self,
        config_dir: str = "config",
        embedding_model: Optional[EmbeddingModel] = None
    ):
        """Initialize the intent analyzer.
        
        Args:
            config_dir: Directory containing configuration files
            embedding_model: Optional embedding model for semantic matching
        """
        self.config_dir = Path(config_dir)
        self.embedding_model = embedding_model
        
        # Load configurations
        self.intent_types = self._load_json("intent/intent_types.json")
        self.intent_examples = self._load_json("intent/intent_examples.json")
        self.entity_types = self._load_json("entities/entity_types.json")
        
        # Initialize example embeddings if model available
        self.example_embeddings = {}
        if self.embedding_model:
            self._initialize_example_embeddings()
    
    def _load_json(self, relative_path: str) -> Dict[str, Any]:
        """Load a JSON configuration file.
        
        Args:
            relative_path: Path relative to config directory
            
        Returns:
            Loaded configuration dictionary
        """
        file_path = self.config_dir / relative_path
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _initialize_example_embeddings(self):
        """Initialize embeddings for example queries if embedding model available."""
        for intent_type, examples in self.intent_examples["examples"].items():
            queries = [ex["query"] for ex in examples]
            if queries:  # Only compute if we have examples
                self.example_embeddings[intent_type] = self.embedding_model.embed(queries)
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze a query to determine intent and extract entities.
        
        Args:
            query: The query to analyze
            
        Returns:
            Dictionary containing:
            - intent_type: The determined intent type
            - confidence: Confidence score for the intent
            - entities: Extracted entities
            - complexity: Assessed query complexity
        """
        # Extract entities first as they help with intent matching
        entities = self._extract_entities(query)
        
        # Determine intent using available methods
        intent_type, confidence = self._determine_intent(query, entities)
        
        # Assess query complexity
        complexity = self._assess_complexity(query, intent_type, entities)
        
        return {
            "intent_type": intent_type,
            "confidence": confidence,
            "entities": entities,
            "complexity": complexity
        }
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from the query using configured patterns.
        
        Args:
            query: Query to extract entities from
            
        Returns:
            Dictionary of extracted entities by type
        """
        entities = {}
        query_lower = query.lower()
        
        for entity_type, config in self.entity_types["entity_types"].items():
            # Check for exact values first
            if "values" in config:
                for value in config["values"]:
                    if value.lower() in query_lower:
                        entities.setdefault(entity_type, []).append(value)
            
            # Check aliases
            if "aliases" in config:
                for alias, value in config["aliases"].items():
                    if alias.lower() in query_lower:
                        entities.setdefault(entity_type, []).append(value)
            
            # Apply regex patterns
            if "patterns" in config:
                for pattern in config["patterns"]:
                    matches = re.finditer(pattern, query, re.IGNORECASE)
                    for match in matches:
                        matched_text = match.group(0)
                        # Don't add if we already found this value
                        if entity_type not in entities or matched_text not in entities[entity_type]:
                            entities.setdefault(entity_type, []).append(matched_text)
        
        return entities
    
    def _determine_intent(
        self,
        query: str,
        entities: Dict[str, List[str]]
    ) -> Tuple[str, float]:
        """Determine the query intent using pattern matching and embeddings.
        
        Args:
            query: The query to analyze
            entities: Previously extracted entities
            
        Returns:
            Tuple of (intent_type, confidence_score)
        """
        # First try rule-based matching
        intent_match = self._match_intent_rules(query, entities)
        if intent_match:
            return intent_match
        
        # If we have an embedding model, try semantic matching
        if self.embedding_model and self.example_embeddings:
            return self._match_intent_semantic(query)
        
        # Fall back to general query with low confidence
        return ("general_query", 0.5)
    
    def _match_intent_rules(
        self,
        query: str,
        entities: Dict[str, List[str]]
    ) -> Optional[Tuple[str, float]]:
        """Match intent using rule-based approach.
        
        Args:
            query: The query to analyze
            entities: Previously extracted entities
            
        Returns:
            Tuple of (intent_type, confidence_score) or None if no match
        """
        query_lower = query.lower()
        
        # Check for comparison intent
        if "comparison_targets" in entities or any(x in query_lower for x in ["compare", "vs", "versus"]):
            return ("comparative_analysis", 0.9)
        
        # Check for causal analysis
        if "effect" in entities and "time_period" in entities:
            return ("causal_analysis", 0.9)
        
        # Check for recommendation
        if "objective" in entities or query_lower.startswith(("how can", "what should", "suggest")):
            return ("recommendation", 0.9)
        
        # Check for metric trend
        if "metric" in entities:
            if any(x in query_lower for x in ["trend", "over time", "changed", "history"]):
                return ("metric_trend", 0.9)
        
        # Check for category analysis
        if "category" in entities:
            return ("category_analysis", 0.8)
        
        return None
    
    def _match_intent_semantic(self, query: str) -> Tuple[str, float]:
        """Match intent using semantic similarity to examples.
        
        Args:
            query: The query to analyze
            
        Returns:
            Tuple of (intent_type, confidence_score)
        """
        query_embedding = self.embedding_model.embed(query)
        
        best_score = -1
        best_intent = "general_query"
        
        for intent_type, examples_embedding in self.example_embeddings.items():
            # Compute similarities to all examples of this intent
            similarities = np.dot(examples_embedding, query_embedding)
            max_similarity = float(np.max(similarities))
            
            if max_similarity > best_score:
                best_score = max_similarity
                best_intent = intent_type
        
        # Convert similarity score to confidence (similarity is in [-1, 1])
        confidence = (best_score + 1) / 2  # Convert to [0, 1]
        
        return (best_intent, confidence)
    
    def _assess_complexity(
        self,
        query: str,
        intent_type: str,
        entities: Dict[str, List[str]]
    ) -> str:
        """Assess the complexity of the query.
        
        Args:
            query: The query to analyze
            intent_type: Determined intent type
            entities: Extracted entities
            
        Returns:
            Complexity level: "simple", "medium", or "complex"
        """
        # Count entities
        entity_count = sum(len(values) for values in entities.values())
        
        # Check for multiple time periods
        has_multiple_times = len(entities.get("time_period", [])) > 1
        
        # Check for complex intents
        complex_intents = ["comparative_analysis", "causal_analysis"]
        
        if intent_type in complex_intents or entity_count > 3 or has_multiple_times:
            return "complex"
        elif entity_count > 1:
            return "medium"
        else:
            return "simple"
