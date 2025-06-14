# Technical Context

## Technologies Used

### Core Technologies
1. **Python**
   - Primary programming language
   - Version: 3.8+
   - Used for all backend logic and data processing

2. **Streamlit**
   - Web framework for UI
   - Provides interactive data visualization
   - Handles state management and user interactions

3. **scikit-learn**
   - Used for TF-IDF vectorization
   - Provides cosine similarity calculations
   - Handles basic ML operations

4. **pandas**
   - Data manipulation and analysis
   - Used for structured data operations
   - Provides DataFrame functionality

5. **plotly**
   - Interactive data visualization
   - Used for charts and graphs
   - Provides rich visual analytics

### LLM Integration
1. **Anthropic Claude**
   - Primary LLM provider
   - Model: claude-3-7-sonnet-20250219
   - Used for analysis and insights

2. **Future Support Planned**
   - OpenAI GPT models
   - Google PaLM/Gemini
   - Local Hugging Face models

### RAG System
1. **TF-IDF Vectorization**
   - Current embedding strategy
   - Used for similarity search
   - Planned upgrade to more sophisticated embeddings

2. **Multi-dimensional Indexing**
   - Category-based indexing
   - Metric impact indexing
   - Temporal indexing
   - Tag-based indexing

## Development Setup

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Required Environment Variables
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

### Running the Application
```bash
# Start the Streamlit app
streamlit run main.py
```

## Dependencies

### Core Dependencies
```
streamlit>=1.10.0
pandas>=1.3.0
numpy>=1.19.0
scikit-learn>=0.24.0
plotly>=5.3.0
anthropic>=0.3.0
python-dotenv>=0.19.0
```

### Development Dependencies
```
pytest>=6.2.0
black>=21.5b2
flake8>=3.9.0
mypy>=0.910
```

## Technical Constraints

### Performance Constraints
1. **Memory Usage**
   - In-memory data storage currently
   - Limited by available RAM
   - Future: Consider persistent storage

2. **LLM Rate Limits**
   - API usage limits
   - Token quotas
   - Response time considerations

3. **Scalability**
   - Current design for single-user usage
   - Local deployment model
   - Future: Consider multi-user support

### Data Serialization Strategy
1. **Current Implementation**
   - Data models with to_dict methods for JSON serialization
   - Repository methods return serializable dictionaries
   - DateTime fields converted to ISO format strings
   - Consistent dictionary structure across layers

2. **Known Issues**
   - UI components expect object attributes but receive dictionaries
   - Need to update UI layer for dictionary compatibility
   - Potential performance impact from frequent serialization
   - Validation needed for serialized structures

3. **Future Improvements**
   - Add view models for UI components
   - Implement data validation for serialized structures
   - Consider caching serialized results
   - Add deserialization methods where needed

### Technical Limitations
1. **Embedding System**
   - Basic TF-IDF implementation
   - Limited semantic understanding
   - Future: Upgrade to better embeddings

2. **Data Storage & State Management**
   - In-memory repository with session persistence
   - Streamlit session state for object persistence:
     - Repository state
     - LLM service state
     - Token counter state
     - RAG system state
   - No cross-session persistence yet
   - Future: Add database support for:
     - Cross-session token usage statistics
     - Query history
     - System state
     - User preferences

3. **LLM Integration**
   - Single provider support (Anthropic)
   - Limited error recovery
   - Future: Multi-provider support

4. **UI Framework Constraints**
   - Streamlit's stateless architecture mitigated with session state
   - State persists during page interactions
   - State resets on browser refresh/restart
   - Limited control over component lifecycle
   - Future: Consider external state persistence

5. **UI Styling & Theming**
   - CSS variables for theme-aware styling
   - Dark mode support through data-theme attribute
   - Responsive design with mobile breakpoints
   - Custom styling through unsafe_allow_html:
     ```css
     /* Base theme variables */
     :root {
         --text-color: #1E1E1E;
         --bg-color: #FFFFFF;
         --card-bg: #FFFFFF;
     }
     
     /* Dark mode overrides */
     [data-theme="dark"] {
         --text-color: #FFFFFF;
         --bg-color: #1E1E1E;
         --card-bg: #2D2D2D;
     }
     ```
   - Component styling patterns:
     - Grid layouts for feature displays
     - Card-based content organization
     - Interactive hover effects
     - Professional animations
   - Limitations:
     - Limited control over Streamlit's base styles
     - Some components require unsafe_allow_html
     - Custom styling needs careful dark mode consideration
     - Mobile responsiveness requires manual implementation

## Security Considerations

### API Key Management
1. **Current Approach**
   - Environment variables
   - Streamlit secrets
   - Session-based storage

2. **Best Practices**
   - Never commit API keys
   - Rotate keys regularly
   - Use secure storage

### Data Security
1. **Current State**
   - Local data only
   - No sensitive information
   - No authentication required

2. **Future Needs**
   - User authentication
   - Data encryption
   - Access control

## Monitoring & Logging

### Current Implementation
1. **Basic Logging**
   - Print statements
   - Streamlit messages
   - Error reporting

2. **Usage Tracking**
   - LLM API call counting
   - Basic rate limiting
   - Usage statistics

### Future Improvements
1. **Enhanced Monitoring**
   - Structured logging
   - Performance metrics
   - Usage analytics

2. **Observability**
   - Error tracking
   - Performance monitoring
   - Usage patterns

## Development Workflow

### Code Organization
1. **Module Structure**
   - Logical component separation
   - Clear module boundaries
   - Consistent naming

2. **Code Style**
   - PEP 8 compliance
   - Type hints
   - Docstrings

### Testing Strategy
1. **Unit Tests**
   - Component-level testing
   - Mocked dependencies
   - Isolated test cases

2. **Integration Tests**
   - Cross-component testing
   - End-to-end flows
   - UI testing

## Future Technical Roadmap

### Short-term Improvements
1. **Embedding System**
   - Upgrade to better embeddings
   - Implement semantic search
   - Add hybrid retrieval

2. **Data Storage**
   - Add database support
   - Implement persistence
   - Add data versioning

### Long-term Goals
1. **Architecture Evolution**
   - Multi-user support
   - Distributed deployment
   - Cloud integration

2. **Feature Expansion**
   - Additional evaluators
   - Enhanced analytics
   - Advanced visualizations
