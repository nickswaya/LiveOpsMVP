import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from src.rag.core import EnhancedRAGSystem

def show_dashboard(rag_system: EnhancedRAGSystem):
    """Display the main analytics dashboard."""
    st.header("Live Ops Analytics Dashboard")
    
    # Get all changes as dictionaries
    changes = [change.to_dict() for change in rag_system.knowledge_repo.changes]
    change_count = len(changes)
    
    # Generate category stats from dictionaries
    categories = {}
    for change in changes:
        category = change["category"]
        if category in categories:
            categories[category] += 1
        else:
            categories[category] = 1
    
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
    
    # Show recent changes using dictionary data
    st.subheader("Recent Changes")
    # Sort changes by timestamp (convert ISO string to datetime for sorting)
    recent_changes = sorted(
        changes,
        key=lambda x: datetime.fromisoformat(x["timestamp"]),
        reverse=True
    )[:10]
    
    recent_data = []
    for change in recent_changes:
        # Get metrics as dictionaries
        metrics = rag_system.knowledge_repo.get_metrics_for_change(change["change_id"])
        # Find revenue impact from dictionary metrics
        revenue_impact = next(
            (m["percent_change"] for m in metrics if m["metric_name"] == "revenue"),
            0
        )
        
        # Format data using dictionary access
        recent_data.append({
            "Date": datetime.fromisoformat(change["timestamp"]).strftime("%Y-%m-%d"),
            "Category": change["category"],
            "Description": change["description"],
            "Revenue Impact": f"{'+' if revenue_impact > 0 else ''}{revenue_impact:.2f}%"
        })
    
    recent_df = pd.DataFrame(recent_data)
    st.dataframe(recent_df)
