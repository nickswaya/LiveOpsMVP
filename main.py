# main.py
from src.data.repository import KnowledgeRepository
from src.data.sample_generator import generate_sample_data
from src.rag.core import EnhancedRAGSystem
from src.llm.service import LLMService
from src.ui.app import create_app
import streamlit as st
import os

def main():
    # Generate sample data
    print("Generating sample data...")
    repo = generate_sample_data(100)
    print(f"Generated {len(repo.changes)} changes with metrics")
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Create RAG system with LLM service
    print("Initializing RAG system...")
    rag = EnhancedRAGSystem(repo, llm_service)
    
    # Start the UI
    print("Starting application...")
    create_app(rag)

if __name__ == "__main__":
    main()
