from typing import Dict, Any, List

def generate_change_analysis_prompt(
    change_data: Dict[str, Any],
    domain_context: Dict[str, Any],
    confounding_factors: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate a prompt for analyzing a specific change."""
    prompt = {
        "change": {
            "category": change_data["category"],
            "description": change_data["description"],
            "timestamp": change_data["timestamp"],
            "tags": change_data["tags"],
            "expected_impact": change_data["expected_impact"]
        },
        "metrics_data": change_data["metrics_data"],
        "domain_context": {
            "category_context": domain_context.get("category_context", ""),
            "relevant_concepts": domain_context.get("relevant_concepts", {}),
            "metric_contexts": domain_context.get("metric_contexts", {})
        },
        "confounding_factors": confounding_factors,
        "analysis_request": (
            f"Analyze the impact of this {change_data['category']} change. "
            f"Determine if it achieved its expected outcomes and why. "
            f"Consider potential confounding factors and suggest improvements for similar future changes."
        )
    }
    
    return prompt

def generate_trend_analysis_prompt(
    query: str,
    intent_analysis: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a prompt for analyzing metric trends.
    
    Args:
        query: The original query
        intent_analysis: Results of intent analysis including type, entities, etc.
        context: Selected and prioritized context data
        
    Returns:
        Prompt data for the LLM
    """
    metric = intent_analysis["entities"].get("metric", [""])[0]
    time_period = intent_analysis["entities"].get("time_period", ["recent"])[0]
    
    prompt = {
        "query": query,
        "intent": {
            "type": intent_analysis["intent_type"],
            "confidence": intent_analysis["confidence"],
            "entities": intent_analysis["entities"],
            "complexity": intent_analysis["complexity"]
        },
        "context": context,
        "analysis_request": (
            f"Analyze trends in {metric} over the specified time period ({time_period}). "
            f"This is a {intent_analysis['complexity']} complexity analysis with {intent_analysis['confidence']:.0%} confidence "
            f"in the metric identification. Focus on:"
            f"\n1. Overall trend direction and magnitude"
            f"\n2. Significant changes or inflection points"
            f"\n3. Correlations with specific change types or events"
            f"\n4. Seasonal patterns and cyclical behavior"
            f"\n5. Recommendations based on observed patterns"
            f"\nProvide specific, data-driven insights that directly address the query: '{query}'"
        )
    }
    
    return prompt

def generate_category_analysis_prompt(
    query: str,
    intent_analysis: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a prompt for analyzing a category of changes.
    
    Args:
        query: The original query
        intent_analysis: Results of intent analysis including type, entities, etc.
        context: Selected and prioritized context data
        
    Returns:
        Prompt data for the LLM
    """
    category = intent_analysis["entities"].get("category", [""])[0]
    
    prompt = {
        "query": query,
        "intent": {
            "type": intent_analysis["intent_type"],
            "confidence": intent_analysis["confidence"],
            "entities": intent_analysis["entities"],
            "complexity": intent_analysis["complexity"]
        },
        "context": context,
        "analysis_request": (
            f"Analyze the overall performance of '{category}' changes based on the provided context. "
            f"This is a {intent_analysis['complexity']} complexity analysis with {intent_analysis['confidence']:.0%} confidence "
            f"in the category identification. Focus on:"
            f"\n1. Performance across different metrics"
            f"\n2. Patterns in successful vs unsuccessful changes"
            f"\n3. Temporal trends and seasonality"
            f"\n4. Recommendations for future changes in this category"
            f"\nProvide specific, data-driven insights that directly address the query: '{query}'"
        )
    }
    
    return prompt
