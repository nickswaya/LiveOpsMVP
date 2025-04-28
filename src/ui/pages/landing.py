import streamlit as st
from pathlib import Path

def show_landing_page():
    """Display the ATLAS landing page with custom styling."""
    
    # Load custom CSS
    st.markdown("""
    <style>
    /* Base styles for dark mode compatibility */
    :root {
        --text-color: #1E1E1E;
        --bg-color: #FFFFFF;
        --card-bg: #FFFFFF;
        --card-text: #333333;
    }

    [data-theme="dark"] {
        --text-color: #FFFFFF;
        --bg-color: #1E1E1E;
        --card-bg: #2D2D2D;
        --card-text: #FFFFFF;
    }

    /* Hero section */
    .hero-section {
        display: flex;
        align-items: center;
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--card-bg) 100%);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: var(--text-color);
    }

    .hero-content {
        flex: 3;
        padding: 2rem;
    }

    .hero-image {
        flex: 2;
        text-align: center;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.8rem;
        font-weight: 500;
        margin-bottom: 1rem;
        color: var(--text-color);
    }

    .hero-slogan {
        font-size: 1.2rem;
        font-style: italic;
        color: var(--text-color);
        opacity: 0.8;
        margin-bottom: 1.5rem;
    }

    .hero-description {
        font-size: 1.1rem;
        color: var(--text-color);
        opacity: 0.9;
        line-height: 1.6;
    }

    /* Value cards */
    .value-cards {
        display: flex;
        justify-content: space-between;
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .value-card {
        flex: 1;
        background: var(--card-bg);
        color: var(--card-text);
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .value-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }

    .value-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    /* Section titles */
    .section-title {
        position: relative;
        font-size: 2rem;
        font-weight: 600;
        margin: 2.5rem 0 1.5rem;
        padding-bottom: 0.5rem;
    }

    .section-title:after {
        content: '';
        position: absolute;
        left: 0;
        bottom: 0;
        height: 3px;
        width: 100px;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
    }

    /* Feature section */
    .feature-section {
        background: var(--card-bg);
        color: var(--card-text);
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
    }

    .feature-item {
        padding: 1.5rem;
        background: var(--card-bg);
        color: var(--card-text);
        border-radius: 8px;
        transition: transform 0.3s ease;
    }

    .feature-item:hover {
        transform: translateY(-5px);
    }

    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        color: #4CAF50;
    }

    /* RAG explanation */
    .rag-comparison {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin: 2rem 0;
    }

    .rag-card {
        background: var(--card-bg);
        color: var(--card-text);
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .rag-card h3 {
        color: var(--text-color);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--text-color);
        opacity: 0.8;
    }

    /* Call to action */
    .cta-section {
        background: linear-gradient(135deg, #4CAF50 0%, #2196F3 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin: 2rem 0;
    }

    .cta-title {
        font-size: 2rem;
        margin-bottom: 1rem;
    }

    .cta-description {
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .cta-button {
        display: inline-block;
        padding: 1rem 2rem;
        background: white;
        color: #4CAF50;
        text-decoration: none;
        border-radius: 5px;
        font-weight: 600;
        transition: transform 0.3s ease;
    }

    .cta-button:hover {
        transform: translateY(-2px);
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .hero-section {
            flex-direction: column;
            text-align: center;
        }

        .value-cards {
            flex-direction: column;
        }

        .rag-comparison {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a container for the hero section
    hero_container = st.container()
    
    with hero_container:
        # Split the hero section into two columns
        col1, col2 = st.columns([3, 2])  # 3:2 ratio to match the flex ratio in CSS
        
        with col1:
            # Hero content
            st.markdown("""
            <div class="hero-content" style="color: var(--text-color);">
                <h1 class="hero-title">ATLAS</h1>
                <h2 class="hero-subtitle" style="color: var(--text-color);">Analytics Tracking and Learning System</h2>
                <p class="hero-slogan">Shouldering the knowledge of today to empower the decisions of tomorrow.</p>
                <div class="hero-description">
                    Transforming LiveOps with AI-powered analytics that understands context, 
                    learns from history, and provides actionable insights.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Hero image - using Streamlit's native image function
            image_path = Path("static/images/atlas.png")
            st.image(image_path, use_container_width=True)
    
    # Apply hero section styling to the container
    st.markdown("""
    <style>
    /* Apply hero section styling to the Streamlit container */
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--card-bg) 100%);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
    }

    /* Style Streamlit markdown text */
    .stMarkdown {
        color: var(--text-color) !important;
    }
    
    /* Style Streamlit headers */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-color) !important;
    }

    /* Style Streamlit paragraphs and lists */
    .stMarkdown p, .stMarkdown li {
        color: var(--text-color) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Value Proposition
    st.markdown("""
    <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px;">
        <h2 class='section-title' style='color: var(--text-color); margin-top: 0;'>Why ATLAS?</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="value-cards" style="margin-top: 2rem;">
        <div class="value-card">
            <div class="value-icon">🔍</div>
            <h3 style="color: var(--text-color);">Knowledge Preservation</h3>
            <p style="color: var(--text-color);">Never lose valuable insights about what works and what doesn't</p>
        </div>
        <div class="value-card">
            <div class="value-icon">📊</div>
            <h3 style="color: var(--text-color);">Data-Driven Decisions</h3>
            <p style="color: var(--text-color);">Make confident decisions backed by comprehensive analysis of historical performance.</p>
        </div>
        <div class="value-card">
            <div class="value-icon">🧠</div>
            <h3 style="color: var(--text-color);">Pattern Recognition</h3>
            <p style="color: var(--text-color);">Identify successful patterns across different types of changes and game features.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # RAG Explanation
    st.markdown("""
    <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px;">
        <h2 class='section-title' style='color: var(--text-color); margin-top: 0;'>How It Works</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <p style="color: var(--text-color); margin: 0;">
            ATLAS uses advanced Retrieval-Augmented Generation (RAG) technology to deliver insights that traditional 
            analytics tools can't provide. Think of it as having a senior analyst with perfect memory of every 
            change ever made to our game, and the understanding of how they all fit together.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # RAG comparison using HTML for consistent styling
    st.markdown("""
    <div class="rag-comparison">
        <div class="rag-card">
            <h3 style="color: var(--text-color);">Traditional Analytics</h3>
            <ul style="color: var(--text-color);">
                <li>Limited to predefined queries and reports</li>
                <li>Relies on 'Tribal Knowledge' of what works and what doesn't</li>
                <li>Changes and impacts are isolated and rely stakeholders to remember and connect the dots</li>
                <li>Often requires SQL or Tableau, gatekeeping team members</li>
            </ul>
        </div>
        <div class="rag-card">
            <h3 style="color: var(--text-color);">ATLAS with RAG</h3>
            <ul style="color: var(--text-color);">
                <li>Answers natural language questions</li>
                <li>Learns from historical context</li>
                <li>Connects related changes and impacts</li>
                <li>Accessible to all team members</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Overview
    st.markdown("""
    <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px;">
        <h2 class='section-title' style='color: var(--text-color); margin-top: 0;'>Explore ATLAS</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Overview using Streamlit columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <h3 style="color: var(--text-color);">📊 Dashboard</h3>
            <p style="color: var(--text-color);">Get a bird's-eye view of your live operations performance with comprehensive metrics and trends.</p>
            <p style="color: var(--text-color); font-size: 0.8rem; opacity: 0.8;">Perfect for: Daily overview and monitoring</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <h3 style="color: var(--text-color);">📈 Impact Analysis</h3>
            <p style="color: var(--text-color);">Analyze how specific changes affect your key metrics with detailed breakdowns.</p>
            <p style="color: var(--text-color); font-size: 0.8rem; opacity: 0.8;">Perfect for: Performance evaluation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <h3 style="color: var(--text-color);">🔍 Search Similar Changes</h3>
            <p style="color: var(--text-color);">Find and learn from similar changes made in the past to predict potential outcomes.</p>
            <p style="color: var(--text-color); font-size: 0.8rem; opacity: 0.8;">Perfect for: Planning new changes</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <h3 style="color: var(--text-color);">❓ Query Interface</h3>
            <p style="color: var(--text-color);">Ask questions in plain English and get AI-powered insights from your data.</p>
            <p style="color: var(--text-color); font-size: 0.8rem; opacity: 0.8;">Perfect for: Deep dive analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title">Ready to Transform Your Game Operations?</h2>
        <p class="cta-description">
            Start making data-driven decisions with confidence using ATLAS's powerful analytics capabilities.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Using Streamlit button instead of HTML button for functionality
    if st.button("Explore Dashboard →", use_container_width=True):
        # Set navigation state to Dashboard
        st.session_state.navigation = "Dashboard"
        # Force a rerun to update the navigation
        st.rerun()
