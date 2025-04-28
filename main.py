# main.py
from src.data.repository import KnowledgeRepository
from src.data.sample_generator import generate_sample_data
from src.rag.core import EnhancedRAGSystem
from src.llm.service import LLMService
from src.ui.app import create_app
import streamlit as st
import os

def main():
    # Initialize session state for persistent objects
    if 'repo' not in st.session_state:
        print("Generating sample data...")
        st.session_state.repo = generate_sample_data(100)
        print(f"Generated {len(st.session_state.repo.changes)} changes with metrics")
    
    if 'llm_service' not in st.session_state:
        print("Initializing LLM service...")
        st.session_state.llm_service = LLMService()
    
    if 'rag' not in st.session_state:
        print("Initializing RAG system...")
        st.session_state.rag = EnhancedRAGSystem(
            knowledge_repo=st.session_state.repo,
            llm_service=st.session_state.llm_service,
            config_dir="config"  # Add config directory path
        )
    
    # Use the persistent objects from session state
    print("Starting application...")
    create_app(st.session_state.rag)

if __name__ == "__main__":
    main()
