import streamlit as st
from typing import Dict, Any

from src.rag.core import EnhancedRAGSystem

def show_llm_config(rag_system: EnhancedRAGSystem):
    """Display the LLM configuration interface."""
    st.header("LLM Configuration")
    
    # Initialize secrets if not present
    if "llm_config" not in st.session_state:
        # Try to load from secrets
        try:
            use_llm = st.secrets.get("USE_LLM", False)
            llm_provider = st.secrets.get("LLM_PROVIDER", "anthropic").lower()
            api_keys = {}
            if "API_KEYS" in st.secrets:
                for provider in ["openai", "anthropic", "google", "huggingface"]:
                    if provider in st.secrets["API_KEYS"]:
                        api_keys[provider] = st.secrets["API_KEYS"][provider]
        except Exception:
            # No secrets found, use defaults
            use_llm = False
            llm_provider = "anthropic"
            api_keys = {}
        
        st.session_state.llm_config = {
            "use_llm": use_llm,
            "llm_provider": llm_provider,
            "api_keys": api_keys
        }
    
    # LLM toggle
    use_llm = st.checkbox("Use LLM for enhanced insights", value=st.session_state.llm_config["use_llm"])
    
    # LLM provider selection
    providers = ["OpenAI", "Anthropic", "Google", "Hugging Face (local)"]
    provider_keys = ["openai", "anthropic", "google", "huggingface"]
    
    try:
        current_index = provider_keys.index(st.session_state.llm_config["llm_provider"])
    except ValueError:
        current_index = 1  # Default to Anthropic
        
    llm_provider = st.selectbox(
        "Select LLM provider",
        providers,
        index=current_index
    )
    
    # API key input
    provider_key = provider_keys[providers.index(llm_provider)]
    current_key = st.session_state.llm_config["api_keys"].get(provider_key, "")
    
    api_key = st.text_input(
        f"{llm_provider} API Key",
        value=current_key,
        type="password"
    )
    
    # Save button
    if st.button("Save LLM Configuration"):
        # Update session state
        st.session_state.llm_config["use_llm"] = use_llm
        st.session_state.llm_config["llm_provider"] = provider_key
        if api_key:  # Only update if not empty
            st.session_state.llm_config["api_keys"][provider_key] = api_key
        
        # Update RAG system
        rag_system.llm_service.is_enabled = use_llm
        if use_llm and api_key:
            # Update API key in LLM service
            rag_system.llm_service.api_key = api_key
            
            if provider_key == "anthropic":
                # Update Anthropic client
                import anthropic # type: ignore
                rag_system.llm_service.client = anthropic.Anthropic(api_key=api_key)
                rag_system.llm_service.model = "claude-3-7-sonnet-20250219"
            elif provider_key == "openai":
                # You would need to update your LLMService class to handle OpenAI
                # For now, just show a message
                st.info("OpenAI support requires LLMService class update")
                
            # Add other providers as needed
        
        st.success("LLM configuration saved!")
        
        # If wanting to persist settings between sessions, you could save to secrets.toml
        # but this requires writing to a file, which should be done carefully
        st.info("Settings saved for this session. For persistent settings, update your .streamlit/secrets.toml file.")
