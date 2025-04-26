# System Architecture & Design Patterns

## Overall Architecture

The system follows a modular architecture with clear separation of concerns, with planned enhancements to the RAG system:

### Current Architecture

```mermaid
flowchart TD
    UI[UI Layer] --> RAG[Enhanced RAG System]
    RAG --> Data[Data Layer]
    RAG --> LLM[LLM Service]
    
    subgraph UI Layer
        App[App Container]
        Pages[UI Pages]
        Components[UI Components]
        App --> Pages
        App --> Components
    end
    
    subgraph "Enhanced RAG System"
        Core[Core RAG]
        
        subgraph "Advanced Retrieval"
            Embeddings[Sentence Embeddings]
            Semantic[Semantic Search]
            Hybrid[Hybrid Retrieval]
            KGraph[Knowledge Graph]
        end
        
        subgraph "Context Management"
            Intent[Intent Analysis]
            Selection[Context Selection]
            Memory[Contextual Memory]
            Verification[Self-Verification]
        end
        
        Core --> Embeddings
        Embeddings --> Semantic
        Semantic --> Hybrid
        Core --> KGraph
        
        Core --> Intent
        Intent --> Selection
        Selection --> Memory
        Memory --> Verification
    end
    
    subgraph Data Layer
        Models[Data Models]
        Repository[Knowledge Repository]
        SampleData[Sample Generator]
    end
    
    subgraph LLM Service
        Service[LLM Service]
        Prompts[Prompts]
        Providers[LLM Providers]
    end
```

### Planned RAG System Architecture

The enhanced RAG system will incorporate several new components and capabilities:

```mermaid
flowchart TD
    Query[Query Input] --> Intent[Intent Analysis]
    Intent --> Retrieval[Advanced Retrieval]
    
    subgraph "Advanced Retrieval"
        Semantic[Semantic Search]
        Keyword[Keyword Search]
        Graph[Knowledge Graph]
        
        Semantic --> Hybrid[Hybrid Results]
        Keyword --> Hybrid
        Graph --> Hybrid
    end
    
    Retrieval --> Context[Context Selection]
    Context --> Memory[Contextual Memory]
    Memory --> Verification[Self-Verification]
    Verification --> Response[Final Response]
    
    subgraph "Knowledge Graph"
        Entities[Entities]
        Relations[Relations]
        Causality[Causal Links]
        
        Entities --> Relations
        Relations --> Causality
    end
```

## Directory Structure

```
LiveOpsAgent/
├── src/                           # Source code
│   ├── data/                      # Data layer
│   │   ├── models.py             # Core data models
│   │   ├── repository.py         # Knowledge repository
│   │   └── sample_generator.py   # Sample data generation
│   │
│   ├── rag/                      # RAG system components
│   │   ├── core.py              # Core RAG functionality
│   │   ├── indexing/            # Indexing strategies
│   │   ├── domain_knowledge/    # Domain knowledge management
│   │   └── analysis/           # Analysis capabilities
│   │
│   ├── llm/                      # LLM integration
│   │   ├── service.py           # LLM service
│   │   ├── providers/           # LLM providers
│   │   └── prompts/            # Structured prompts
│   │
│   ├── ui/                       # UI components
│   │   ├── app.py              # Main app container
│   │   └── pages/              # Page components
│   │
│   └── evaluators/              # Future evaluators
│
├── config/                       # Configuration
├── tests/                       # Tests
└── memory-bank/                 # Memory Bank files
```

## Key Design Patterns

### 1. Embedding System Patterns
- **Factory Pattern**: Used in embedding model creation
  ```python
  model = create_embedding_model("local", "all-MiniLM-L6-v2")
  ```
- **Strategy Pattern**: Different embedding providers follow same interface
  ```python
  class EmbeddingModel(ABC):
      def embed(self, text: str | List[str]) -> np.ndarray:
          pass
  ```
- **Composite Pattern**: Hybrid search combines multiple search strategies
  ```python
  combined_score = (
      semantic_weight * semantic_score +
      keyword_weight * keyword_score
  )
  ```

### 2. Repository Pattern
- `KnowledgeRepository` acts as a centralized data store
- Provides methods for adding and retrieving changes and metrics
- Abstracts data storage details from the rest of the system

### 3. Service Layer Pattern
- `LLMService` encapsulates LLM interaction details
- Handles API communication, rate limiting, and error handling
- Provides a clean interface for LLM operations

### 4. Strategy Pattern
- Used in the indexing system to support different indexing strategies
- Each index type (category, metric, temporal, tag) follows the same interface
- Makes it easy to add new indexing strategies

### 5. Factory Pattern
- Used in prompt generation to create different types of prompts
- Each prompt type has its own generator function
- Makes it easy to maintain and modify prompt structures

### 6. Facade Pattern
- `EnhancedRAGSystem` provides a simplified interface to the complex subsystems
- Coordinates between data layer, indexing, domain knowledge, and analysis
- Makes the system easier to use from the UI layer

### 7. Observer Pattern
- Used in the UI for state management with Streamlit
- Components react to state changes automatically
- Enables interactive UI updates

## Component Responsibilities

### Embedding System
- **Models**: Manage embedding model implementations
- **Vector Store**: Handle vector storage and similarity search
- **Text Processor**: Process and chunk text documents
- **Hybrid Search**: Combine semantic and keyword search

### Data Layer
- Define data structures for changes and metrics
- Manage data storage and retrieval
- Generate sample data for testing

### RAG System
- Core: Coordinate between components
- Embeddings: Generate and manage embeddings
  - Model management and configuration
  - Vector storage and retrieval
  - Text processing and chunking
  - Hybrid search implementation
- Domain Knowledge: Manage domain-specific context
- Analysis: Analyze changes and generate insights

### LLM Service
- Handle LLM API integration
- Manage prompts and responses
- Support multiple LLM providers

### UI Layer
- Present data and insights
- Handle user interactions
- Manage application state

## Design Decisions

1. **Modular Structure**
   - Each component is self-contained
   - Clear interfaces between components
   - Easy to modify or replace individual parts

2. **Extensible Architecture**
   - Easy to add new features
   - Support for multiple LLM providers
   - Flexible indexing system

3. **Separation of Concerns**
   - UI logic separate from business logic
   - Data layer independent of presentation
   - Clear boundaries between components

4. **Configuration Over Code**
   - Domain knowledge in configuration
   - LLM settings configurable
   - Easy to modify system behavior

5. **Future-Proof Design**
   - Support for additional evaluators
   - Flexible data model
   - Scalable architecture

## Implementation Notes

1. **Code Organization**
   - Each module in its own directory
   - Clear file naming conventions
   - Logical grouping of related functionality

2. **Dependencies**
   - Minimal coupling between components
   - Clear dependency flow
   - Easy to understand relationships

3. **Error Handling**
   - Graceful fallbacks for LLM failures
   - Clear error messages
   - Robust error recovery

4. **Performance Considerations**
   - Efficient indexing strategies
   - Smart caching opportunities
   - Optimized data structures

5. **Testing Strategy**
   - Each component independently testable
   - Clear interfaces for mocking
   - Comprehensive test coverage possible
