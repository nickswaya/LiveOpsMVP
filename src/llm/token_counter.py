"""
Simple token counter for tracking LLM token usage.
"""

class TokenCounter:
    """Simple token counter for tracking LLM token usage."""
    
    def __init__(self):
        """Initialize token counter with default settings."""
        self.total_tokens_sent = 0
        self.query_count = 0
        self.char_to_token_ratio = 4  # Approximate ratio
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from text.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated number of tokens
        """
        return len(text) // self.char_to_token_ratio
    
    def track_query(self, context_text: str, query_text: str) -> dict:
        """Track tokens for a query and its context.
        
        Args:
            context_text: The context text being sent to LLM
            query_text: The query text being sent to LLM
            
        Returns:
            Dictionary containing token counts:
            - context_tokens: Tokens in context
            - query_tokens: Tokens in query
            - total_tokens: Total tokens sent
        """
        context_tokens = self.estimate_tokens(context_text)
        query_tokens = self.estimate_tokens(query_text)
        total_tokens = context_tokens + query_tokens
        
        self.total_tokens_sent += total_tokens
        self.query_count += 1
        
        return {
            "context_tokens": context_tokens,
            "query_tokens": query_tokens,
            "total_tokens": total_tokens
        }
    
    def get_stats(self) -> dict:
        """Get token usage statistics.
        
        Returns:
            Dictionary containing:
            - total_tokens_sent: Total tokens sent to LLM
            - query_count: Number of queries processed
            - avg_tokens_per_query: Average tokens per query
        """
        return {
            "total_tokens_sent": self.total_tokens_sent,
            "query_count": self.query_count,
            "avg_tokens_per_query": self.total_tokens_sent / max(1, self.query_count)
        }
