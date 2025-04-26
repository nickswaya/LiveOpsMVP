
def generate_change_analysis_prompt(change_data, domain_context, confounding_factors):
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


def generate_trend_analysis_prompt(metric_name, trend_data, domain_context):
    """Generate a prompt for analyzing metric trends."""
    prompt = {
        "metric_name": metric_name,
        "metric_context": domain_context.get("metric_contexts", {}).get(metric_name, ""),
        "trend_data": trend_data,
        "relevant_concepts": domain_context.get("relevant_concepts", {}),
        "analysis_request": (
            f"Analyze trends in {metric_name} over the provided time period. "
            f"Identify patterns, correlations with specific change types, and provide actionable insights. "
            f"Consider seasonal effects, day-of-week patterns, and the impact of specific change categories."
        )
    }
    return prompt


def generate_category_analysis_prompt(category, metrics_stats, sample_changes, domain_context):
    """Generate a prompt for analyzing a category of changes."""
    prompt = {
        "category": category,
        "category_context": domain_context.get("category_contexts", {}).get(category, ""),
        "metrics_stats": metrics_stats,
        "sample_changes": sample_changes,
        "relevant_concepts": domain_context.get("relevant_concepts", {}),
        "analysis_request": (
            f"Analyze the overall performance of '{category}' changes. "
            f"Identify which metrics are most impacted, any patterns in successful vs unsuccessful changes, "
            f"and provide recommendations for optimizing future changes in this category."
        )
    }
    return prompt