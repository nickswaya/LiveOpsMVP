import os
import anthropic
from typing import Optional
import streamlit as st


class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        # Try to get API key from different sources in order of priority:
        # 1. Directly provided API key
        # 2. Streamlit secrets
        # 3. Environment variables
        
        if api_key:
            self.api_key = api_key
        elif "ANTHROPIC_API_KEY" in st.secrets:
            self.api_key = st.secrets["ANTHROPIC_API_KEY"]
        else:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            self.is_enabled = False
            print("WARNING: No Anthropic API key found. LLM features will be disabled.")
        else:
            self.is_enabled = True
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-3-7-sonnet-20250219"
            self.usage_count = 0
            self.usage_limit = 50
            
    def generate_response(self, prompt: str, system_prompt: str = "", max_tokens: int = 1000) -> str:
        """Generate a response from the LLM model."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        try:
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
    
    def analyze_change_impact(self, change_description: str, metrics_data: dict) -> str:
        """Generate an analysis of the impact of a change based on metrics data."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        system_prompt = """
        You are an analytics expert for a mobile gaming company. 
        Analyze the impact of a live ops change based on the provided metrics data.
        Focus on whether the change achieved its expected impact and provide insights on why it may have performed as it did.
        Keep your analysis concise and data-driven, focusing on the most significant impacts.
        """
        
        prompt = f"""
        Change Description: {change_description}
        
        Metrics Data:
        {metrics_data}
        
        Please analyze the impact of this change, focusing on:
        1. Did the change achieve its expected impact?
        2. Which metrics were most significantly affected?
        3. What insights can be drawn from this change for future similar changes?
        """
        
        return self.generate_response(prompt, system_prompt)
    
    def generate_insight_from_query(self, query: str, changes_data: list) -> str:
        """Generate an insight based on a natural language query about changes."""
        if not self.is_enabled:
            return "LLM service is not configured. Please set ANTHROPIC_API_KEY environment variable."
        
        system_prompt = """
        You are an analytics expert for a mobile gaming company.
        Answer questions about live ops changes and their impacts on key metrics.
        Use the provided data to give concise, data-driven insights.
        Focus on extracting actionable insights from the patterns in the data.
        """
        
        prompt = f"""
        User Query: {query}
        
        Changes Data:
        {changes_data}
        
        Please provide a concise and specific answer to the query using only the data provided.
        """
        
        return self.generate_response(prompt, system_prompt)