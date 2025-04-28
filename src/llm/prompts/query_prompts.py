import datetime
from typing import Dict, Any
import json
import numpy as np


def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()  # Convert datetime to ISO format string
    elif isinstance(obj, np.float64):
        return float(obj)
    elif hasattr(obj, '__dict__'):
        return convert_to_serializable(obj.__dict__)
    else:
        return obj

def generate_query_prompt(
    query: str,
    intent_analysis: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a prompt for answering a natural language query.
    
    Args:
        query: The original query
        intent_analysis: Results of intent analysis including type, entities, etc.
        context: Selected and prioritized context data
        
    Returns:
        Prompt data for the LLM
    """
    # Build the prompt
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
            f"Answer the query: '{query}'. "
            f"This is a {intent_analysis['complexity']} complexity {intent_analysis['intent_type']} query. "
            f"Focus on providing specific, data-driven insights that directly address the question. "
            f"Consider all relevant context provided about our gaming domain, metrics, and live ops changes."
        )
    }
    
    return convert_to_serializable(prompt)

def generate_complex_query_prompt(
    query: str,
    intent_analysis: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a prompt for complex queries that span multiple intents.
    
    Args:
        query: The original query
        intent_analysis: Results of intent analysis including type, entities, etc.
        context: Selected and prioritized context data
        
    Returns:
        Prompt data for the LLM
    """
    # Build the prompt
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
            f"This is a {intent_analysis['complexity']} complexity {intent_analysis['intent_type']} query "
            f"that requires synthesizing multiple types of information: '{query}'. "
            f"Analyze the provided context thoroughly and provide a comprehensive answer that addresses all aspects. "
            f"Pay special attention to relationships between different metrics, changes, and time periods. "
            f"Consider the confidence level ({intent_analysis['confidence']:.0%}) when forming conclusions."
        )
    }
    
    return convert_to_serializable(prompt)
