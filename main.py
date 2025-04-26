# main.py
from data_model import KnowledgeRepository
from sample_data import generate_sample_data
from rag_system import EnhancedRAGSystem
from llm_service import LLMService
from ui import create_app
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