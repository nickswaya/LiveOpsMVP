# main.py
from data_model import LiveOpsChange, MetricMeasurement, KnowledgeRepository
from sample_data import generate_sample_data
from rag_system import RAGSystem
from ui import create_app
import sys
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit'])
def main():
    # Generate sample data
    print("Generating sample data...")
    repo = generate_sample_data(50)
    print(f"Generated {len(repo.changes)} changes with metrics")
    
    # Create RAG system
    print("Initializing RAG system...")
    rag = RAGSystem(repo)
    
    # Start the UI
    print("Starting application...")
    create_app(rag)

if __name__ == "__main__":
    main()