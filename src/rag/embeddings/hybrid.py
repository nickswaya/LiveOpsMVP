"""
Hybrid search implementation combining semantic and keyword-based search.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from dataclasses import dataclass

from .models import EmbeddingModel
from .vectorstore import Document, VectorStore

@dataclass
class SearchResult:
    """Search result with combined score."""
    document: Document
    semantic_score: float
    keyword_score: float
    combined_score: float

class HybridSearcher:
    """Combines semantic and keyword-based search."""
    
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        """Initialize the hybrid searcher.
        
        Args:
            embedding_model: Model for generating embeddings
            vector_store: Store for vector similarity search
            semantic_weight: Weight for semantic search scores (0-1)
            keyword_weight: Weight for keyword search scores (0-1)
        """
        if not 0 <= semantic_weight <= 1 or not 0 <= keyword_weight <= 1:
            raise ValueError("Weights must be between 0 and 1")
        if abs(semantic_weight + keyword_weight - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1")
        
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        
        # Initialize TF-IDF vectorizer for keyword search
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents='unicode',
            ngram_range=(1, 2)  # Use unigrams and bigrams
        )
        self._tfidf_matrix = None
        self._needs_refresh = True
    
    def _refresh_tfidf(self) -> None:
        """Update TF-IDF matrix if needed."""
        if self._needs_refresh:
            if not self.vector_store.documents:
                self._tfidf_matrix = None
            else:
                texts = [doc.text for doc in self.vector_store.documents]
                self._tfidf_matrix = self.vectorizer.fit_transform(texts)
            self._needs_refresh = False
    
    def _compute_keyword_scores(self, query: str) -> np.ndarray:
        """Compute TF-IDF similarity scores for query.
        
        Args:
            query: Search query
            
        Returns:
            Array of similarity scores
        """
        self._refresh_tfidf()
        if self._tfidf_matrix is None:
            return np.array([])
        
        # Transform query and compute similarities
        query_vector = self.vectorizer.transform([query])
        return (self._tfidf_matrix @ query_vector.T).toarray().flatten()
    
    def search(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Perform hybrid search combining semantic and keyword matching.
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum combined score threshold
            metadata_filters: Optional metadata filters to apply
            
        Returns:
            List of SearchResult objects, sorted by combined score
        """
        # Get semantic search results for all documents
        query_embedding = self.embedding_model.embed(query)
        semantic_results = self.vector_store.similarity_search(
            query_embedding,
            k=len(self.vector_store.documents),
            score_threshold=None
        )
        
        # Create mapping of document ID to semantic score
        semantic_scores = {doc.id: score for doc, score in semantic_results}
        
        # Get keyword search scores
        keyword_scores = self._compute_keyword_scores(query)
        
        # Combine scores for all documents
        results = []
        for doc, keyword_score in zip(self.vector_store.documents, keyword_scores):
            # Get semantic score (default to 0 if not in top results)
            semantic_score = semantic_scores.get(doc.id, 0.0)
            # Normalize keyword score to 0-1 range if needed
            keyword_score = float(keyword_score)
            if keyword_score > 1.0:
                keyword_score = keyword_score / (1.0 + keyword_score)  # Soft normalization
            
            # Include if either score is significant
            if semantic_score > 0.01 or keyword_score > 0.01:
                # Compute combined score
                combined_score = (
                    self.semantic_weight * semantic_score +
                    self.keyword_weight * keyword_score
                )
                
                # Apply score threshold
                if score_threshold is not None and combined_score < score_threshold:
                    continue
                
                # Apply metadata filters
                if metadata_filters:
                    matches = True
                    for key, value in metadata_filters.items():
                        if key not in doc.metadata or doc.metadata[key] != value:
                            matches = False
                            break
                    if not matches:
                        continue
                
                results.append(SearchResult(
                    document=doc,
                    semantic_score=semantic_score,
                    keyword_score=keyword_score,
                    combined_score=combined_score
                ))
        
        # Sort by combined score
        results.sort(key=lambda x: x.combined_score, reverse=True)
        
        return results[:k]
    
    def adjust_weights(
        self,
        semantic_weight: float,
        keyword_weight: float
    ) -> None:
        """Adjust the weights for semantic and keyword scores.
        
        Args:
            semantic_weight: New weight for semantic scores (0-1)
            keyword_weight: New weight for keyword scores (0-1)
        """
        if not 0 <= semantic_weight <= 1 or not 0 <= keyword_weight <= 1:
            raise ValueError("Weights must be between 0 and 1")
        if abs(semantic_weight + keyword_weight - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1")
        
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
    
    def on_vector_store_update(self) -> None:
        """Called when vector store is updated."""
        self._needs_refresh = True
