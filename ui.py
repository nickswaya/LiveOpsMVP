import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def create_app(rag_system):
    st.title("Live Ops Analytics System - MVP")
    
    # Sidebar navigation
    nav = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Search Similar Changes", "Impact Analysis", "Query Interface", "LLM Configuration"]
    )
    
    if nav == "Dashboard":
        show_dashboard(rag_system)
    elif nav == "Search Similar Changes":
        show_search_interface(rag_system)
    elif nav == "Impact Analysis":
        show_impact_analysis(rag_system)
    elif nav == "LLM Configuration":
        show_llm_config(rag_system)
    else:  # Query Interface
        show_query_interface(rag_system)

def show_dashboard(rag_system):
    st.header("Live Ops Analytics Dashboard")
    
    # Generate some stats
    change_count = len(rag_system.knowledge_repo.changes)
    categories = {}
    for change in rag_system.knowledge_repo.changes:
        if change.category in categories:
            categories[change.category] += 1
        else:
            categories[change.category] = 1
    
    # Show stats
    st.subheader("Overall Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Changes", change_count)
    with col2:
        st.metric("Time Period", "Last 30 days")
    
    # Show category breakdown
    st.subheader("Change Categories")
    category_df = pd.DataFrame({
        "Category": list(categories.keys()),
        "Count": list(categories.values())
    })
    fig = px.pie(category_df, values="Count", names="Category", title="Changes by Category")
    st.plotly_chart(fig)
    
    # Show recent changes
    st.subheader("Recent Changes")
    recent_changes = sorted(rag_system.knowledge_repo.changes, key=lambda x: x.timestamp, reverse=True)[:10]
    
    recent_data = []
    for change in recent_changes:
        metrics = rag_system.knowledge_repo.get_metrics_for_change(change.change_id)
        # Find revenue impact
        revenue_impact = next((m.percent_change for m in metrics if m.metric_name == "revenue"), 0)
        
        recent_data.append({
            "Date": change.timestamp.strftime("%Y-%m-%d"),
            "Category": change.category,
            "Description": change.description,
            "Revenue Impact": f"{'+' if revenue_impact > 0 else ''}{revenue_impact:.2f}%"
        })
    
    recent_df = pd.DataFrame(recent_data)
    st.dataframe(recent_df)

def show_search_interface(rag_system):
    st.header("Search Similar Changes")
    
    # Search input
    search_query = st.text_input("Enter search terms (e.g., 'sale on coins')")
    
    if search_query:
        st.subheader("Search Results")
        similar_changes = rag_system.search_similar_changes(search_query)
        
        for i, result in enumerate(similar_changes):
            change = result["change"]
            metrics = result["metrics"]
            
            # Create an expander for each result
            with st.expander(f"{i+1}. {change.description} ({change.category}) - {change.timestamp.strftime('%Y-%m-%d')}"):
                st.write(f"**Category:** {change.category}")
                st.write(f"**Tags:** {', '.join(change.tags)}")
                
                # Display expected vs actual impact
                st.subheader("Impact Analysis")
                
                impact_data = []
                for metric in metrics:
                    expected = change.expected_impact.get(metric.metric_name, "neutral")
                    actual = "neutral"
                    if metric.percent_change > 5:
                        actual = "increase"
                    elif metric.percent_change < -5:
                        actual = "decrease"
                    
                    impact_data.append({
                        "Metric": metric.metric_name,
                        "Before": f"{metric.before_value:.2f}",
                        "After": f"{metric.after_value:.2f}",
                        "Change": f"{'+' if metric.percent_change > 0 else ''}{metric.percent_change:.2f}%",
                        "Expected": expected,
                        "Matched": "✓" if expected == actual or (expected == "neutral" and -5 <= metric.percent_change <= 5) else "✗"
                    })
                
                impact_df = pd.DataFrame(impact_data)
                st.dataframe(impact_df)

def show_impact_analysis(rag_system):
    st.header("Impact Analysis")
    
    # Select metric to analyze
    metric = st.selectbox(
        "Select metric to analyze",
        ["revenue", "dau", "retention", "session_length", "conversion_rate"]
    )
    
    # Generate dataframe with changes and their impact on the selected metric
    changes_data = []
    for change in rag_system.knowledge_repo.changes:
        metrics = rag_system.knowledge_repo.get_metrics_for_change(change.change_id)
        # Find the selected metric
        impact = next((m for m in metrics if m.metric_name == metric), None)
        
        if impact:
            changes_data.append({
                "change_id": change.change_id,
                "date": change.timestamp,  # Keep as datetime for sorting
                "date_str": change.timestamp.strftime("%Y-%m-%d"),
                "category": change.category,
                "description": change.description,
                "before": impact.before_value,
                "after": impact.after_value,
                "percent_change": impact.percent_change
            })
    
    changes_df = pd.DataFrame(changes_data)
    
    # First part - showing top positive impact
    if not changes_df.empty:
        # Sort by impact
        changes_df = changes_df.sort_values(by="percent_change", ascending=False)
        
        # Show top positive impact
        st.subheader(f"Top Positive Impact on {metric.upper()}")
        positive_df = changes_df.head(5)
        
        # Create a bar chart
        fig = px.bar(
            positive_df, 
            x="description", 
            y="percent_change",
            color="category",
            labels={"description": "Change", "percent_change": "% Change", "category": "Category"},
            title=f"Top 5 Changes by {metric.upper()} Impact"
        )
        st.plotly_chart(fig)
        
        # Show details in table
        st.dataframe(positive_df[["date_str", "category", "description", "percent_change"]])
        
        # Show bottom negative impact
        st.subheader(f"Bottom Negative Impact on {metric.upper()}")
        negative_df = changes_df.tail(5).sort_values(by="percent_change")
        
        # Create a bar chart
        fig = px.bar(
            negative_df, 
            x="description", 
            y="percent_change",
            color="category",
            labels={"description": "Change", "percent_change": "% Change", "category": "Category"},
            title=f"Bottom 5 Changes by {metric.upper()} Impact"
        )
        st.plotly_chart(fig)
        
        # Show details in table
        st.dataframe(negative_df[["date_str", "category", "description", "percent_change"]])
    
        # Show LLM-powered analysis if available
        st.subheader("AI Analysis")
        
        # Sort changes chronologically for the dropdown
        sorted_changes = sorted(changes_data, key=lambda x: x["date"], reverse=True)
        
        # Create options list with datetime as the sorting key but showing formatted date in display
        change_options = [(f"{x['date_str']} - {x['category']}: {x['description']}", x["change_id"]) 
                         for x in sorted_changes]
        
        selected_option = st.selectbox(
            "Select a change to analyze in depth",
            options=[option[0] for option in change_options],
            format_func=lambda x: x
        )
        
        # Add a button to trigger the analysis
        analyze_button = st.button("Analyze Selected Change")
        
        if analyze_button and selected_option:
            # Get the change_id from the selected option
            selected_change_id = next(option[1] for option in change_options if option[0] == selected_option)
            
            # Analyze the change
            with st.spinner("Analyzing change..."):
                analysis = rag_system.analyze_change_impact(selected_change_id)
            
            # Display the analysis
            if "llm_analysis" in analysis:
                st.write(analysis["llm_analysis"])
            else:
                # If LLM is not available, show a basic analysis
                st.write("Basic analysis (LLM not configured):")
                metrics_matched = sum(1 for m in analysis["impact_analysis"].values() if m["matched_expectation"])
                total_metrics = len(analysis["impact_analysis"])
                
                st.write(f"This change met {metrics_matched}/{total_metrics} of its expected impacts.")
                
                # Show metrics that didn't meet expectations
                if metrics_matched < total_metrics:
                    st.write("Metrics that didn't meet expectations:")
                    for metric_name, metric_data in analysis["impact_analysis"].items():
                        if not metric_data["matched_expectation"]:
                            st.write(f"- {metric_name}: Expected {metric_data['expected']} but got {metric_data['actual']} ({metric_data['percent_change']:.2f}%)")
                        

def show_query_interface(rag_system):
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
                with st.spinner("Analyzing data and generating insight..."):
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
        for concept, description in rag_system.domain_context["concepts"].items():
            st.markdown(f"**{concept}**: {description}")
        
        st.subheader("Metrics")
        for metric, description in rag_system.domain_context["metric_contexts"].items():
            st.markdown(f"**{metric}**: {description}")


def generate_follow_up_suggestions(query):
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

def show_llm_config(rag_system):
    st.header("LLM Configuration")
    
    # Initialize secrets if not present
    if "llm_config" not in st.session_state:
        # Try to load from secrets
        try:
            use_llm = st.secrets.get("USE_LLM", False)
            llm_provider = st.secrets.get("LLM_PROVIDER", "anthropic").lower()
            api_keys = {}
            if "API_KEYS" in st.secrets:
                for provider in ["openai", "anthropic", "google", "huggingface"]:
                    if provider in st.secrets["API_KEYS"]:
                        api_keys[provider] = st.secrets["API_KEYS"][provider]
        except Exception:
            # No secrets found, use defaults
            use_llm = False
            llm_provider = "anthropic"
            api_keys = {}
        
        st.session_state.llm_config = {
            "use_llm": use_llm,
            "llm_provider": llm_provider,
            "api_keys": api_keys
        }
    
    # LLM toggle
    use_llm = st.checkbox("Use LLM for enhanced insights", value=st.session_state.llm_config["use_llm"])
    
    # LLM provider selection
    providers = ["OpenAI", "Anthropic", "Google", "Hugging Face (local)"]
    provider_keys = ["openai", "anthropic", "google", "huggingface"]
    
    try:
        current_index = provider_keys.index(st.session_state.llm_config["llm_provider"])
    except ValueError:
        current_index = 1  # Default to Anthropic
        
    llm_provider = st.selectbox(
        "Select LLM provider",
        providers,
        index=current_index
    )
    
    # API key input
    provider_key = provider_keys[providers.index(llm_provider)]
    current_key = st.session_state.llm_config["api_keys"].get(provider_key, "")
    
    api_key = st.text_input(
        f"{llm_provider} API Key",
        value=current_key,
        type="password"
    )
    
    # Save button
    if st.button("Save LLM Configuration"):
        # Update session state
        st.session_state.llm_config["use_llm"] = use_llm
        st.session_state.llm_config["llm_provider"] = provider_key
        if api_key:  # Only update if not empty
            st.session_state.llm_config["api_keys"][provider_key] = api_key
        
        # Update RAG system
        rag_system.llm_service.is_enabled = use_llm
        if use_llm and api_key:
            # Update API key in LLM service
            rag_system.llm_service.api_key = api_key
            
            if provider_key == "anthropic":
                # Update Anthropic client
                import anthropic # type: ignore
                rag_system.llm_service.client = anthropic.Anthropic(api_key=api_key)
                rag_system.llm_service.model = "claude-3-7-sonnet-20250219"
            elif provider_key == "openai":
                # You would need to update your LLMService class to handle OpenAI
                # For now, just show a message
                st.info("OpenAI support requires LLMService class update")
                
            # Add other providers as needed
        
        st.success("LLM configuration saved!")
        
        # If wanting to persist settings between sessions, you could save to secrets.toml
        # but this requires writing to a file, which should be done carefully
        st.info("Settings saved for this session. For persistent settings, update your .streamlit/secrets.toml file.")