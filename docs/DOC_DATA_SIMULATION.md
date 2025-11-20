# DOC_DATA_SIMULATION

## Overview
The Data Simulation module generates realistic market data for NSE futures contracts when live data is unavailable or for educational purposes. This is crucial for testing, backtesting, and demonstrating the options pricing tool functionality.

## Why Simulate NSE Market Data?

### Practical Challenges:
- **Cost**: Live NSE data costs KES 50,000/month
- **Access**: Limited API availability for retail developers
- **Historical Data**: NSE derivatives market only started in 2019 (limited history)
- **Testing**: Need controlled scenarios for model validation

### Educational Benefits:
- **Learning**: Students can experiment without real money
- **Scenario Analysis**: Test extreme market conditions safely
- **Strategy Development**: Backtest trading strategies
- **Model Validation**: Verify pricing models with known parameters

## Simulation Architecture

### Data Generation Approach:
1. **Geometric Brownian Motion (GBM)** - Foundation for price movements
2. **Regime Switching** - Alternate between bull/bear/sideways markets
3. **Volatility Clustering** - Realistic volatility patterns using GARCH
4. **Volume Modeling** - Correlated volume patterns
5. **NSE-Specific Features** - Local market characteristics

### Mathematical Foundation:

#### Geometric Brownian Motion:
```
dS = μS dt + σS dW
```
Where:
- S = Stock/futures price
- μ = Drift (expected return)
- σ = Volatility
- dW = Wiener process (random walk)

#### GARCH Volatility:
```
σₜ² = α₀ + α₁ε²ₜ₋₁ + β₁σ²ₜ₋₁
```

#### Volume Model:
```
V_t = V₀ * exp(ρ * |r_t| + γ * ε_v)
```
Where ρ correlates volume with absolute returns

## NSE Market Characteristics

### Contract Specifications:
```python
NSE_MARKET_PARAMS = {
    'SCOM': {
        'base_price': 28.50,
        'annual_volatility': 0.25,
        'average_volume': 2_000_000,
        'trading_hours': (9, 15),  # 9 AM to 3 PM EAT
        'tick_size': 0.05,
        'market_cap': 1.2e12  # Large cap
    },
    'KCB': {
        'base_price': 45.20,
        'annual_volatility': 0.28,
        'average_volume': 800_000,
        'tick_size': 0.05,
        'market_cap': 5e11  # Large cap
    },
    # ... other contracts
}
```

### Trading Calendar:
- **Trading Days**: Monday - Friday
- **Market Hours**: 9:00 AM - 3:00 PM EAT
- **Holidays**: Kenyan public holidays
- **Quarter Ends**: March, June, September, December (options expiry)

### Market Regimes:
1. **Bull Market**: μ = 12%, σ = 20%
2. **Bear Market**: μ = -8%, σ = 30%
3. **Sideways Market**: μ = 2%, σ = 15%
4. **Crisis Mode**: μ = -20%, σ = 50%

## Implementation Components

### Core Simulator Classes:
```python
class NSEMarketSimulator:
    """Main market data simulator"""
    
class PriceGenerator:
    """Generate realistic price movements"""
    
class VolumeGenerator:
    """Generate correlated volume data"""
    
class RegimeModel:
    """Handle market regime transitions"""
    
class CalendarManager:
    """Manage NSE trading calendar"""
```

### Simulation Features:

#### 1. Multi-Asset Simulation
Generate correlated movements across NSE contracts:
```python
# Correlation matrix for NSE stocks
CORRELATION_MATRIX = {
    'SCOM': {'KCB': 0.4, 'EQTY': 0.3, 'ABSA': 0.35},
    'KCB': {'EQTY': 0.6, 'ABSA': 0.7},  # Banks correlated
    'EQTY': {'ABSA': 0.65},
    'NSE25': {'SCOM': 0.8, 'KCB': 0.7, 'EQTY': 0.7}  # Index correlations
}
```

#### 2. Intraday Patterns
Model realistic intraday price movements:
```python
INTRADAY_PATTERNS = {
    'opening_gap': {'mean': 0.001, 'std': 0.005},
    'morning_trend': {'mean': 0.0002, 'std': 0.003},
    'midday_quiet': {'mean': 0.0001, 'std': 0.002},
    'afternoon_pickup': {'mean': 0.0003, 'std': 0.004},
    'closing_effect': {'mean': -0.0001, 'std': 0.003}
}
```

#### 3. Corporate Actions
Simulate stock splits, dividends, and other corporate events:
```python
CORPORATE_ACTIONS = {
    'dividend': {'frequency': 'quarterly', 'yield': 0.03},
    'stock_split': {'probability': 0.02, 'ratio': [2, 1]},
    'rights_issue': {'probability': 0.01, 'discount': 0.1}
}
```

#### 4. Economic Events
Include macroeconomic impacts:
```python
ECONOMIC_EVENTS = {
    'cbk_rate_change': {'probability': 0.08, 'impact': 0.02},
    'inflation_report': {'probability': 0.25, 'impact': 0.01},
    'political_events': {'probability': 0.1, 'impact': 0.03},
    'currency_shock': {'probability': 0.05, 'impact': 0.05}
}
```

## Simulation Scenarios

### 1. Historical Recreation
Recreate past market conditions:
```python
def simulate_covid_crash():
    """Simulate March 2020 market crash scenario"""
    return {
        'regime': 'crisis',
        'volatility_multiplier': 3.0,
        'correlation_increase': 0.3,
        'volume_spike': 5.0,
        'duration_days': 30
    }

def simulate_election_period():
    """Simulate election uncertainty"""
    return {
        'regime': 'volatile',
        'political_risk': 0.05,
        'foreign_outflow': True,
        'currency_weakness': 0.1
    }
```

### 2. Stress Testing
Generate extreme scenarios for risk testing:
```python
STRESS_SCENARIOS = {
    'black_swan': {
        'description': 'Extreme negative event',
        'probability': 0.001,
        'market_drop': 0.20,
        'volatility_spike': 3.0
    },
    'liquidity_crisis': {
        'description': 'Market liquidity dries up',
        'volume_reduction': 0.7,
        'bid_ask_widening': 5.0
    },
    'currency_crisis': {
        'description': 'KES devaluation',
        'fx_shock': 0.25,
        'capital_flight': True
    }
}
```

### 3. Educational Scenarios
Controlled scenarios for learning:
```python
EDUCATIONAL_SCENARIOS = {
    'volatility_demo': {
        'description': 'Show impact of changing volatility',
        'volatility_schedule': [0.15, 0.25, 0.40, 0.25, 0.15],
        'regime': 'controlled'
    },
    'trend_following': {
        'description': 'Strong trending market',
        'trend_strength': 0.8,
        'noise_level': 0.1
    }
}
```

## Data Quality and Realism

### Validation Metrics:
1. **Statistical Properties**:
   - Return distribution (normal vs fat tails)
   - Volatility clustering
   - Serial correlation
   - Leverage effect

2. **Market Microstructure**:
   - Bid-ask bounce
   - Volume-price relationships
   - Intraday patterns
   - Day-of-week effects

3. **Financial Stylized Facts**:
   - Fat tails in return distribution
   - Volatility clustering
   - Mean reversion in volatility
   - Asymmetric volatility (leverage effect)

### Quality Assurance:
```python
def validate_simulated_data(data):
    """Validate simulated data quality"""
    
    checks = {
        'returns_distribution': check_return_normality(data),
        'volatility_clustering': check_arch_effects(data),
        'price_continuity': check_no_gaps(data),
        'volume_correlation': check_volume_price_correlation(data),
        'trading_hours': check_trading_time_consistency(data)
    }
    
    return all(checks.values())
```

## Integration with Options Pricing

### Seamless Data Flow:
```python
# Generate market data
simulator = NSEMarketSimulator()
market_data = simulator.generate_scenario(
    contract='SCOM',
    days=252,
    scenario='normal_market'
)

# Use for volatility estimation
vol_predictor = VolatilityPredictor()
vol_predictor.fit(market_data)

# Price options with simulated data
pricer = Black76Pricer()
current_price = market_data['price'].iloc[-1]
predicted_vol = vol_predictor.predict_volatility(market_data.tail(60))

option_price = pricer.price_call(
    futures_price=current_price,
    strike_price=current_price * 1.05,
    time_to_expiry=0.25,
    volatility=predicted_vol.predicted_volatility,
    risk_free_rate=0.10
)
```

### Backtesting Framework:
```python
def backtest_pricing_model(model, simulated_data, lookback_window=60):
    """Backtest pricing model on simulated data"""
    
    results = []
    
    for i in range(lookback_window, len(simulated_data)):
        # Historical data for model training
        train_data = simulated_data.iloc[i-lookback_window:i]
        
        # Current market conditions
        current_data = simulated_data.iloc[i]
        
        # Predict volatility
        predicted_vol = model.predict(train_data)
        
        # Actual realized volatility (forward-looking)
        actual_vol = calculate_realized_vol(
            simulated_data.iloc[i:i+30]
        )
        
        results.append({
            'date': current_data['date'],
            'predicted_vol': predicted_vol,
            'actual_vol': actual_vol,
            'error': abs(predicted_vol - actual_vol)
        })
    
    return pd.DataFrame(results)
```

## Real-World Calibration

### Market Data Sources for Calibration:
1. **NSE Historical Data**: Available daily summaries
2. **Regional Markets**: Use South African JSE or Nigerian NSE patterns
3. **Currency Data**: USD/KES for correlation analysis
4. **Economic Indicators**: Inflation, interest rates, GDP

### Calibration Process:
```python
def calibrate_to_nse_data(historical_nse_data):
    """Calibrate simulation parameters to real NSE data"""
    
    # Estimate parameters from real data
    returns = historical_nse_data['price'].pct_change().dropna()
    
    calibrated_params = {
        'annual_return': returns.mean() * 252,
        'annual_volatility': returns.std() * np.sqrt(252),
        'skewness': returns.skew(),
        'kurtosis': returns.kurtosis(),
        'max_drawdown': calculate_max_drawdown(historical_nse_data['price'])
    }
    
    return calibrated_params
```

## Performance and Scalability

### Efficient Generation:
```python
# Vectorized operations for speed
def generate_price_paths(n_paths, n_days, dt=1/252):
    """Generate multiple price paths efficiently"""
    
    # Generate all random numbers at once
    random_shocks = np.random.normal(
        size=(n_paths, n_days)
    )
    
    # Vectorized price calculation
    log_returns = (
        (mu - 0.5 * sigma**2) * dt + 
        sigma * np.sqrt(dt) * random_shocks
    )
    
    log_prices = np.cumsum(log_returns, axis=1)
    prices = S0 * np.exp(log_prices)
    
    return prices
```

### Memory Management:
```python
# Efficient data structures
class StreamingDataGenerator:
    """Generate data on-demand to save memory"""
    
    def __iter__(self):
        return self
    
    def __next__(self):
        # Generate next data point
        return self.generate_next_point()
```

## Educational Applications

### Interactive Demonstrations:
1. **Volatility Impact**: Show how changing volatility affects option prices
2. **Time Decay**: Demonstrate theta decay over time
3. **Regime Changes**: Show how market regimes affect pricing
4. **Correlation Effects**: Multi-asset option strategies

### Student Exercises:
1. **Parameter Estimation**: Estimate GBM parameters from simulated data
2. **Model Validation**: Test pricing models on known simulated data
3. **Strategy Backtesting**: Test options strategies on historical simulations
4. **Risk Management**: Calculate VaR on simulated portfolios

This simulation framework provides the foundation for realistic market data generation, enabling comprehensive testing and education in NSE options pricing and risk management.