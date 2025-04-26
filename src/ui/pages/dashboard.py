import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from src.rag.core import EnhancedRAGSystem

def show_dashboard(rag_system: EnhancedRAGSystem):
    """Display the main analytics dashboard."""
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
