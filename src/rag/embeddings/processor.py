"""
Text processing utilities for the embedding system.
"""

from typing import List, Optional, Dict, Any
import re
from dataclasses import dataclass

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    metadata: Dict[str, Any]
    start_char: int
    end_char: int

class TextProcessor:
    """Text processing utilities for document preparation."""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        clean_text: bool = True,
        min_chunk_size: int = 50
    ):
        """Initialize the text processor.
        
        Args:
            chunk_size: Target size for text chunks (in characters)
            chunk_overlap: Number of characters to overlap between chunks
            clean_text: Whether to apply text cleaning
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.clean_text = clean_text
        self.min_chunk_size = min_chunk_size
    
    def clean(self, text: str) -> str:
        """Clean text by removing extra whitespace and normalizing.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not self.clean_text:
            return text
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', '-')
        
        return text.strip()
    
    def split_into_chunks(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to split
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of TextChunk objects
        """
        if metadata is None:
            metadata = {}
        
        # Clean text if enabled
        if self.clean_text:
            text = self.clean(text)
        
        # If text is shorter than chunk size, return as single chunk
        if len(text) <= self.chunk_size:
            return [TextChunk(
                text=text,
                metadata=metadata.copy(),
                start_char=0,
                end_char=len(text)
            )]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find end of current chunk
            end = start + self.chunk_size
            
            if end >= len(text):
                # Last chunk
                chunk_text = text[start:]
            else:
                # Find a good break point
                break_point = self._find_break_point(text, end)
                chunk_text = text[start:break_point]
                end = break_point
            
            # Only add if chunk meets minimum size
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(TextChunk(
                    text=chunk_text,
                    metadata=metadata.copy(),
                    start_char=start,
                    end_char=end
                ))
            
            # Move start position for next chunk
            start = end - self.chunk_overlap
        
        return chunks
    
    def _find_break_point(self, text: str, pos: int) -> int:
        """Find a good position to break the text, preferring sentence or paragraph boundaries.
        
        Args:
            text: Text to analyze
            pos: Target position to break at
            
        Returns:
            Actual break position
        """
        # Look for paragraph break
        next_para = text.find('\n\n', pos - 50, pos + 50)
        if next_para != -1:
            return next_para
        
        # Look for sentence break (period followed by space)
        next_sent = text.find('. ', pos - 30, pos + 30)
        if next_sent != -1:
            return next_sent + 1  # Include the period
        
        # Look for other punctuation
        for punct in [',', ';', ':', ' ']:
            next_punct = text.find(punct, pos - 20, pos + 20)
            if next_punct != -1:
                return next_punct + (1 if punct != ' ' else 0)
        
        # If no good break point found, break at exact position
        return pos
    
    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from text content.
        Currently a placeholder for future metadata extraction.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {}
        
        # Example metadata extraction (customize based on needs):
        
        # Extract potential date patterns
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, text)
        if dates:
            metadata['dates'] = dates
        
        # Count code-like patterns
        if re.search(r'(def |class |import |from .* import)', text):
            metadata['content_type'] = 'code'
        
        # Detect language features
        if re.search(r'(SELECT|FROM|WHERE|JOIN)\s', text, re.IGNORECASE):
            metadata['has_sql'] = True
        
        return metadata
