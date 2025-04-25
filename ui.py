import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def create_app(rag_system):
    st.title("Live Ops Analytics System - MVP")
    
    # Sidebar navigation
    nav = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Search Similar Changes", "Impact Analysis", "Query Interface"]
    )
    
    if nav == "Dashboard":
        show_dashboard(rag_system)
    elif nav == "Search Similar Changes":
        show_search_interface(rag_system)
    elif nav == "Impact Analysis":
        show_impact_analysis(rag_system)
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
                "date": change.timestamp.strftime("%Y-%m-%d"),
                "category": change.category,
                "description": change.description,
                "before": impact.before_value,
                "after": impact.after_value,
                "percent_change": impact.percent_change
            })
    
    changes_df = pd.DataFrame(changes_data)
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
    st.dataframe(positive_df[["date", "category", "description", "percent_change"]])
    
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
    st.dataframe(negative_df[["date", "category", "description", "percent_change"]])

def show_query_interface(rag_system):
    st.header("Natural Language Query Interface")
    
    st.write("""
    Ask questions about changes and their impacts. For example:
    - What changes are similar to BOGO sale?
    - What changes had the biggest impact on revenue?
    - Show me events that affected retention
    """)
    
    query = st.text_input("Enter your question")
    
    if query:
        insight = rag_system.generate_insight(query)
        st.subheader("Insight")
        st.write(insight)