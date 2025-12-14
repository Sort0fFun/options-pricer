"""
OPTIONS ON FUTURES CALCULATOR

A comprehensive tool for pricing and analyzing options on futures contracts
using the Black-76 model, with integrated ML predictions and educational features.
Supports NSE futures contracts with real-time market data and analysis.
"""

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import pytz

# Configure page
st.set_page_config(
    page_title="OPTIONS ON FUTURES CALCULATOR",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
def get_theme_css(theme='light'):
    """Return CSS based on selected theme."""
    if theme == 'dark':
        return """
<style>
    /* Dark Theme */
    .main-header {
        background: linear-gradient(135deg, #1a4d2e 0%, #0d261f 100%);
        padding: 2rem;
        border-radius: 10px;
        color: #e8f5e9;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-card {
        background-color: rgba(26, 77, 46, 0.2);
        border: 1px solid #2e8b57;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Main app background */
    .stApp {
        background-color: #0a0e0d;
        color: #e8f5e9;
    }
    
    /* Header styling for dark mode */
    .header-container {
        background: linear-gradient(135deg, #0d261f 0%, #1a4d2e 100%) !important;
    }
    
    /* Navigation buttons in dark mode */
    .stButton button {
        background-color: transparent !important;
        border: 1px solid #2e8b57 !important;
        color: #e8f5e9 !important;
    }
    .stButton button:hover {
        background-color: rgba(46, 139, 87, 0.3) !important;
        border-color: #4ade80 !important;
    }
    
    /* Sidebar dark theme */
    section[data-testid="stSidebar"] {
        background-color: #0f1410 !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #0f1410 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e8f5e9 !important;
    }
    section[data-testid="stSidebar"] label {
        color: #e8f5e9 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stNumberInput label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #e8f5e9 !important;
    }
    
    /* Sidebar inputs */
    section[data-testid="stSidebar"] input {
        background-color: #1a2520 !important;
        color: #e8f5e9 !important;
        border-color: #2e8b57 !important;
    }
    section[data-testid="stSidebar"] input::placeholder {
        color: #a0b8a8 !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] select {
        background-color: #1a2520 !important;
        color: #e8f5e9 !important;
    }
    
    /* Main content text inputs in dark mode */
    .stTextInput input {
        background-color: #1a2520 !important;
        color: #e8f5e9 !important;
        border-color: #2e8b57 !important;
    }
    .stTextInput input::placeholder {
        color: #a0b8a8 !important;
        opacity: 1 !important;
    }
    .stTextInput label {
        color: #e8f5e9 !important;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton button {
        background-color: #1a4d2e !important;
        color: #e8f5e9 !important;
        border-color: #2e8b57 !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #2e8b57 !important;
        border-color: #4ade80 !important;
    }
    
    /* Radio buttons in sidebar */
    section[data-testid="stSidebar"] .stRadio > div {
        background-color: #1a2520 !important;
        padding: 0.5rem;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #e8f5e9 !important;
    }
    
    /* Slider styling - dark mode */
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        color: #e8f5e9 !important;
    }
    .stSlider [data-baseweb="slider"] > div > div {
        background-color: #1A4D2E !important;
    }
    .stSlider [data-baseweb="slider"] > div > div > div {
        background-color: #1A4D2E !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    
    /* Radio button styling - dark mode */
    .stRadio [role="radiogroup"] label > div:first-child {
        border-color: #1A4D2E !important;
    }
    .stRadio [role="radiogroup"] label[data-checked="true"] > div:first-child {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    .stRadio [role="radiogroup"] label[data-checked="true"] > div:first-child::after {
        background-color: white !important;
    }
    
    /* Checkbox styling - dark mode */
    .stCheckbox [data-baseweb="checkbox"] > div:first-child {
        border-color: #1A4D2E !important;
    }
    .stCheckbox [data-baseweb="checkbox"] input:checked + div {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    .stCheckbox label span[data-testid="stCheckbox"] > div {
        border-color: #1A4D2E !important;
    }
    .stCheckbox input[type="checkbox"]:checked + div {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    [data-testid="stCheckbox"] > label > div:first-child {
        border-color: #1A4D2E !important;
    }
    [data-testid="stCheckbox"] > label > div:first-child[aria-checked="true"] {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    
    .stMarkdown {
        color: #e8f5e9;
    }
    div[data-testid="stMetricValue"] {
        color: #4ade80;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a0a0a0;
        background-color: #2a2a2a;
    }
    .stTabs [aria-selected="true"] {
        color: #4ade80;
        border-bottom-color: #2e8b57;
    }
    .theme-badge {
        background: linear-gradient(135deg, #1a4d2e 0%, #0d261f 100%);
        color: #4ade80;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    /* Divider in dark mode */
    section[data-testid="stSidebar"] hr {
        border-color: #2e8b57 !important;
    }
    
    /* Mobile Responsive Styles - Dark Mode */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem !important;
        }
        .main-header h2 {
            font-size: 1.2rem !important;
        }
        .header-container {
            padding: 0.5rem !important;
        }
        .header-brand {
            font-size: 0.9rem !important;
        }
    }
</style>
"""
    else:  # light theme
        return """
<style>
    /* Light Theme */
    .main-header {
        background: linear-gradient(135deg, #2e8b57 0%, #1e6b47 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: rgba(46, 139, 87, 0.1);
        border: 1px solid #2e8b57;
        border-radius: 8px;
        padding: 1rem;
    }
    .stApp {
        background-color: #ffffff;
    }
    
    /* Sidebar light theme */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #f8f9fa !important;
    }
    
    /* Slider styling - light mode */
    .stSlider [data-baseweb="slider"] > div > div {
        background-color: #1A4D2E !important;
    }
    .stSlider [data-baseweb="slider"] > div > div > div {
        background-color: #1A4D2E !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    
    /* Radio button styling - light mode */
    .stRadio [role="radiogroup"] label > div:first-child {
        border-color: #1A4D2E !important;
    }
    .stRadio [role="radiogroup"] label[data-checked="true"] > div:first-child {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    
    /* Checkbox styling - light mode */
    .stCheckbox [data-baseweb="checkbox"] > div:first-child {
        border-color: #1A4D2E !important;
    }
    .stCheckbox [data-baseweb="checkbox"] input:checked + div {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    [data-testid="stCheckbox"] > label > div:first-child {
        border-color: #1A4D2E !important;
    }
    [data-testid="stCheckbox"] > label > div:first-child[aria-checked="true"] {
        background-color: #1A4D2E !important;
        border-color: #1A4D2E !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #2e8b57;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab"] {
        color: #495057;
    }
    .stTabs [aria-selected="true"] {
        color: #2e8b57;
        border-bottom-color: #2e8b57;
    }
    .theme-badge {
        background: linear-gradient(135deg, #2e8b57 0%, #1e6b47 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    /* Mobile Responsive Styles */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem !important;
        }
        .main-header h2 {
            font-size: 1.2rem !important;
        }
        .header-container {
            padding: 0.5rem !important;
        }
        .header-brand {
            font-size: 0.9rem !important;
        }
        /* Stack columns on mobile */
        [data-testid="column"] {
            min-width: 100% !important;
        }
    }
</style>
"""

# Initialize session state for theme BEFORE using it
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# Import our modules
MODULES_AVAILABLE = False
CHATBOT_AVAILABLE = False
try:
    from src.core.pricing.black76 import Black76Pricer
    from src.core.greeks.calculator import GreeksCalculator
    # from src.ml.volatility.predictor import VolatilityPredictor
    # from src.ml.regime.detector import RegimeDetector
    from src.core.pricing.contracts import NSE_FUTURES
    from src.visualization.styles import get_plotly_layout
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Module import error: {e}")
    MODULES_AVAILABLE = False

try:
    from src.web.chatbot import FlaviaAIBot, render_flavia_chat
    CHATBOT_AVAILABLE = True
except ImportError as e:
    logger.error(f"Chatbot import error: {e}")
    CHATBOT_AVAILABLE = False

# Helper functions
def format_currency(amount, currency='KES'):
    """Format amount as currency string."""
    return f"{currency} {amount:,.2f}"

def get_market_status():
    """Check if NSE market is currently open."""
    eat = pytz.timezone('Africa/Nairobi')
    now = datetime.now(eat)
    current_time = now.time()

    # NSE trading hours: 9:00 AM to 3:00 PM EAT, Monday to Friday
    market_open = time(9, 0)
    market_close = time(15, 0)

    if now.weekday() >= 5:  # Weekend
        return "CLOSED", "Market is closed for the weekend"
    elif market_open <= current_time <= market_close:
        next_close = eat.localize(datetime.combine(now.date(), market_close))
        time_until_close = next_close - now
        hours, remainder = divmod(time_until_close.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return "OPEN", f"Closes in {hours}h {minutes}m"
    else:
        if current_time < market_open:
            next_open = eat.localize(datetime.combine(now.date(), market_open))
        else:
            next_open = eat.localize(datetime.combine(now.date() + timedelta(days=1), market_open))
        time_until_open = next_open - now
        hours, remainder = divmod(time_until_open.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return "CLOSED", f"Opens in {hours}h {minutes}m"

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Theme already initialized earlier in the file

if 'pricing_inputs' not in st.session_state:
    st.session_state.pricing_inputs = {
        'contract': 'SCOM',
        'futures_price': 100.0,
        'strike_price': 105.0,
        'time_to_expiry': 30,  # days
        'volatility': 0.20,
        'risk_free_rate': 0.10,
        'option_type': 'Call',
        'include_fees': False
    }

# Display market status at the top
status, status_msg = get_market_status()

# Professional Website Header Navigation Bar
st.markdown("""
<style>
/* Header Navigation Styles */
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background: linear-gradient(135deg, #1a4d2e 0%, #2e8b57 100%);
    border-radius: 8px;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.header-brand {
    font-size: 1.25rem;
    font-weight: 700;
    color: white;
    margin: 0;
}
.header-nav {
    display: flex;
    gap: 0.25rem;
}
.header-status {
    color: white;
    font-size: 0.85rem;
}
/* Hide default streamlit button styling for nav */
div[data-testid="column"] .nav-btn button {
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.85) !important;
    padding: 0.5rem 1rem !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
div[data-testid="column"] .nav-btn button:hover {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
}
div[data-testid="column"] .nav-btn-active button {
    background: rgba(255,255,255,0.25) !important;
    color: white !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# Navigation pages list (Greeks Analysis hidden)
nav_pages = ["Home", "Option Pricing", "ML Predictions", "Flavia AI", "Settings"]

# Create header with brand, navigation, and status
st.markdown("""
<div class="header-container">
    <div class="header-brand">NSE Options Calculator</div>
    <div class="header-status"></div>
</div>
""", unsafe_allow_html=True)

# Navigation row with buttons
nav_cols = st.columns([1, 1, 1, 1, 1, 1.5, 0.8])

for idx, page_name in enumerate(nav_pages):
    with nav_cols[idx]:
        is_active = st.session_state.page == page_name
        btn_class = "nav-btn-active" if is_active else "nav-btn"
        st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
        if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
            st.session_state.page = page_name
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Market status in second to last column
with nav_cols[5]:
    status_color = "green" if status == "OPEN" else "red"
    st.markdown(f"**NSE:** :{status_color}[{status}] - {status_msg}")

# Theme toggle in last column
with nav_cols[6]:
    theme_label = "Switch to Dark" if st.session_state.theme == 'light' else "Switch to Light"
    toggle_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
    if st.button(toggle_icon, help=theme_label, use_container_width=True, key="theme_toggle"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()

st.markdown("")  # Spacing

# Sidebar for Input Parameters only
with st.sidebar:
    st.markdown("### Input Parameters")

    # Contract selection
    available_contracts = list(NSE_FUTURES.keys()) if MODULES_AVAILABLE else ['SCOM', 'KCB', 'EQTY']
    contract = st.selectbox("Futures Contract", available_contracts)
    st.session_state.pricing_inputs['contract'] = contract

    # Price inputs
    futures_price = st.number_input("Current Futures Price (KES)", value=100.0, step=0.1)
    st.session_state.pricing_inputs['futures_price'] = futures_price

    strike_price = st.number_input("Strike Price (KES)", value=100.0, step=0.1)
    st.session_state.pricing_inputs['strike_price'] = strike_price

    days_to_expiry = st.number_input("Days to Expiry", value=30, min_value=1)
    st.session_state.pricing_inputs['time_to_expiry'] = days_to_expiry

    volatility = st.slider("Volatility (%)", min_value=10, max_value=100, value=30) / 100
    st.session_state.pricing_inputs['volatility'] = volatility

    risk_free_rate = st.number_input("Risk-Free Rate (%)", value=12.0, step=0.1) / 100
    st.session_state.pricing_inputs['risk_free_rate'] = risk_free_rate

    option_type = st.radio("Option Type", ['Call', 'Put'])
    st.session_state.pricing_inputs['option_type'] = option_type

    st.divider()
    
    # NSE Market Fees
    st.markdown("### Market Fees")
    include_fees = st.checkbox("Include NSE Market Fees", value=False, help="Add NSE trading fees to the option price calculation")
    st.session_state.pricing_inputs['include_fees'] = include_fees
    
    if include_fees:
        with st.expander("Fee Breakdown", expanded=True):
            st.markdown("""
            | Participant | Rate |
            |-------------|------|
            | NSE Clear | 0.0125% |
            | Clearing Member | 0.0125% |
            | Trading Member | 0.05% |
            | IPF Levy | 0.005% |
            | CMA Fee | 0.005% |
            | **Total** | **0.085%** |
            """)
            st.caption("Fees calculated on notional contract value")

# NSE Market Fee rates (as percentages)
NSE_FEES = {
    'nse_clear': 0.000125,      # 0.0125%
    'clearing_member': 0.000125, # 0.0125%
    'trading_member': 0.0005,    # 0.05%
    'ipf_levy': 0.00005,         # 0.005%
    'cma_fee': 0.00005,          # 0.005%
}
NSE_TOTAL_FEE_RATE = sum(NSE_FEES.values())  # 0.085% = 0.00085

def calculate_market_fees(notional_value):
    """Calculate NSE market fees based on notional contract value."""
    return {
        'nse_clear': notional_value * NSE_FEES['nse_clear'],
        'clearing_member': notional_value * NSE_FEES['clearing_member'],
        'trading_member': notional_value * NSE_FEES['trading_member'],
        'ipf_levy': notional_value * NSE_FEES['ipf_levy'],
        'cma_fee': notional_value * NSE_FEES['cma_fee'],
        'total': notional_value * NSE_TOTAL_FEE_RATE
    }

# Page content
page = st.session_state.page

if page == "Home":
    st.markdown("""
    <div class="main-header">
        <h2 style="margin: 0;">Welcome to NSE Options Calculator</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Powered by Black-76 Model • Machine Learning • Real-time Analytics</p>
    </div>
    """, unsafe_allow_html=True)

    # Get current inputs for pricing
    inputs = st.session_state.pricing_inputs

    if MODULES_AVAILABLE:
        # Initialize pricer and calculate prices
        pricer = Black76Pricer()
        time_to_expiry = inputs['time_to_expiry'] / 365

        call_price = pricer.price_call(
            inputs['futures_price'],
            inputs['strike_price'],
            time_to_expiry,
            inputs['volatility'],
            inputs['risk_free_rate']
        )
        put_price = pricer.price_put(
            inputs['futures_price'],
            inputs['strike_price'],
            time_to_expiry,
            inputs['volatility'],
            inputs['risk_free_rate']
        )
        
        # Calculate market fees if enabled
        include_fees = inputs.get('include_fees', False)
        notional_value = inputs['futures_price']  # Notional value based on futures price
        fees = calculate_market_fees(notional_value) if include_fees else {'total': 0}
        
        # Add fees to option prices
        call_price_with_fees = call_price + fees['total']
        put_price_with_fees = put_price + fees['total']

        # Black-76 Pricing Model Summary Section
        st.markdown("### Black-76 Pricing Model")

        # Summary metrics bar
        summary_cols = st.columns(5)
        with summary_cols[0]:
            st.markdown("**Current Asset Price**")
            st.markdown(f"**{inputs['futures_price']:.4f}**")
        with summary_cols[1]:
            st.markdown("**Strike Price**")
            st.markdown(f"**{inputs['strike_price']:.4f}**")
        with summary_cols[2]:
            st.markdown("**Time to Maturity (Years)**")
            st.markdown(f"**{time_to_expiry:.4f}**")
        with summary_cols[3]:
            st.markdown("**Volatility (σ)**")
            st.markdown(f"**{inputs['volatility']:.4f}**")
        with summary_cols[4]:
            st.markdown("**Risk-Free Interest Rate**")
            st.markdown(f"**{inputs['risk_free_rate']:.4f}**")

        # Call and Put value boxes
        value_cols = st.columns(2)
        with value_cols[0]:
            fee_label = f" (incl. fees: KES {fees['total']:.4f})" if include_fees else ""
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e6b7b 0%, #2e8b9b 100%);
                        padding: 1.5rem; border-radius: 10px; text-align: center;">
                <p style="margin: 0; color: white; font-size: 0.9rem;">CALL Value{fee_label}</p>
                <h2 style="margin: 0.5rem 0 0 0; color: white;">KES {call_price_with_fees:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with value_cols[1]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #8b2e4d 0%, #a04060 100%);
                        padding: 1.5rem; border-radius: 10px; text-align: center;">
                <p style="margin: 0; color: white; font-size: 0.9rem;">PUT Value{fee_label}</p>
                <h2 style="margin: 0.5rem 0 0 0; color: white;">KES {put_price_with_fees:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Show fee breakdown if enabled
        if include_fees:
            with st.expander("Fee Breakdown Details", expanded=False):
                fee_cols = st.columns(6)
                with fee_cols[0]:
                    st.metric("NSE Clear", f"KES {fees['nse_clear']:.4f}")
                with fee_cols[1]:
                    st.metric("Clearing Member", f"KES {fees['clearing_member']:.4f}")
                with fee_cols[2]:
                    st.metric("Trading Member", f"KES {fees['trading_member']:.4f}")
                with fee_cols[3]:
                    st.metric("IPF Levy", f"KES {fees['ipf_levy']:.4f}")
                with fee_cols[4]:
                    st.metric("CMA Fee", f"KES {fees['cma_fee']:.4f}")
                with fee_cols[5]:
                    st.metric("Total Fees", f"KES {fees['total']:.4f}")

        st.markdown("")  # Spacing

        # Options Price - Interactive Heatmap Section
        st.markdown("### Options Price - Interactive Heatmap")
        st.info("Explore how option prices fluctuate with varying 'Spot Prices and Volatility' levels using interactive heatmap parameters, all while maintaining a constant 'Strike Price'.")

        # Heatmap Parameters Expander
        with st.expander("Heatmap Parameters", expanded=False):
            hm_param_cols = st.columns(2)
            with hm_param_cols[0]:
                min_spot = st.number_input(
                    "Min Spot Price",
                    value=float(inputs['futures_price'] * 0.8),
                    step=0.01,
                    format="%.2f",
                    key="hm_min_spot"
                )
                max_spot = st.number_input(
                    "Max Spot Price",
                    value=float(inputs['futures_price'] * 1.2),
                    step=0.01,
                    format="%.2f",
                    key="hm_max_spot"
                )
            with hm_param_cols[1]:
                min_vol_hm = st.slider(
                    "Min Volatility for Heatmap",
                    min_value=0.05,
                    max_value=0.50,
                    value=0.14,
                    step=0.01,
                    format="%.2f",
                    key="hm_min_vol"
                )
                max_vol_hm = st.slider(
                    "Max Volatility for Heatmap",
                    min_value=0.15,
                    max_value=1.0,
                    value=0.41,
                    step=0.01,
                    format="%.2f",
                    key="hm_max_vol"
                )

        # Generate heatmap data
        spot_range = np.linspace(min_spot, max_spot, 12)
        vol_range = np.linspace(min_vol_hm, max_vol_hm, 10)

        call_prices_grid = np.zeros((len(vol_range), len(spot_range)))
        put_prices_grid = np.zeros((len(vol_range), len(spot_range)))

        for i, vol in enumerate(vol_range):
            for j, spot in enumerate(spot_range):
                call_prices_grid[i, j] = pricer.price_call(
                    spot, inputs['strike_price'], time_to_expiry, vol, inputs['risk_free_rate']
                )
                put_prices_grid[i, j] = pricer.price_put(
                    spot, inputs['strike_price'], time_to_expiry, vol, inputs['risk_free_rate']
                )

        # Create side-by-side heatmaps
        heatmap_cols = st.columns(2)

        with heatmap_cols[0]:
            st.markdown("**Call Price Heatmap**")
            fig_call = go.Figure(data=go.Heatmap(
                z=call_prices_grid,
                x=np.round(spot_range, 2),
                y=np.round(vol_range, 2),
                colorscale='Viridis',
                text=np.round(call_prices_grid, 2),
                texttemplate='%{text}',
                textfont={"size": 8, "color": "white"},
                hovertemplate='Spot: %{x:.2f}<br>Vol: %{y:.2f}<br>Call Price: KES %{z:.2f}<extra></extra>',
                colorbar=dict(title=dict(text="Price", side="right"))
            ))
            fig_call.update_layout(
                title=dict(text="CALL", x=0.5, font=dict(size=16)),
                xaxis_title="Spot Price",
                yaxis_title="Volatility",
                height=450,
                template="plotly_dark" if st.session_state.theme == 'dark' else "plotly_white",
                margin=dict(l=50, r=20, t=60, b=50)
            )
            st.plotly_chart(fig_call, use_container_width=True, config={'displayModeBar': False})

        with heatmap_cols[1]:
            st.markdown("**Put Price Heatmap**")
            fig_put = go.Figure(data=go.Heatmap(
                z=put_prices_grid,
                x=np.round(spot_range, 2),
                y=np.round(vol_range, 2),
                colorscale='Viridis',
                text=np.round(put_prices_grid, 2),
                texttemplate='%{text}',
                textfont={"size": 8, "color": "white"},
                hovertemplate='Spot: %{x:.2f}<br>Vol: %{y:.2f}<br>Put Price: KES %{z:.2f}<extra></extra>',
                colorbar=dict(title=dict(text="Price", side="right"))
            ))
            fig_put.update_layout(
                title=dict(text="PUT", x=0.5, font=dict(size=16)),
                xaxis_title="Spot Price",
                yaxis_title="Volatility",
                height=450,
                template="plotly_dark" if st.session_state.theme == 'dark' else "plotly_white",
                margin=dict(l=50, r=20, t=60, b=50)
            )
            st.plotly_chart(fig_put, use_container_width=True, config={'displayModeBar': False})

    else:
        st.warning("Pricing engine not available. Please check module installation.")

    st.markdown("### NSE Market Overview")

    sample_data = {
        'Contract': ['SCOM', 'EQTY', 'KCBG', 'EABL', 'BATK', 'ABSA', 'NCBA', 'COOP', 'SCBK', 'IMHP', 'N25I'],
        'Name': ['Safaricom', 'Equity Group', 'KCB Group', 'EA Breweries', 'BAT Kenya', 'ABSA Kenya', 'NCBA Group', 'Co-op Bank', 'Stanchart', 'I&M Holdings', 'NSE 25 Index'],
        'MTM Price': [28.21, 60.13, 56.84, 230.45, 437.40, 22.05, 78.17, 22.00, 287.60, 45.45, 3155.58],
        'Sector': ['Telecom', 'Banking', 'Banking', 'Manufacturing', 'Manufacturing', 'Banking', 'Banking', 'Banking', 'Banking', 'Banking', 'Index']
    }

    df = pd.DataFrame(sample_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.info("**Disclaimer**: This tool is for educational and research purposes. All market data shown is simulated.")

elif page == "Option Pricing":
    st.markdown("### Black-76 Pricing Model")
    st.markdown("Price European-style options on NSE futures")

    inputs = st.session_state.pricing_inputs

    if MODULES_AVAILABLE:
        try:
            pricer = Black76Pricer()
            time_to_expiry = inputs['time_to_expiry'] / 365

            # Calculate option values
            if inputs['option_type'] == 'Call':
                option_price = pricer.price_call(
                    inputs['futures_price'],
                    inputs['strike_price'],
                    time_to_expiry,
                    inputs['volatility'],
                    inputs['risk_free_rate']
                )
            else:
                option_price = pricer.price_put(
                    inputs['futures_price'],
                    inputs['strike_price'],
                    time_to_expiry,
                    inputs['volatility'],
                    inputs['risk_free_rate']
                )

            # Calculate market fees if enabled
            include_fees = inputs.get('include_fees', False)
            notional_value = inputs['futures_price']
            fees = calculate_market_fees(notional_value) if include_fees else {'total': 0}
            option_price_with_fees = option_price + fees['total']

            # Display results
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                price_label = f"{inputs['option_type']} Price" + (" (incl. fees)" if include_fees else "")
                st.metric(
                    price_label,
                    format_currency(option_price_with_fees),
                    f"Fees: {format_currency(fees['total'])}" if include_fees else "Per contract"
                )

            with col2:
                st.metric(
                    "Strike Price",
                    format_currency(inputs['strike_price']),
                    ""
                )

            with col3:
                st.metric(
                    "Time to Expiry",
                    f"{inputs['time_to_expiry']} days",
                    ""
                )

            with col4:
                st.metric(
                    "Volatility",
                    f"{inputs['volatility']:.1%}",
                    ""
                )
            
            # Show fee breakdown if enabled
            if include_fees:
                with st.expander("Fee Breakdown", expanded=False):
                    fee_cols = st.columns(6)
                    with fee_cols[0]:
                        st.metric("NSE Clear", f"KES {fees['nse_clear']:.4f}")
                    with fee_cols[1]:
                        st.metric("Clearing Member", f"KES {fees['clearing_member']:.4f}")
                    with fee_cols[2]:
                        st.metric("Trading Member", f"KES {fees['trading_member']:.4f}")
                    with fee_cols[3]:
                        st.metric("IPF Levy", f"KES {fees['ipf_levy']:.4f}")
                    with fee_cols[4]:
                        st.metric("CMA Fee", f"KES {fees['cma_fee']:.4f}")
                    with fee_cols[5]:
                        st.metric("Total Fees", f"KES {fees['total']:.4f}")

            st.divider()

            # P&L Analysis
            st.markdown("### Profit & Loss Analysis")

            price_range = np.linspace(inputs['futures_price'] * 0.7, inputs['futures_price'] * 1.3, 100)

            if inputs['option_type'] == 'Call':
                pnl = [max(0, p - inputs['strike_price']) - option_price_with_fees for p in price_range]
            else:
                pnl = [max(0, inputs['strike_price'] - p) - option_price_with_fees for p in price_range]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=price_range,
                y=pnl,
                name=f"{inputs['option_type']} Option",
                line=dict(color="#2e8b57", width=2),
                fill='tonexty',
                fillcolor='rgba(46, 139, 87, 0.1)'
            ))

            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_vline(x=inputs['futures_price'], line_dash="dash", line_color="gray", opacity=0.5,
                        annotation_text="Current Price", annotation_position="top")

            fig.update_layout(
                title=f"{inputs['option_type']} Option P&L at Expiry",
                xaxis_title="Futures Price at Expiry (KES)",
                yaxis_title="Profit/Loss (KES)",
                hovermode='x unified',
                template="plotly_white",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # Price sensitivity heatmap
            st.markdown("### Price Sensitivity Heatmap")

            price_range_heat = np.linspace(inputs['futures_price'] * 0.7, inputs['futures_price'] * 1.3, 30)
            vol_range = np.linspace(0.1, 0.6, 30)

            prices = np.zeros((len(vol_range), len(price_range_heat)))

            for i, vol in enumerate(vol_range):
                for j, price in enumerate(price_range_heat):
                    if inputs['option_type'] == 'Call':
                        prices[i, j] = pricer.price_call(price, inputs['strike_price'], time_to_expiry, vol, inputs['risk_free_rate'])
                    else:
                        prices[i, j] = pricer.price_put(price, inputs['strike_price'], time_to_expiry, vol, inputs['risk_free_rate'])

            fig_heat = go.Figure(data=go.Heatmap(
                z=prices,
                x=price_range_heat,
                y=vol_range * 100,
                colorscale="RdYlBu",
                hovertemplate="Price: KES %{x:.2f}<br>Vol: %{y:.1f}%<br>Option Price: KES %{z:.2f}<extra></extra>"
            ))

            fig_heat.update_layout(
                title=f"{inputs['option_type']} Option Price Sensitivity",
                xaxis_title="Futures Price (KES)",
                yaxis_title="Volatility (%)",
                height=400
            )

            st.plotly_chart(fig_heat, use_container_width=True)

        except Exception as e:
            st.error(f"Pricing error: {str(e)}")
            logger.error(f"Pricing error: {e}")
    else:
        st.warning("Pricing engine not available. Please check module installation.")

elif page == "Greeks Analysis":
    st.markdown("### Greeks Analysis")
    st.markdown("Analyze option risk sensitivities for comprehensive risk management")

    if not MODULES_AVAILABLE:
        st.warning("Greeks calculator not available. Please check module installation.")
    else:
        inputs = st.session_state.pricing_inputs
        
        try:
            # Initialize calculators
            pricer = Black76Pricer()
            greeks_calc = GreeksCalculator(pricer)
            
            time_to_expiry = inputs['time_to_expiry'] / 365
            
            # Calculate Greeks
            greeks = greeks_calc.calculate_greeks(
                futures_price=inputs['futures_price'],
                strike_price=inputs['strike_price'],
                time_to_expiry=time_to_expiry,
                volatility=inputs['volatility'],
                risk_free_rate=inputs['risk_free_rate'],
                option_type=inputs['option_type'].lower(),
                contract_symbol=inputs['contract']
            )
            
            # Display Greeks in metric cards
            st.markdown("#### Primary Greeks")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Delta (Δ)",
                    f"{greeks.delta:.4f}",
                    help="Change in option price per KES 1 change in futures price"
                )
            
            with col2:
                st.metric(
                    "Gamma (Γ)",
                    f"{greeks.gamma:.6f}",
                    help="Change in delta per KES 1 change in futures price"
                )
            
            with col3:
                st.metric(
                    "Vega (ν)",
                    f"{greeks.vega:.4f}",
                    help="Change in option price per 1% change in volatility"
                )
            
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.metric(
                    "Theta (Θ)",
                    f"{greeks.theta:.4f}",
                    help="Change in option price per day (time decay)"
                )
            
            with col5:
                st.metric(
                    "Rho (ρ)",
                    f"{greeks.rho:.4f}",
                    help="Change in option price per 1% change in interest rate"
                )
            
            with col6:
                st.metric(
                    "Lambda (λ)",
                    f"{greeks.lambda_:.4f}",
                    help="Leverage ratio (elasticity)"
                )
            
            st.divider()
            
            # Greeks visualization
            st.markdown("#### Greeks vs Futures Price")
            
            # Create price range
            price_range = np.linspace(
                inputs['futures_price'] * 0.7,
                inputs['futures_price'] * 1.3,
                50
            )
            
            # Calculate Greeks for each price
            deltas = []
            gammas = []
            vegas = []
            thetas = []
            
            for price in price_range:
                g = greeks_calc.calculate_greeks(
                    futures_price=price,
                    strike_price=inputs['strike_price'],
                    time_to_expiry=time_to_expiry,
                    volatility=inputs['volatility'],
                    risk_free_rate=inputs['risk_free_rate'],
                    option_type=inputs['option_type'].lower()
                )
                deltas.append(g.delta)
                gammas.append(g.gamma)
                vegas.append(g.vega)
                thetas.append(g.theta)
            
            # Create two columns for charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Delta chart
                fig_delta = go.Figure()
                fig_delta.add_trace(go.Scatter(
                    x=price_range,
                    y=deltas,
                    mode='lines',
                    name='Delta',
                    line=dict(color='#2e8b57', width=3),
                    fill='tonexty',
                    fillcolor='rgba(46, 139, 87, 0.1)'
                ))
                fig_delta.add_vline(
                    x=inputs['futures_price'],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Current Price"
                )
                fig_delta.update_layout(
                    title="Delta vs Futures Price",
                    xaxis_title="Futures Price (KES)",
                    yaxis_title="Delta",
                    height=350,
                    template="plotly_white"
                )
                st.plotly_chart(fig_delta, use_container_width=True)
            
            with chart_col2:
                # Gamma chart
                fig_gamma = go.Figure()
                fig_gamma.add_trace(go.Scatter(
                    x=price_range,
                    y=gammas,
                    mode='lines',
                    name='Gamma',
                    line=dict(color='#1e6b47', width=3),
                    fill='tonexty',
                    fillcolor='rgba(30, 107, 71, 0.1)'
                ))
                fig_gamma.add_vline(
                    x=inputs['futures_price'],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Current Price"
                )
                fig_gamma.update_layout(
                    title="Gamma vs Futures Price",
                    xaxis_title="Futures Price (KES)",
                    yaxis_title="Gamma",
                    height=350,
                    template="plotly_white"
                )
                st.plotly_chart(fig_gamma, use_container_width=True)
            
            # Vega and Theta charts
            chart_col3, chart_col4 = st.columns(2)
            
            with chart_col3:
                # Vega chart
                fig_vega = go.Figure()
                fig_vega.add_trace(go.Scatter(
                    x=price_range,
                    y=vegas,
                    mode='lines',
                    name='Vega',
                    line=dict(color='#ff8c00', width=3),
                    fill='tonexty',
                    fillcolor='rgba(255, 140, 0, 0.1)'
                ))
                fig_vega.add_vline(
                    x=inputs['futures_price'],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Current Price"
                )
                fig_vega.update_layout(
                    title="Vega vs Futures Price",
                    xaxis_title="Futures Price (KES)",
                    yaxis_title="Vega",
                    height=350,
                    template="plotly_white"
                )
                st.plotly_chart(fig_vega, use_container_width=True)
            
            with chart_col4:
                # Theta chart
                fig_theta = go.Figure()
                fig_theta.add_trace(go.Scatter(
                    x=price_range,
                    y=thetas,
                    mode='lines',
                    name='Theta',
                    line=dict(color='#dc143c', width=3),
                    fill='tonexty',
                    fillcolor='rgba(220, 20, 60, 0.1)'
                ))
                fig_theta.add_vline(
                    x=inputs['futures_price'],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Current Price"
                )
                fig_theta.update_layout(
                    title="Theta vs Futures Price",
                    xaxis_title="Futures Price (KES)",
                    yaxis_title="Theta (per day)",
                    height=350,
                    template="plotly_white"
                )
                st.plotly_chart(fig_theta, use_container_width=True)
            
            st.divider()
            
            # Greeks interpretation
            st.markdown("#### Greeks Interpretation")
            
            with st.expander("Delta - Directional Risk", expanded=False):
                delta_sign = "positive" if greeks.delta > 0 else "negative"
                st.markdown(f"""
                **Current Delta: {greeks.delta:.4f}**
                
                - Your {inputs['option_type']} option has a **{delta_sign}** delta
                - For every KES 1 increase in futures price, option price changes by approximately **KES {abs(greeks.delta):.4f}**
                - Delta ranges from 0 to 1 for calls, -1 to 0 for puts
                - At-the-money options have delta around ±0.5
                """)
            
            with st.expander("Gamma - Delta Sensitivity", expanded=False):
                st.markdown(f"""
                **Current Gamma: {greeks.gamma:.6f}**
                
                - Gamma measures how quickly delta changes
                - For every KES 1 change in futures price, delta changes by **{greeks.gamma:.6f}**
                - Highest gamma occurs at-the-money
                - Important for managing delta hedging strategies
                """)
            
            with st.expander("Vega - Volatility Risk", expanded=False):
                st.markdown(f"""
                **Current Vega: {greeks.vega:.4f}**
                
                - For every 1% increase in volatility, option price increases by **KES {greeks.vega:.4f}**
                - Long options have positive vega (benefit from volatility increase)
                - Vega is highest for at-the-money options
                - Important for volatility trading strategies
                """)
            
            with st.expander("Theta - Time Decay", expanded=False):
                theta_per_week = greeks.theta * 7
                st.markdown(f"""
                **Current Theta: {greeks.theta:.4f} per day**
                
                - Option loses approximately **KES {abs(greeks.theta):.4f}** per day due to time decay
                - Weekly decay: **KES {abs(theta_per_week):.2f}**
                - Theta accelerates as expiration approaches
                - Long options have negative theta (time works against you)
                """)
            
            with st.expander("Rho - Interest Rate Risk", expanded=False):
                st.markdown(f"""
                **Current Rho: {greeks.rho:.4f}**
                
                - For every 1% increase in interest rates, option price changes by **KES {greeks.rho:.4f}**
                - Usually the least important Greek for short-term options
                - More significant for longer-dated options
                """)
            
            with st.expander("Lambda - Leverage", expanded=False):
                st.markdown(f"""
                **Current Lambda: {greeks.lambda_:.4f}**
                
                - Lambda measures the leverage of the option position
                - A value of {greeks.lambda_:.2f} means a 1% change in futures price results in approximately **{greeks.lambda_:.2f}%** change in option price
                - Higher lambda = higher leverage and risk
                """)
            
        except Exception as e:
            st.error(f"Greeks calculation failed: {str(e)}")
            logger.error(f"Greeks error: {e}", exc_info=True)

elif page == "ML Predictions":
    st.markdown("### Machine Learning Analysis")

    if not MODULES_AVAILABLE:
        st.warning("ML modules not available. Please check installation.")
    else:
        st.info("ML predictions coming soon!")

elif page == "Flavia AI":
    if CHATBOT_AVAILABLE:
        render_flavia_chat()
    else:
        st.markdown("### Flavia AI Chatbot")

        # Fallback simple chat interface with hardcoded API key
        FLAVIA_API_KEY = "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"

        # Initialize session state for chat
        if 'flavia_history' not in st.session_state:
            st.session_state.flavia_history = []

        try:
            from openai import OpenAI
            client = OpenAI(api_key=FLAVIA_API_KEY)

            st.info("Hi! I'm Flavia, your NSE options trading assistant. Ask me anything about options trading, market analysis, or Kenyan securities!")

            # Display chat history
            for msg in st.session_state.flavia_history:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**Flavia:** {msg['content']}")

            # Chat input
            user_input = st.text_input("Ask Flavia:", key="flavia_input_fallback")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Send", use_container_width=True) and user_input:
                    with st.spinner("Flavia is thinking..."):
                        try:
                            response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": "You are Flavia, an AI expert on NSE options trading and Kenyan securities market."},
                                    {"role": "user", "content": user_input}
                                ],
                                max_tokens=500
                            )
                            flavia_response = response.choices[0].message.content
                            st.session_state.flavia_history.append({"role": "user", "content": user_input})
                            st.session_state.flavia_history.append({"role": "assistant", "content": flavia_response})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            with col2:
                if st.button("Clear Chat", use_container_width=True):
                    st.session_state.flavia_history = []
                    st.rerun()
        except ImportError:
            st.error("OpenAI library not installed. Run: pip install openai")

elif page == "Settings":
    st.markdown("### Application Settings")

    st.subheader("Theme Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Current Theme:**")
        theme_name = "Light" if st.session_state.theme == 'light' else "Dark"
        st.info(theme_name)
    
    with col2:
        st.markdown("**Toggle Theme:**")
        if st.button("Switch Theme", use_container_width=True):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    **Theme Features:**
    - Toggle between light and dark modes
    - Custom color schemes for each theme
    - Optimized chart colors for readability
    - NSE-inspired green accent colors
    """)

    st.divider()

    st.subheader("Display Settings")
    show_advanced = st.checkbox("Show Advanced Metrics", value=True)
    show_tooltips = st.checkbox("Show Helpful Tooltips", value=True)
    
    st.divider()

    st.subheader("Application Information")
    st.info("""
    **NSE Options Pricing Tool v2.0**

    - **Framework**: Streamlit
    - **Pricing Model**: Black-76
    - **Greeks**: Delta, Gamma, Theta, Vega, Rho, Lambda
    - **ML Models**: GARCH, LSTM Volatility Prediction (Coming Soon)
    - **Data Source**: NSE & Yahoo Finance
    - **Advanced Analytics**: Heatmaps, P&L Analysis
    - **Themes**: Light & Dark Mode

    Built for the Kenyan securities market.
    """)
