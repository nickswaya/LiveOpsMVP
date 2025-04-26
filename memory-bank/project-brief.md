Project Brief: AI-Powered Analytics System for Game Operations
Project Overview
We are building an intelligent analytics system that leverages RAG (Retrieval-Augmented Generation) and LLM technologies to track, analyze, and provide insights on live operations changes in mobile casino games. The system connects operational changes to business outcomes while preserving institutional knowledge, addressing the challenge of managing numerous daily changes (up to 15) and understanding their impacts on key metrics.
The core vision is a system that can answer complex questions about past changes, identify patterns of success, provide actionable recommendations, and continuously learn from new data and user interactions.
Problem Statement & Business Need
Mobile gaming companies implement numerous live operations changes daily, including promotions, events, content updates, and balance adjustments. Currently, there are significant challenges in:

Tracking what changes were made and when
Attributing metric movements to specific changes
Preserving "tribal knowledge" about the gaming industry, domain, and specific games
Making data-driven decisions for future planning

The lack of a unified system results in inefficient analysis, lost institutional knowledge, and sub-optimal decision-making that directly impacts revenue and player engagement.
Technical Architecture & Components
The current architecture consists of the following components:

Data Model

LiveOpsChange class for storing change details
MetricMeasurement class for before/after metric comparisons
KnowledgeRepository for organizing changes and metrics


Enhanced RAG System

Vector-based similarity search using TF-IDF (to be upgraded)
Multi-dimensional indexing (by category, tag, metric impact, time)
Domain knowledge context for gaming concepts
Intent recognition for query understanding


LLM Integration

Structured prompt system for different analysis types
Context augmentation with relevant domain knowledge
Query-specific response generation


User Interface

Interactive dashboard for metric visualization
Natural language query interface
Detailed impact analysis for specific changes
Conversation-like follow-up capabilities



Work Accomplished to Date

Foundation Architecture

Created core data models for changes and metrics
Implemented basic repository for in-memory storage
Developed sample data generation for testing


RAG System Implementation

Built multi-dimensional indexing for efficient retrieval
Created domain knowledge context structure
Implemented intent detection for query understanding
Developed analysis capabilities for various metrics and categories


LLM Integration

Set up Anthropic API integration
Created structured prompt system
Implemented contextual response generation
Added follow-up capabilities


User Interface

Developed interactive dashboard for metrics visualization
Created natural language query interface
Implemented impact analysis views
Added example queries and follow-up suggestions


Security & Deployment

Implemented secure API key handling
Set up environment variable management
Created Streamlit-based deployment structure



Key System Requirements
Flexibility

The system must be designed to easily add new metrics for analysis without requiring significant code changes
Relationships between metrics should be definable through a flexible schema
Configuration-driven approach to allow non-technical users to add new analytics dimensions
Domain knowledge should be expandable through a simple interface

Continuous Learning

The system should capture user feedback on insights and recommendations
New changes and their impacts should automatically enrich the knowledge base
Regular retraining of vector embeddings to incorporate new domain knowledge
Learning loop to improve response quality based on user interactions

Modularity & Scalability

Core components (data model, RAG system, LLM service) should be independent and reusable
Knowledge repository should support multiple domain-specific knowledge bases
System architecture should allow for specialized evaluators beyond Live Ops:

Client/server release risk evaluators
A/B test evaluators
Slot impact evaluators
Player behavior analyzers


Each evaluator could potentially have its own knowledge base or share a centralized one

Knowledge Base Management

Tracking of knowledge base size and complexity metrics
Automatic pruning of less relevant or outdated information
Strategy for contextual sampling of information to avoid LLM token limits
Performance monitoring to ensure response time remains acceptable

Domain Knowledge Integration

Interface for manually adding industry, domain, and game-specific context
Ability to define relationships between concepts (e.g., how BOGO sales typically affect player behavior)
Support for importing external knowledge sources
Version control for knowledge base updates

Next Steps & Future Development
The current MVP demonstrates core functionality with sample data. The next phases should focus on:

Production Data Integration

Connect to actual live ops change logs and metrics databases
Implement ETL processes for ongoing data ingestion
Develop data validation and cleaning processes


Enhanced Vector Representations

Replace TF-IDF with more sophisticated embedding models
Implement semantic search capabilities
Add support for hybrid retrieval (keyword + semantic)


Advanced Analytics

Implement causal analysis capabilities
Add cohort analysis for player segments
Develop statistical significance testing
Create anomaly detection for unexpected metric changes


Knowledge Base Management

Develop UI for knowledge base curation
Implement relevance scoring for knowledge entries
Create automated knowledge extraction from change data


Extension to Additional Evaluators

Define architecture for multiple specialized evaluators
Implement shared vs. domain-specific knowledge bases
Create cross-evaluator insights capability



This system aims to transform how we understand and optimize our operations strategy, turning our rapid pace of change from a challenge into a competitive advantage through data-driven insights and preserved institutional knowledge.