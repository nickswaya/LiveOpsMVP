"""
Basic example demonstrating the enhanced embedding system.
"""

from typing import List, Dict
from datetime import datetime

from ..models import create_embedding_model
from ..vectorstore import VectorStore, Document
from ..processor import TextProcessor
from ..hybrid import HybridSearcher

def create_sample_documents() -> List[Dict]:
    """Create sample documents for demonstration."""
    return [
        {
            "text": """
            BOGO promotion increased revenue by 15% over the weekend.
            Player engagement metrics showed significant improvement.
            Daily active users increased from 100k to 115k.
            """,
            "metadata": {
                "category": "promotion",
                "type": "BOGO",
                "date": "2025-04-20"
            }
        },
        {
            "text": """
            Slot machine RTP adjustment from 92% to 94% resulted in
            longer session lengths. Average session time increased
            by 8 minutes, while revenue per session decreased by 3%.
            """,
            "metadata": {
                "category": "configuration",
                "type": "RTP_adjustment",
                "date": "2025-04-21"
            }
        },
        {
            "text": """
            New featured placement for Dragon's Fortune slot machine
            led to 25% increase in spins. Player feedback indicates
            high interest in the dragon theme and bonus features.
            """,
            "metadata": {
                "category": "content",
                "type": "featured_placement",
                "date": "2025-04-22"
            }
        }
    ]

def main():
    """Demonstrate basic usage of the embedding system."""
    print("Initializing embedding system...")
    
    # Create embedding model
    model = create_embedding_model("local", "all-MiniLM-L6-v2")
    
    # Initialize vector store
    store = VectorStore()
    
    # Initialize text processor
    processor = TextProcessor(
        chunk_size=200,  # Smaller chunks for this example
        chunk_overlap=20
    )
    
    # Initialize hybrid searcher
    searcher = HybridSearcher(
        embedding_model=model,
        vector_store=store,
        semantic_weight=0.7,
        keyword_weight=0.3
    )
    
    # Process and store sample documents
    print("\nProcessing sample documents...")
    sample_docs = create_sample_documents()
    
    for doc_data in sample_docs:
        # Process text into chunks
        chunks = processor.split_into_chunks(
            doc_data["text"],
            metadata=doc_data["metadata"]
        )
        
        # Create embeddings and store documents
        for chunk in chunks:
            embedding = model.embed(chunk.text)
            doc = Document(
                text=chunk.text,
                embedding=embedding,
                metadata=chunk.metadata,
                timestamp=datetime.now()
            )
            store.add(doc)
    
    print(f"Stored {store.size} document chunks")
    
    # Perform some example searches
    example_queries = [
        "How did the BOGO promotion affect revenue?",
        "What was the impact of RTP changes on player behavior?",
        "Tell me about slot machine performance",
    ]
    
    print("\nPerforming example searches...")
    for query in example_queries:
        print(f"\nQuery: {query}")
        results = searcher.search(query, k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Text: {result.document.text.strip()}")
            print(f"Category: {result.document.metadata['category']}")
            print(f"Semantic Score: {result.semantic_score:.3f}")
            print(f"Keyword Score: {result.keyword_score:.3f}")
            print(f"Combined Score: {result.combined_score:.3f}")
    
    # Demonstrate metadata filtering
    print("\nSearching with metadata filter...")
    results = searcher.search(
        "performance improvements",
        k=2,
        metadata_filters={"category": "promotion"}
    )
    
    print(f"\nFound {len(results)} results in 'promotion' category:")
    for result in results:
        print(f"\nText: {result.document.text.strip()}")
        print(f"Score: {result.combined_score:.3f}")

if __name__ == "__main__":
    main()
