"""
Theme Management System for NSE Options Pricing Tool

This module provides comprehensive theme management including:
- Light/Dark mode support
- NSE branding colors
- User preference persistence
- Dynamic CSS generation
"""

import streamlit as st
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ThemeColors:
    """Theme color configuration"""
    primary: str
    secondary: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    success: str
    warning: str
    error: str
    border: str

class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self):
        self.themes = {
            'light': ThemeColors(
                primary='#2e8b57',           # NSE Green
                secondary='#98FB98',         # Light Green
                background='#ffffff',        # White
                surface='#f8f9fa',          # Light Gray
                text_primary='#2c3333',     # Dark Gray
                text_secondary='#6c757d',   # Medium Gray
                success='#28a745',          # Green
                warning='#ffc107',          # Yellow
                error='#dc3545',            # Red
                border='#e9ecef'            # Light Border
            ),
            'dark': ThemeColors(
                primary='#2e8b57',           # NSE Green
                secondary='#98FB98',         # Light Green
                background='#0e1117',        # Dark Background
                surface='#262730',          # Dark Surface
                text_primary='#fafafa',     # Light Text
                text_secondary='#a6a6a6',   # Medium Light Text
                success='#28a745',          # Green
                warning='#ffc107',          # Yellow
                error='#dc3545',            # Red
                border='#4a4a4a'            # Dark Border
            ),
            'nse_official': ThemeColors(
                primary='#1e4d3b',           # Dark NSE Green
                secondary='#2e8b57',         # NSE Green
                background='#ffffff',        # White
                surface='#f0f8f0',          # Very Light Green
                text_primary='#1e4d3b',     # Dark Green Text
                text_secondary='#4a6741',   # Medium Green Text
                success='#28a745',          # Green
                warning='#ff8c00',          # Orange
                error='#dc3545',            # Red
                border='#c3e6cb'            # Light Green Border
            )
        }
        
        # Initialize theme in session state
        if 'current_theme' not in st.session_state:
            st.session_state.current_theme = 'light'  # Default to light/white theme
    
    def get_theme(self, theme_name: str = None) -> ThemeColors:
        """Get theme colors for specified theme or current theme"""
        if theme_name is None:
            theme_name = st.session_state.get('current_theme', 'light')
        return self.themes.get(theme_name, self.themes['light'])
    
    def set_theme(self, theme_name: str):
        """Set the current theme"""
        if theme_name in self.themes:
            st.session_state.current_theme = theme_name
            st.rerun()
    
    def generate_css(self, theme_name: str = None) -> str:
        """Generate CSS for the specified theme"""
        theme = self.get_theme(theme_name)
        
        return f"""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* CSS Variables for Theme */
            :root {{
                --primary-color: {theme.primary};
                --secondary-color: {theme.secondary};
                --background-color: {theme.background};
                --surface-color: {theme.surface};
                --text-primary: {theme.text_primary};
                --text-secondary: {theme.text_secondary};
                --success-color: {theme.success};
                --warning-color: {theme.warning};
                --error-color: {theme.error};
                --border-color: {theme.border};
            }}
            
            /* Global App Styling */
            .stApp {{
                background: var(--background-color);
                font-family: 'Inter', sans-serif;
                color: var(--text-primary);
            }}
            
            /* Sidebar Styling */
            .css-1d391kg {{
                background: var(--background-color);
                border-right: 1px solid var(--border-color);
            }}
            
            /* Main Content */
            .main {{
                background: var(--background-color);
            }}
            
            /* Theme Toggle Buttons */
            .theme-toggle {{
                display: flex;
                gap: 8px;
                margin-bottom: 1rem;
            }}
            
            .theme-btn {{
                padding: 8px 16px;
                border-radius: 20px;
                border: 1px solid var(--border-color);
                background: var(--surface-color);
                color: var(--text-primary);
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            
            .theme-btn:hover {{
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }}
            
            .theme-btn.active {{
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }}
            
            /* Metric Cards */
            [data-testid="metric-container"] {{
                background: var(--surface-color);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1rem;
                transition: all 0.2s ease;
            }}
            
            [data-testid="metric-container"]:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            
            /* Call Option Styling */
            .call-option [data-testid="stMetricContainer"] {{
                background: linear-gradient(135deg, {theme.primary}20, {theme.primary}10);
                border: 1px solid {theme.primary};
                border-radius: 8px;
            }}
            
            /* Put Option Styling */
            .put-option [data-testid="stMetricContainer"] {{
                background: linear-gradient(135deg, {theme.error}20, {theme.error}10);
                border: 1px solid {theme.error};
                border-radius: 8px;
            }}
            
            /* Market Status */
            .market-status {{
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-weight: 600;
                text-align: center;
                margin-bottom: 1rem;
            }}
            
            .market-open {{
                background: linear-gradient(135deg, {theme.success}20, {theme.success}10);
                color: {theme.success};
                border: 1px solid {theme.success};
            }}
            
            .market-closed {{
                background: linear-gradient(135deg, {theme.error}20, {theme.error}10);
                color: {theme.error};
                border: 1px solid {theme.error};
            }}
            
            /* Buttons */
            .stButton > button {{
                background: var(--primary-color);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0.5rem 1.25rem;
                font-weight: 500;
                transition: all 0.2s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .stButton > button:hover {{
                background: var(--primary-color);
                filter: brightness(110%);
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
            
            /* Input Fields */
            .stNumberInput > div > div > input,
            .stSelectbox > div > div > div,
            .stTextInput > div > div > input {{
                background: var(--background-color);
                border: 1px solid var(--border-color);
                border-radius: 6px;
                color: var(--text-primary);
                transition: border-color 0.2s ease;
            }}
            
            .stNumberInput > div > div > input:focus,
            .stSelectbox > div > div > div:focus,
            .stTextInput > div > div > input:focus {{
                border-color: var(--primary-color);
                box-shadow: 0 0 0 2px {theme.primary}20;
            }}
            
            /* Expanders */
            .streamlit-expanderHeader {{
                background: var(--surface-color);
                border-radius: 6px;
                border: 1px solid var(--border-color);
            }}
            
            /* Charts */
            .stPlotlyChart {{
                background: var(--background-color);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 0.5rem;
            }}
            
            /* DataFrames */
            .stDataFrame {{
                border: 1px solid var(--border-color);
                border-radius: 8px;
                overflow: hidden;
            }}
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background: var(--surface-color);
                border: 1px solid var(--border-color);
                border-radius: 6px 6px 0 0;
                color: var(--text-primary);
            }}
            
            .stTabs [aria-selected="true"] {{
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }}
            
            /* Floating Chat Button */
            .floating-chat-btn {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: var(--primary-color);
                color: white;
                padding: 12px 24px;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 500;
                box-shadow: 0 4px 12px {theme.primary}40;
                display: flex;
                align-items: center;
                gap: 8px;
                z-index: 9999;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
            }}
            
            .floating-chat-btn:hover {{
                background: var(--primary-color);
                filter: brightness(110%);
                transform: translateY(-2px);
                box-shadow: 0 6px 16px {theme.primary}50;
            }}
            
            /* Hide Streamlit Elements */
            #MainMenu {{visibility: hidden;}}
            .stDeployButton {{display:none;}}
            footer {{visibility: hidden;}}
            .stApp > header {{visibility: hidden;}}
            
            /* Responsive Design */
            @media (max-width: 768px) {{
                .theme-toggle {{
                    justify-content: center;
                }}
                
                .floating-chat-btn {{
                    bottom: 10px;
                    right: 10px;
                    padding: 10px 20px;
                }}
            }}
        </style>
        """

def get_current_theme() -> str:
    """Get the current theme name"""
    return st.session_state.get('current_theme', 'light')

def apply_theme(theme_manager: ThemeManager, theme_name: str = None):
    """Apply the specified theme or current theme"""
    css = theme_manager.generate_css(theme_name)
    st.markdown(css, unsafe_allow_html=True)

def create_theme_selector(theme_manager: ThemeManager):
    """Create theme selector UI component"""
    current_theme = get_current_theme()
    
    st.markdown("""
    <div class="theme-toggle">
        <span style="font-weight: 500; margin-right: 8px;">Theme:</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("☀️ Light", key="light_theme", help="Light theme"):
            theme_manager.set_theme('light')
    
    with col2:
        if st.button("🌙 Dark", key="dark_theme", help="Dark theme"):
            theme_manager.set_theme('dark')
    
    with col3:
        if st.button("🟢 NSE", key="nse_theme", help="NSE official theme"):
            theme_manager.set_theme('nse_official')
    
    # Show current theme indicator
    theme_names = {
        'light': '☀️ Light',
        'dark': '🌙 Dark', 
        'nse_official': '🟢 NSE Official'
    }
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-secondary);">
        Current: {theme_names.get(current_theme, current_theme)}
    </div>
    """, unsafe_allow_html=True)