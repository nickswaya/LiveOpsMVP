"""
Vector storage and similarity search implementation.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Document:
    """Represents a document with its embedding and metadata."""
    text: str
    embedding: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __hash__(self):
        """Make Document hashable using its unique ID."""
        return hash(self.id)
    
    def __eq__(self, other):
        """Implement equality using document ID."""
        if not isinstance(other, Document):
            return False
        return self.id == other.id

class VectorStore:
    """In-memory vector store with similarity search capabilities."""
    
    def __init__(self):
        """Initialize an empty vector store."""
        self.documents: List[Document] = []
        self.embeddings: Optional[np.ndarray] = None
        self._needs_refresh = True
    
    def add(self, doc: Document) -> None:
        """Add a document to the store.
        
        Args:
            doc: Document instance with text, embedding, and optional metadata
        """
        self.documents.append(doc)
        self._needs_refresh = True
    
    def add_many(self, docs: List[Document]) -> None:
        """Add multiple documents to the store.
        
        Args:
            docs: List of Document instances
        """
        self.documents.extend(docs)
        self._needs_refresh = True
    
    def _refresh_embeddings(self) -> None:
        """Update the embeddings matrix if needed."""
        if self._needs_refresh:
            if not self.documents:
                self.embeddings = None
            else:
                # Stack all embeddings into a single matrix
                self.embeddings = np.vstack([doc.embedding for doc in self.documents])
            self._needs_refresh = False
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Document, float]]:
        """Find most similar documents using cosine similarity.
        
        Args:
            query_embedding: Query vector to compare against
            k: Number of results to return
            score_threshold: Minimum similarity score (optional)
            
        Returns:
            List of (document, score) tuples, sorted by descending similarity
        """
        self._refresh_embeddings()
        
        if not self.documents or self.embeddings is None:
            return []
        
        # Compute cosine similarity
        # Note: Embeddings are assumed to be L2-normalized
        similarities = self.embeddings @ query_embedding
        
        # Get top k indices
        if score_threshold is not None:
            # Filter by threshold first
            mask = similarities >= score_threshold
            indices = np.argsort(similarities[mask])[-k:][::-1]
            # Map back to original indices
            top_indices = np.where(mask)[0][indices]
            top_scores = similarities[top_indices]
        else:
            top_indices = np.argsort(similarities)[-k:][::-1]
            top_scores = similarities[top_indices]
        
        # Return documents and scores
        return [
            (self.documents[idx], float(score))
            for idx, score in zip(top_indices, top_scores)
        ]
    
    def filter_by_metadata(
        self,
        filters: Dict[str, Any],
        results: List[Tuple[Document, float]]
    ) -> List[Tuple[Document, float]]:
        """Filter search results by metadata.
        
        Args:
            filters: Dictionary of metadata field-value pairs to match
            results: List of (document, score) tuples to filter
            
        Returns:
            Filtered list of (document, score) tuples
        """
        filtered = []
        for doc, score in results:
            matches = True
            for key, value in filters.items():
                if key not in doc.metadata or doc.metadata[key] != value:
                    matches = False
                    break
            if matches:
                filtered.append((doc, score))
        return filtered
    
    def clear(self) -> None:
        """Clear all documents from the store."""
        self.documents.clear()
        self.embeddings = None
        self._needs_refresh = True
    
    @property
    def size(self) -> int:
        """Get the number of documents in the store."""
        return len(self.documents)
    
    def __len__(self) -> int:
        return self.size
