import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from src.rag.core import EnhancedRAGSystem

def show_impact_analysis(rag_system: EnhancedRAGSystem):
    """Display the impact analysis interface."""
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
