import streamlit as st
import pandas as pd

from src.rag.core import EnhancedRAGSystem

def show_search_interface(rag_system: EnhancedRAGSystem):
    """Display the search interface for finding similar changes."""
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
