# DOC_PRICING_ENGINE

## Overview
The Pricing Engine module implements the Black-76 model for pricing European-style options on futures contracts. This is the core mathematical foundation of the application, specifically designed for the Kenyan NSE derivatives market.

## What is the Black-76 Model?
The Black-76 model is a mathematical formula used to calculate the fair value of options on futures contracts. It was developed by Fischer Black in 1976 as an extension of the famous Black-Scholes model.

### Key Differences from Black-Scholes:
- Uses futures price instead of stock price
- Assumes no dividend yield (since futures already account for this)
- Discounts the entire payoff at the risk-free rate

## Mathematical Foundation

### Call Option Price:
```
C = e^(-r*T) * [F * N(d1) - K * N(d2)]
```

### Put Option Price:
```
P = e^(-r*T) * [K * N(-d2) - F * N(-d1)]
```

### Where:
- **C** = Call option price
- **P** = Put option price  
- **F** = Current futures price
- **K** = Strike price
- **r** = Risk-free interest rate
- **T** = Time to expiration (in years)
- **σ** = Volatility of the futures price
- **N()** = Cumulative standard normal distribution function

### Helper Variables:
```
d1 = [ln(F/K) + (σ²/2) * T] / (σ * √T)
d2 = d1 - σ * √T
```

## Module Structure

### Files:
- `src/core/pricing/black76.py` - Main Black-76 implementation
- `src/core/pricing/validators.py` - Input validation functions
- `src/core/pricing/utils.py` - Helper utilities and constants

### Classes:
- `Black76Pricer` - Main pricing engine class
- `OptionContract` - Data structure for option parameters
- `PricingResult` - Structured output for pricing results

## Usage Examples

### Basic Usage:
```python
from src.core.pricing.black76 import Black76Pricer

# Initialize the pricing engine
pricer = Black76Pricer()

# Price a call option
call_price = pricer.price_call(
    futures_price=100.0,
    strike_price=105.0,
    time_to_expiry=0.25,  # 3 months
    volatility=0.20,      # 20% annual volatility
    risk_free_rate=0.05   # 5% annual rate
)

print(f"Call option price: KES {call_price:.2f}")
```

### Batch Pricing:
```python
# Price multiple options at once
options_data = [
    {"F": 100, "K": 95, "T": 0.25, "σ": 0.2, "r": 0.05, "type": "call"},
    {"F": 100, "K": 105, "T": 0.25, "σ": 0.2, "r": 0.05, "type": "put"},
]

results = pricer.price_batch(options_data)
```

## NSE-Specific Adaptations

### Supported Futures Contracts:
- **Safaricom (SCOM)** - Most liquid NSE stock
- **KCB Group (KCB)** - Major banking stock  
- **Equity Group (EQTY)** - Leading bank
- **ABSA Bank (ABSA)** - International bank
- **NSE 25 Index** - Broad market index
- **Mini NSE 25** - Smaller contract size

### Market Conventions:
- **Trading Hours**: 9:00 AM - 3:00 PM EAT
- **Currency**: Kenyan Shilling (KES)
- **Expiry Months**: March, June, September, December (quarterly)
- **Settlement**: Cash-settled on expiry date

## Input Validation

The module includes comprehensive input validation:

### Validation Rules:
- Futures price must be positive
- Strike price must be positive  
- Time to expiry must be positive and ≤ 5 years
- Volatility must be between 0.01 and 5.0 (1% to 500%)
- Risk-free rate must be between -0.1 and 1.0 (-10% to 100%)

### Error Handling:
```python
from src.core.pricing.validators import PricingError

try:
    price = pricer.price_call(F=100, K=105, T=0.25, vol=0.2, r=0.05)
except PricingError as e:
    print(f"Pricing error: {e}")
```

## Performance Considerations

### Optimization Features:
- Vectorized calculations using NumPy
- Cached normal distribution calculations  
- Efficient batch processing
- Memory-optimized data structures

### Typical Performance:
- Single option pricing: < 1ms
- Batch pricing (100 options): < 10ms
- Heatmap generation (10,000 points): < 100ms

## Testing Framework

### Test Coverage:
- Unit tests for all pricing functions
- Validation tests for edge cases
- Performance benchmarks
- Comparison with reference implementations

### Running Tests:
```bash
pytest tests/test_pricing_engine.py -v
```

## Common Use Cases

### 1. Real-time Option Pricing
Monitor option values as market conditions change

### 2. Strategy Analysis  
Compare prices across different strikes and expiries

### 3. Risk Management
Calculate position values for portfolio management

### 4. Educational Tools
Demonstrate how inputs affect option prices

## Limitations

### Model Assumptions:
- Constant volatility (not realistic but mathematically tractable)
- Constant risk-free rate
- No transaction costs
- Perfect liquidity
- European exercise only (cannot exercise before expiry)

### Market Reality:
- Real volatility changes over time
- Transaction costs affect profitability  
- Liquidity varies by contract
- Early exercise may be optimal for some strategies

## Future Enhancements

### Planned Improvements:
- Stochastic volatility models (Heston, SABR)
- Term structure of volatility
- Transaction cost modeling  
- American option pricing
- Multi-asset option pricing

### Integration Points:
- Machine learning volatility predictions
- Real-time market data feeds
- Risk management systems
- Portfolio optimization tools