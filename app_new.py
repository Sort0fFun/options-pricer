"""
NSE Options Pricing Tool - Main App
"""

import streamlit as st
from datetime import datetime
from src.core.pricing.contracts import NSE_FUTURES

def display_nse_charges():
    """Display NSE charges with checkboxes and calculate total."""
    st.sidebar.markdown("### 💰 NSE Charges")
    
    # Initialize charges in session state if not present
    if 'nse_charges' not in st.session_state:
        st.session_state.nse_charges = {
            'clearing_fee': True,
            'trading_levy': True,
            'investor_protection': True
        }
    
    # Create checkboxes for each charge with unique keys
    st.session_state.nse_charges['clearing_fee'] = st.sidebar.checkbox(
        "Clearing Fee (0.14%)", 
        value=st.session_state.nse_charges['clearing_fee'],
        key="nse_clearing_fee"
    )
    
    st.session_state.nse_charges['trading_levy'] = st.sidebar.checkbox(
        "Trading Levy (0.12%)", 
        value=st.session_state.nse_charges['trading_levy'],
        key="nse_trading_levy"
    )
    
    st.session_state.nse_charges['investor_protection'] = st.sidebar.checkbox(
        "Investor Protection (0.02%)", 
        value=st.session_state.nse_charges['investor_protection'],
        key="nse_investor_protection"
    )
    
    # Calculate total charges
    total_charges = (
        (0.0014 if st.session_state.nse_charges['clearing_fee'] else 0) +
        (0.0012 if st.session_state.nse_charges['trading_levy'] else 0) +
        (0.0002 if st.session_state.nse_charges['investor_protection'] else 0)
    )
    
    if total_charges > 0:
        st.sidebar.markdown(
            f"""<div style='background-color: #2e8b57; color: white; padding: 8px; border-radius: 5px; margin-top: 10px;'>
                <strong>Total Charges</strong>: {total_charges:.2%}
            </div>""",
            unsafe_allow_html=True
        )

def create_sidebar():
    """Create sidebar navigation."""
    st.sidebar.title("NSE Options Tool")
    
    # Theme selector with unique key
    theme = st.sidebar.selectbox("Theme", ["Light", "Dark"], key="app_theme_selector")
    
    # Apply seagreen theme
    if theme == "Dark":
        st.markdown("""
            <style>
                .stApp { background-color: #0E1117; }
                .main-header { background-color: #262730; }
                .element-container { color: #FAFAFA; }
                .stButton>button { background-color: #2e8b57 !important; color: white !important; }
                .stSelectbox>div>div { border-color: #2e8b57 !important; }
                .stTextInput>div>div { border-color: #2e8b57 !important; }
                div[data-baseweb="select"] { border-color: #2e8b57 !important; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                .stApp { background-color: #FFFFFF; }
                .main-header { background-color: #F0F2F6; }
                .stButton>button { background-color: #2e8b57 !important; color: white !important; }
                .stSelectbox>div>div { border-color: #2e8b57 !important; }
                .stTextInput>div>div { border-color: #2e8b57 !important; }
                div[data-baseweb="select"] { border-color: #2e8b57 !important; }
            </style>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Page navigation
    pages = [
        "🏠 Home",
        "Option Pricing", 
        "Greeks Analysis",
        "Strategy Builder",
        "ML Volatility",
        "Market Data",
        "Educational Hub"
    ]
    
    selected_page = st.sidebar.radio("Navigation", pages, key="nav_pages")
    st.session_state.page = selected_page.split(" ", 1)[1]  # Remove emoji
    
    st.sidebar.markdown("---")
    
    # Market status with seagreen theme
    st.sidebar.subheader("📍 Market Status")
    
    # Check if market is open (9:30 AM - 3 PM EAT)
    now = datetime.now()
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=15, minute=0, second=0)
    is_market_open = market_open <= now <= market_close and now.weekday() < 5
    
    # Custom market status with seagreen color
    if is_market_open:
        st.sidebar.markdown("""
            <div style='padding: 10px; border-radius: 5px; background-color: #2e8b57; color: white; text-align: center; margin-bottom: 10px;'>
                🟢 NSE Market OPEN
            </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
            <div style='padding: 10px; border-radius: 5px; background-color: #3d3d3d; color: white; text-align: center; margin-bottom: 10px;'>
                ⭕ NSE Market CLOSED
            </div>
        """, unsafe_allow_html=True)
    
    # Market timing info with theme-aware styling
    st.sidebar.markdown(f"""
        <div style='padding: 10px; border-radius: 5px; background-color: {'#1a472a' if theme == 'Dark' else '#e6f3ed'}; margin-bottom: 10px;'>
            <p style='margin: 0; color: {'white' if theme == 'Dark' else 'black'};'>
                <strong>Time</strong>: {now.strftime('%H:%M EAT')}<br>
                <strong>Date</strong>: {now.strftime('%Y-%m-%d')}<br>
                <small>Trading Hours: 9:30 AM - 3:00 PM EAT</small>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick contract info
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Contract Info")
    
    # Show contract information with NSE charges
    if 'pricing_inputs' in st.session_state:
        contract = st.session_state.pricing_inputs['contract']
        if contract in NSE_FUTURES:
            contract_info = NSE_FUTURES[contract]
            st.sidebar.write(f"**{contract}**: {contract_info.get('name', 'N/A')}")
            st.sidebar.write(f"**Sector**: {contract_info.get('sector', 'N/A')}")
            st.sidebar.write(f"**Contract Size**: {contract_info.get('contract_size', 'N/A')}")
            
            # Display NSE charges section
            st.sidebar.markdown("---")
            display_nse_charges()

# Initialize sidebar
create_sidebar()