# DOC_STREAMLIT_APP

## Overview
The Streamlit Web Application provides an intuitive, browser-based interface for the NSE Options Pricing Tool. It combines all the powerful backend functionality with a user-friendly frontend that makes complex financial calculations accessible to students, traders, and educators.

## Why Streamlit for Financial Applications?
Streamlit is an excellent choice for financial tools because:

### Advantages:
- **Rapid Development**: Build complex UIs with simple Python code
- **Interactive Widgets**: Real-time updates as users change inputs
- **Data Visualization**: Built-in plotting and charting capabilities
- **No Frontend Knowledge Required**: Pure Python development
- **Easy Deployment**: One-click deployment to Streamlit Cloud
- **State Management**: Handles session state for complex applications

### Perfect for Finance:
- **Real-time Calculations**: Instant feedback as parameters change
- **Complex Visualizations**: Multi-dimensional heatmaps and charts
- **Educational Features**: Step-by-step explanations and tutorials
- **Professional Appearance**: Clean, modern interface suitable for business use

## Application Architecture

### Page Structure:
```
Main App (app.py)
├── Home Page - Introduction and overview
├── Option Pricing - Core Black-76 pricing engine
├── Greeks Analysis - Risk sensitivities calculator
├── Strategy Builder - Multi-leg strategy analyzer
├── Volatility Forecasting - ML-based volatility prediction
├── Market Simulation - NSE data simulation and analysis
├── Educational Hub - Learning resources and tutorials
└── API Documentation - Developer resources
```

### Component Organization:
```
src/web/
├── pages/           # Individual page implementations
├── components/      # Reusable UI components
├── utils/          # Web-specific utilities
└── styles/         # CSS and styling
```

## User Interface Design

### Design Principles:
1. **Simplicity First**: Complex calculations made simple
2. **Progressive Disclosure**: Basic → Intermediate → Advanced features
3. **Immediate Feedback**: Real-time updates and validation
4. **Educational Focus**: Built-in explanations and help
5. **NSE Context**: Kenya-specific data and conventions

### Color Scheme (NSE-Inspired):
- **Primary**: Deep Blue (#1f4e79) - Professional, trustworthy
- **Secondary**: Orange (#ff7b00) - NSE brand color, highlights
- **Success**: Green (#2e7d32) - Positive values, profits
- **Warning**: Amber (#f57c00) - Cautions, medium risk
- **Error**: Red (#d32f2f) - Losses, high risk
- **Background**: Light Gray (#f5f5f5) - Clean, readable

## Page-by-Page Functionality

### 1. Home Page
**Purpose**: Welcome users and provide navigation

**Features**:
- Overview of NSE derivatives market
- Quick links to main features
- Recent market news/updates (simulated)
- Getting started tutorial

**Layout**:
```python
# Hero section with NSE branding
st.title("🇰🇪 NSE Options Pricing Tool")
st.subheader("Advanced options pricing and analysis for Kenyan markets")

# Feature highlights in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Supported Contracts", "6", delta="SCOM, KCB, EQTY...")
with col2:
    st.metric("ML Models", "3", delta="GARCH, LSTM, Ensemble")
with col3:
    st.metric("Greeks Calculated", "8", delta="Delta, Gamma, Vega...")
```

### 2. Option Pricing Page
**Purpose**: Core Black-76 pricing functionality

**Input Controls**:
- Contract selection dropdown (SCOM, KCB, EQTY, etc.)
- Futures price slider with live validation
- Strike price input with suggested strikes
- Time to expiry (days/months converter)
- Volatility input with ML prediction option
- Risk-free rate with CBK rate default
- Option type radio buttons (Call/Put)

**Output Display**:
- Large option price display
- Confidence interval if using ML volatility
- Input parameter summary table
- Intrinsic vs time value breakdown
- Moneyness indicators

**Advanced Features**:
- Batch pricing for multiple strikes
- Sensitivity analysis graphs
- Historical pricing comparison
- Export results to CSV

### 3. Greeks Analysis Page
**Purpose**: Risk sensitivity analysis

**Interactive Greeks Display**:
```python
# Greeks summary cards
metrics_row = st.columns(5)
with metrics_row[0]:
    st.metric("Delta", f"{greeks.delta:.4f}", 
              help="Price sensitivity to futures price changes")
with metrics_row[1]:
    st.metric("Gamma", f"{greeks.gamma:.6f}",
              help="Rate of change of delta")
# ... continue for all Greeks
```

**Visualization Features**:
- Greeks vs underlying price charts
- Greeks vs time to expiry surfaces
- Portfolio Greeks aggregation
- Greeks heatmaps across strike/expiry combinations

**Educational Integration**:
- Pop-up explanations for each Greek
- Interactive scenarios ("What if futures price moves 5%?")
- Real-world examples and interpretations

### 4. Strategy Builder Page  
**Purpose**: Multi-leg options strategy analysis

**Strategy Templates**:
- Bull Call Spread
- Bear Put Spread
- Long Straddle
- Short Strangle
- Iron Condor
- Custom (user-defined)

**Interactive Builder**:
```python
# Strategy selection
strategy_type = st.selectbox("Select Strategy", strategy_options)

# Leg configuration
num_legs = st.number_input("Number of Legs", min_value=1, max_value=4)

for i in range(num_legs):
    with st.expander(f"Leg {i+1}"):
        leg_type = st.radio(f"Leg {i+1} Type", ["Long Call", "Short Call", "Long Put", "Short Put"])
        leg_strike = st.number_input(f"Strike Price", key=f"strike_{i}")
        leg_quantity = st.number_input(f"Quantity", key=f"qty_{i}")
```

**Analysis Output**:
- Payoff diagram at expiration
- Profit/loss at different underlying prices
- Maximum profit/loss scenarios
- Breakeven points
- Greeks for entire strategy

### 5. Volatility Forecasting Page
**Purpose**: ML-powered volatility prediction

**Model Selection**:
- GARCH model results
- LSTM neural network predictions
- Ensemble forecast
- Confidence intervals

**Interactive Features**:
```python
# Volatility forecast horizon
horizon = st.slider("Forecast Horizon (Days)", 1, 90, 30)

# Model comparison
show_models = st.multiselect("Show Models", 
                            ["GARCH", "LSTM", "Ensemble", "Historical"])

# Volatility surface
if st.checkbox("Show Volatility Surface"):
    create_volatility_surface()
```

**Educational Components**:
- Volatility explanation videos
- Model methodology descriptions
- Backtesting performance metrics
- Feature importance analysis

### 6. Market Simulation Page
**Purpose**: NSE market data simulation and analysis

**Simulation Controls**:
- Price trend (bullish/bearish/sideways)
- Volatility regime (low/medium/high)
- Time period for simulation
- Random seed for reproducibility

**Generated Scenarios**:
- Realistic NSE price movements
- Volume patterns
- Corporate actions simulation
- Holiday effects

## Technical Implementation

### State Management:
```python
# Initialize session state
if 'pricing_inputs' not in st.session_state:
    st.session_state.pricing_inputs = {
        'futures_price': 100.0,
        'strike_price': 105.0,
        'volatility': 0.20,
        # ... other defaults
    }

# Update state on input changes
def update_pricing_inputs():
    st.session_state.pricing_inputs['futures_price'] = futures_price_input
    # ... update other inputs
```

### Performance Optimization:
```python
# Cache expensive calculations
@st.cache_data
def calculate_option_prices(F, K_list, T, vol, r, opt_type):
    return [pricer.price_option(...) for K in K_list]

@st.cache_data
def load_historical_data(symbol):
    return data_loader.get_historical_data(symbol)

# Use fragments for partial updates
@st.fragment
def update_greeks_display():
    # Only recalculate Greeks when inputs change
    pass
```

### Error Handling:
```python
try:
    option_price = pricer.price_call(F, K, T, vol, r)
    st.success(f"Option Price: KES {option_price:.2f}")
except PricingError as e:
    st.error(f"Pricing Error: {e}")
except Exception as e:
    st.error("An unexpected error occurred. Please check your inputs.")
    logger.error(f"Unexpected error in pricing: {e}")
```

## User Experience Features

### Input Validation and Feedback:
```python
# Real-time validation
if futures_price <= 0:
    st.error("Futures price must be positive")
elif futures_price > 10000:
    st.warning("Very high futures price. Please verify.")
else:
    st.success("✓ Valid futures price")

# Smart defaults based on contract
if contract_symbol == "SCOM":
    default_price = get_current_scom_price()
    default_vol = get_scom_historical_volatility()
```

### Help and Documentation:
```python
# Contextual help
with st.expander("ℹ️ What is Delta?"):
    st.markdown("""
    Delta measures how much the option price changes when the underlying 
    futures price changes by KES 1. For example:
    - Delta of 0.6 means option price increases by KES 0.60 when futures price increases by KES 1
    - Call options have positive delta (0 to 1)
    - Put options have negative delta (-1 to 0)
    """)

# Interactive tutorials
if st.button("🎓 Start Pricing Tutorial"):
    run_interactive_tutorial()
```

### Responsive Design:
```python
# Mobile-friendly layouts
if st.session_state.get('is_mobile', False):
    # Single column layout for mobile
    display_mobile_layout()
else:
    # Multi-column layout for desktop
    col1, col2 = st.columns([2, 1])
    with col1:
        display_main_content()
    with col2:
        display_sidebar_content()
```

## Data Visualization Components

### Price Charts:
```python
def create_payoff_diagram(strategy):
    fig = go.Figure()
    
    # Add payoff line
    fig.add_trace(go.Scatter(
        x=underlying_prices,
        y=payoffs,
        mode='lines',
        name='Payoff at Expiration',
        line=dict(color='blue', width=3)
    ))
    
    # Add breakeven lines
    for breakeven in breakeven_points:
        fig.add_vline(x=breakeven, line_dash="dash", 
                     annotation_text=f"Breakeven: {breakeven}")
    
    return fig
```

### Greeks Visualization:
```python
def create_greeks_heatmap(strikes, expiries, greek_name):
    fig = go.Figure(data=go.Heatmap(
        z=greek_values,
        x=strikes,
        y=expiries,
        colorscale='RdYlBu',
        colorbar=dict(title=greek_name)
    ))
    
    fig.update_layout(
        title=f"{greek_name} Heatmap",
        xaxis_title="Strike Price (KES)",
        yaxis_title="Days to Expiry"
    )
    
    return fig
```

### Performance Metrics:
```python
def display_model_performance():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("RMSE", f"{performance.rmse:.4f}")
    with col2:
        st.metric("R²", f"{performance.r_squared:.3f}")
    with col3:
        st.metric("Hit Rate", f"{performance.hit_rate:.1f}%")
```

## Integration with Backend Systems

### API Connections:
```python
# Connect to pricing engine
from src.core.pricing.black76 import Black76Pricer
from src.core.greeks.calculator import GreeksCalculator
from src.ml.volatility.predictor import VolatilityPredictor

# Initialize models
@st.cache_resource
def load_models():
    pricer = Black76Pricer()
    greeks_calc = GreeksCalculator()
    vol_predictor = VolatilityPredictor()
    return pricer, greeks_calc, vol_predictor
```

### Real-time Updates:
```python
# Auto-refresh for live data
if st.checkbox("Auto-refresh (30s)"):
    time.sleep(30)
    st.rerun()

# Manual refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
```

## Deployment Considerations

### Streamlit Cloud Configuration:
```toml
# .streamlit/config.toml
[server]
maxUploadSize = 10
maxMessageSize = 10

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#ff7b00"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### Environment Variables:
```python
# secrets.toml (for production)
OPENAI_API_KEY = "your-api-key"
NSE_DATA_API_KEY = "your-nse-key"
ENVIRONMENT = "production"
```

### Performance Monitoring:
```python
# Track usage and performance
import time

start_time = time.time()
# ... app logic ...
execution_time = time.time() - start_time

if execution_time > 5.0:
    st.warning(f"Slow performance detected: {execution_time:.2f}s")
```

This Streamlit application provides a comprehensive, user-friendly interface that makes sophisticated options pricing and analysis accessible to NSE market participants while maintaining professional standards and educational value.