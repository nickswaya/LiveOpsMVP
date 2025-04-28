import streamlit as st
from typing import Dict, Any

from src.rag.core import EnhancedRAGSystem
from .pages.landing import show_landing_page
from .pages.dashboard import show_dashboard
from .pages.search import show_search_interface
from .pages.impact_analysis import show_impact_analysis
from .pages.query_interface import show_query_interface
from .pages.config import show_llm_config

def create_app(rag_system: EnhancedRAGSystem):
    """Create and run the Streamlit application."""
    
    # Initialize navigation state if not present
    if "navigation" not in st.session_state:
        st.session_state.navigation = "Home"
    
    # Sidebar navigation
    nav = st.sidebar.radio(
        "Navigation",
        ["Home", "Dashboard", "Search Similar Changes", "Impact Analysis", "Query Interface", "LLM Configuration"],
        key="nav",
        index=["Home", "Dashboard", "Search Similar Changes", "Impact Analysis", "Query Interface", "LLM Configuration"].index(st.session_state.navigation)
    )
    
    # Update navigation state when sidebar selection changes
    if nav != st.session_state.navigation:
        st.session_state.navigation = nav
        st.rerun()
    
    # Route to appropriate page based on navigation state
    if st.session_state.navigation == "Home":
        show_landing_page()
    elif st.session_state.navigation == "Dashboard":
        show_dashboard(rag_system)
    elif st.session_state.navigation == "Search Similar Changes":
        show_search_interface(rag_system)
    elif st.session_state.navigation == "Impact Analysis":
        show_impact_analysis(rag_system)
    elif st.session_state.navigation == "Query Interface":
        show_query_interface(rag_system)
    else:  # LLM Configuration
        show_llm_config(rag_system)
