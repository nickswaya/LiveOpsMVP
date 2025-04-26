import os
import json
import anthropic # type: ignore
from typing import Optional, Dict, Any
import streamlit as st

from prompts.system_prompts import (
    CHANGE_ANALYSIS_PROMPT, 
    TREND_ANALYSIS_PROMPT, 
    CATEGORY_ANALYSIS_PROMPT,
    QUERY_ANALYSIS_PROMPT
)
from prompts.analysis_prompts import (
    generate_change_analysis_prompt,
    generate_trend_analysis_prompt,
    generate_category_analysis_prompt
)
from prompts.query_prompts import (
    generate_query_prompt,
    generate_complex_query_prompt
)


class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        # Use provided API key or try to get from environment variable
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            self.is_enabled = False
            print("WARNING: No Anthropic API key found. LLM features will be disabled.")
        else:
            self.is_enabled = True
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-3-7-sonnet-20250219"  # Use this model or a less expensive one
            self.usage_count = 0
            self.usage_limit = 50  # Adjust based on credit allocation
            
    def generate_response(self, prompt: str, system_prompt: str = "", max_tokens: int = 1000) -> str:
        """Generate a response from the LLM model."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        # Check usage limit
        if self.usage_count >= self.usage_limit:
            return "API usage limit reached. To conserve credits, LLM features have been temporarily disabled."
        
        try:
            # Increment usage count (do this before the API call in case of errors)
            self.usage_count += 1
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating LLM response: {str(e)}"
    
    def analyze_change_impact(self, change_data: Dict[str, Any], domain_context: Dict[str, Any], confounding_factors: list) -> str:
        """Generate an analysis of the impact of a change based on provided data."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        # Generate prompt using the template
        prompt_data = generate_change_analysis_prompt(change_data, domain_context, confounding_factors)
        
        # Convert to JSON string for the LLM
        prompt = json.dumps(prompt_data, indent=2)
        
        # Use the specific system prompt for change analysis
        return self.generate_response(prompt, CHANGE_ANALYSIS_PROMPT)
    
    def analyze_metric_trend(self, metric_name: str, trend_data: list, domain_context: Dict[str, Any]) -> str:
        """Generate an analysis of trends for a specific metric."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        # Generate prompt using the template
        prompt_data = generate_trend_analysis_prompt(metric_name, trend_data, domain_context)
        
        # Convert to JSON string for the LLM
        prompt = json.dumps(prompt_data, indent=2)
        
        # Use the specific system prompt for trend analysis
        return self.generate_response(prompt, TREND_ANALYSIS_PROMPT)
    
    def analyze_category(self, category: str, metrics_stats: Dict[str, Any], sample_changes: list, domain_context: Dict[str, Any]) -> str:
        """Generate an analysis of a category of changes."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        # Generate prompt using the template
        prompt_data = generate_category_analysis_prompt(category, metrics_stats, sample_changes, domain_context)
        
        # Convert to JSON string for the LLM
        prompt = json.dumps(prompt_data, indent=2)
        
        # Use the specific system prompt for category analysis
        return self.generate_response(prompt, CATEGORY_ANALYSIS_PROMPT)
    
    def answer_query(self, query: str, intent: Dict[str, Any], domain_context: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Generate an answer to a natural language query."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        # Generate prompt using the template
        prompt_data = generate_query_prompt(query, intent, domain_context, context_data)
        
        # Convert to JSON string for the LLM
        prompt = json.dumps(prompt_data, indent=2)
        
        # Use the specific system prompt for query analysis
        return self.generate_response(prompt, QUERY_ANALYSIS_PROMPT)
    
    def answer_complex_query(self, query: str, related_data: Dict[str, Any], domain_context: Dict[str, Any]) -> str:
        """Generate an answer to a complex query that spans multiple intents."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        # Generate prompt using the template
        prompt_data = generate_complex_query_prompt(query, related_data, domain_context)
        
        # Convert to JSON string for the LLM
        prompt = json.dumps(prompt_data, indent=2)
        
        # Use the specific system prompt for query analysis
        return self.generate_response(prompt, QUERY_ANALYSIS_PROMPT)