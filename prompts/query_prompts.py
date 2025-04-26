
def generate_query_prompt(query, intent, domain_context, context_data):
    """Generate a prompt for answering a natural language query."""
    
    # Build the relevant domain context
    relevant_domain_context = {}
    
    # Add relevant concepts
    concepts = domain_context.get("concepts", {})
    relevant_concepts = {}
    for concept, description in concepts.items():
        if concept.lower() in query.lower():
            relevant_concepts[concept] = description
    
    if relevant_concepts:
        relevant_domain_context["concepts"] = relevant_concepts
    
    # Add relevant category context
    categories = domain_context.get("category_contexts", {})
    relevant_categories = {}
    for category, description in categories.items():
        if category.lower() in query.lower() or (
            intent["type"] == "category_analysis" and 
            intent["params"].get("category") == category
        ):
            relevant_categories[category] = description
    
    if relevant_categories:
        relevant_domain_context["categories"] = relevant_categories
    
    # Add relevant metric context
    metrics = domain_context.get("metric_contexts", {})
    relevant_metrics = {}
    for metric, description in metrics.items():
        if metric.lower() in query.lower() or (
            intent["type"] in ["metric_impact", "metric_trend"] and 
            intent["params"].get("metric") == metric
        ):
            relevant_metrics[metric] = description
    
    if relevant_metrics:
        relevant_domain_context["metrics"] = relevant_metrics
    
    # Build the prompt
    prompt = {
        "query": query,
        "intent_type": intent["type"],
        "intent_params": intent["params"],
        "domain_context": relevant_domain_context,
        "context_data": context_data,
        "analysis_request": (
            f"Answer the query: '{query}'. "
            f"Focus on providing specific, data-driven insights that directly address the question. "
            f"Consider the relevant context about our gaming domain, metrics, and live ops changes."
        )
    }
    
    return prompt


def generate_complex_query_prompt(query, related_data, domain_context):
    """Generate a prompt for complex queries that span multiple intents."""
    
    prompt = {
        "query": query,
        "domain_context": domain_context,
        "data": related_data,
        "analysis_request": (
            f"This is a complex query that may require synthesizing multiple types of information: '{query}'. "
            f"Analyze the provided data thoroughly and provide a comprehensive answer that addresses all aspects. "
            f"Consider relationships between different metrics, changes, and time periods as needed."
        )
    }
    
    return prompt