import streamlit as st

def inject_custom_css():
    """Injects global CSS styles for the dashboard."""
    st.markdown("""
    <style>
        /* Global Font & Theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Remove default Streamlit padding */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
        }
        
        /* Premium Card Hover Effect */
        .vessel-card {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .vessel-card:hover {
            transform: translateY(-2px);
        }
        
        /* Scrollbar customization */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.02);
        }
        ::-webkit-scrollbar-thumb {
            background: #555;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #777;
        }
    </style>
    """, unsafe_allow_html=True)
