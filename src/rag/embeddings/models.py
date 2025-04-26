"""
Embedding model implementations for the enhanced RAG system.
Designed for easy swapping between different embedding providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingModel(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def embed(self, text: str | List[str]) -> np.ndarray:
        """Convert text (single string or list of strings) to embeddings.
        
        Args:
            text: Single text string or list of text strings to embed
            
        Returns:
            numpy.ndarray: If input is single string, returns shape (embedding_dim,)
                         If input is list, returns shape (n_texts, embedding_dim)
        """
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Get the dimensionality of the embeddings."""
        pass

class LocalModel(EmbeddingModel):
    """Local embedding model using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the local model.
        
        Args:
            model_name: Name of the pre-trained model to use
        """
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
    
    def embed(self, text: str | List[str]) -> np.ndarray:
        """Convert text to embeddings using local model."""
        return self.model.encode(
            text,
            batch_size=32,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
    
    @property
    def dimension(self) -> int:
        return self._dimension

# Easy to add more providers like:
# class SnowflakeModel(EmbeddingModel):
#     def __init__(self, connection_params: Dict[str, Any]):
#         """Initialize Snowflake connection and model."""
#         pass
#
#     def embed(self, text: str | List[str]) -> np.ndarray:
#         """Convert text to embeddings using Snowflake."""
#         pass
#
#     @property
#     def dimension(self) -> int:
#         return self._dimension

def create_embedding_model(
    provider: str = "local",
    model_name: str = "all-MiniLM-L6-v2",
    **kwargs
) -> EmbeddingModel:
    """Factory function to create embedding models.
    
    Args:
        provider: Embedding provider ("local", "snowflake", etc.)
        model_name: Name of the model to use (if applicable)
        **kwargs: Additional provider-specific configuration
        
    Returns:
        EmbeddingModel: Configured embedding model instance
        
    Example:
        # Local model
        model = create_embedding_model("local", "all-MiniLM-L6-v2")
        
        # Future Snowflake integration
        # model = create_embedding_model(
        #     "snowflake",
        #     connection_params={
        #         "account": "...",
        #         "warehouse": "...",
        #         "database": "..."
        #     }
        # )
    """
    if provider == "local":
        return LocalModel(model_name)
    # elif provider == "snowflake":
    #     return SnowflakeModel(kwargs.get("connection_params", {}))
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
