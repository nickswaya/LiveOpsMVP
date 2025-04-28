import streamlit as st
from typing import List, Dict, Any

from src.rag.core import EnhancedRAGSystem

def generate_follow_up_suggestions(query: str) -> List[str]:
    """Generate contextual follow-up suggestions based on the query."""
    query_lower = query.lower()
    
    # Base set of generic follow-ups
    generic_follow_ups = [
        "How has this trend changed over time?",
        "What are the top 3 factors influencing these results?",
        "Can you recommend specific improvements based on this data?"
    ]
    
    # Context-specific follow-ups
    if "revenue" in query_lower:
        return [
            "How does this compare to last week's revenue performance?",
            "Which user segments contributed most to this revenue?",
            "What other metrics were affected by these same changes?"
        ]
    elif "retention" in query_lower:
        return [
            "What's the correlation between these retention changes and revenue?",
            "How have retention trends changed over the past month?",
            "Which day of the week shows the best retention results?"
        ]
    elif any(term in query_lower for term in ["event", "pearly", "trident", "dealers edge"]):
        return [
            "How do weekend events compare to weekday events?",
            "What's the optimal duration for this type of event?",
            "Which metrics are most improved by these events?"
        ]
    elif "slot" in query_lower or "add slot" in query_lower or "remove slot" in query_lower:
        return [
            "Which slot themes perform best for revenue?",
            "What's the impact of slot positioning on engagement?",
            "How does adding a new slot compare to running a BOGO sale?"
        ]
    elif "bogo" in query_lower or "sale" in query_lower:
        return [
            "What's the optimal discount percentage for maximum revenue?",
            "Do sales perform better on specific days of the week?",
            "How do sales affect long-term metrics after they end?"
        ]
    elif "rtp" in query_lower or "adjustment" in query_lower:
        return [
            "What's the relationship between RTP changes and session length?",
            "Do RTP increases improve retention enough to offset revenue decreases?",
            "Which slot types respond best to RTP adjustments?"
        ]
    else:
        return generic_follow_ups

def show_query_interface(rag_system: EnhancedRAGSystem):
    """Display the natural language query interface."""
    # Display token usage statistics in sidebar if LLM service is enabled
    if rag_system.llm_service and rag_system.llm_service.is_enabled:
        st.sidebar.subheader("Token Usage Statistics")
        stats = rag_system.llm_service.token_counter.get_stats()
        st.sidebar.metric("Total Tokens Used", f"{stats['total_tokens_sent']:,}")
        st.sidebar.metric("Queries Processed", stats['query_count'])
        st.sidebar.metric("Avg. Tokens/Query", f"{stats['avg_tokens_per_query']:.0f}")
        st.sidebar.divider()
    
    st.header("Natural Language Query Interface")
    
    # Introduction to the enhanced capabilities
    st.write("""
    Our AI analytics system can now understand complex questions about your live ops changes and their impacts.
    You can ask questions about relationships between different metrics, categories, time periods, and more.
    """)
    
    # Example queries section
    with st.expander("Example questions you can ask", expanded=True):
        example_queries = [
            {
                "category": "Category Analysis",
                "examples": [
                    "Which BOGO offers have had the highest impact on revenue?",
                    "Compare the effectiveness of Pearly Rush Events vs Dealers Edge Events for retention",
                    "What's the average revenue impact of sales with discounts over 50%?"
                ]
            },
            {
                "category": "Temporal Analysis",
                "examples": [
                    "How has our revenue from slot additions changed over time?",
                    "Are BOGO sales more effective on weekends than weekdays?",
                    "Which day of the week shows the best conversion rates for our events?"
                ]
            },
            {
                "category": "Correlation Analysis",
                "examples": [
                    "Which changes that improved retention also increased revenue?",
                    "Do RTP adjustments that decrease revenue improve retention?",
                    "What's the relationship between session length and conversion rate in our events?"
                ]
            },
            {
                "category": "Comparative Analysis",
                "examples": [
                    "Which performs better for DAU: adding new slots or running events?",
                    "Compare the impact of cooldown reductions versus BOGO offers on engagement",
                    "Are RYD multiplier increases more effective than slot repositioning for revenue?"
                ]
            },
            {
                "category": "Insight Requests",
                "examples": [
                    "What's our most effective strategy for increasing conversion rates?",
                    "Which live ops changes should we prioritize for weekend revenue?",
                    "What patterns do our most successful retention-driving changes share?"
                ]
            }
        ]
        
        # Display example queries by category
        for category in example_queries:
            st.subheader(category["category"])
            for example in category["examples"]:
                # Create a clickable button for each example
                if st.button(example, key=f"btn_{example[:20]}"):
                    # When clicked, populate the query input and set a flag to submit
                    st.session_state.query = example
                    st.session_state.submit_query = True
                    st.rerun()
    
    # Initialize session state variables
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "submit_query" not in st.session_state:
        st.session_state.submit_query = False
    if "previous_query" not in st.session_state:
        st.session_state.previous_query = ""
    if "follow_up_suggestions" not in st.session_state:
        st.session_state.follow_up_suggestions = []
    
    # Form for submitting the query
    with st.form(key="query_form"):
        query = st.text_input("Enter your question", value=st.session_state.query)
        submit_button = st.form_submit_button(label="Submit")
        
        # Handle form submission
        if submit_button or st.session_state.submit_query:
            st.session_state.submit_query = False  # Reset flag
            if query:  # Only process if there's a query
                # Save current query as previous for context
                st.session_state.previous_query = query
                
                # Display spinner while generating insight
                with st.spinner("Adam is working on it..."):
                    insight = rag_system.generate_insight(query)
                
                # Store the insight for displaying outside the form
                st.session_state.current_insight = insight
                
                # Generate new follow-up suggestions based on this query
                st.session_state.follow_up_suggestions = generate_follow_up_suggestions(query)
    
    # Display insight if available
    if "current_insight" in st.session_state and st.session_state.current_insight:
        st.subheader("Insight")
        st.markdown(st.session_state.current_insight)
        
        # If LLM is not configured, show a message
        if "LLM service is not configured" in st.session_state.current_insight:
            st.warning("For enhanced insights, configure the LLM service by setting the API key.")
        
        # Provide follow-up suggestions if available
        if st.session_state.follow_up_suggestions:  # Check if we have suggestions
            with st.expander("Suggested follow-up questions", expanded=False):
                # Generate follow-up buttons based on the current query context
                for follow_up in st.session_state.follow_up_suggestions:
                    if st.button(follow_up, key=f"follow_{follow_up[:20]}"):
                        # Create a combined query with context from previous query
                        combined_query = f"Following up on my question about {st.session_state.previous_query}, {follow_up}"
                        
                        # Update the query and trigger submission
                        st.session_state.query = combined_query
                        st.session_state.submit_query = True
                        
                        # Rerun to show the new query and process it
                        st.rerun()
    
    # Add an option to view the domain knowledge the system has
    with st.expander("View Domain Knowledge Context", expanded=False):
        st.subheader("Game Concepts")
        for concept, description in rag_system.domain_manager.domain_context["concepts"].items():
            st.markdown(f"**{concept}**: {description}")
        
        st.subheader("Metrics")
        for metric, description in rag_system.domain_manager.domain_context["metric_contexts"].items():
            st.markdown(f"**{metric}**: {description}")
