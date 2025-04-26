import streamlit as st
from typing import Dict, Any

from src.rag.core import EnhancedRAGSystem
from .pages.dashboard import show_dashboard
from .pages.search import show_search_interface
from .pages.impact_analysis import show_impact_analysis
from .pages.query_interface import show_query_interface
from .pages.config import show_llm_config

def create_app(rag_system: EnhancedRAGSystem):
    """Create and run the Streamlit application."""
    st.title("Live Ops Analytics System - MVP")
    
    # Sidebar navigation
    nav = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Search Similar Changes", "Impact Analysis", "Query Interface", "LLM Configuration"]
    )
    
    # Route to appropriate page based on navigation selection
    if nav == "Dashboard":
        show_dashboard(rag_system)
    elif nav == "Search Similar Changes":
        show_search_interface(rag_system)
    elif nav == "Impact Analysis":
        show_impact_analysis(rag_system)
    elif nav == "Query Interface":
        show_query_interface(rag_system)
    else:  # LLM Configuration
        show_llm_config(rag_system)
