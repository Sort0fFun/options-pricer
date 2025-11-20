# DOC_GREEKS_ENGINE

## Overview
The Greeks Engine calculates the risk sensitivities of options positions, commonly known as "the Greeks." These metrics help traders and risk managers understand how option prices change in response to various market factors.

## What are the Greeks?
The Greeks are mathematical measures that describe how sensitive an option's price is to changes in underlying parameters. They are essential tools for:

- **Risk Management**: Understanding portfolio exposure
- **Hedging**: Creating delta-neutral positions
- **Trading**: Timing entry and exit points
- **Portfolio Optimization**: Balancing risk and reward

## The Five Primary Greeks

### 1. Delta (Δ)
**What it measures**: Price sensitivity to changes in the underlying futures price

**Mathematical Definition**:
- **Call Delta**: N(d1)  
- **Put Delta**: N(d1) - 1 = -N(-d1)

**Practical Meaning**:
- Delta ranges from 0 to 1 for calls, -1 to 0 for puts
- A delta of 0.6 means a KES 1 increase in futures price increases call value by KES 0.60
- At-the-money options have delta ≈ 0.5 (calls) or ≈ -0.5 (puts)

**Business Applications**:
- **Hedging**: For every 100 call options with delta 0.6, you need to short 60 futures contracts
- **Probability**: Delta approximates the probability of finishing in-the-money
- **Position Sizing**: Helps determine equivalent exposure to the underlying

### 2. Gamma (Γ)  
**What it measures**: Rate of change of delta (acceleration of price moves)

**Mathematical Definition**:
```
Gamma = φ(d1) / (F × σ × √T)
```
Where φ(d1) is the standard normal probability density function

**Practical Meaning**:
- Gamma is always positive for both calls and puts
- Highest for at-the-money options
- Approaches zero for deep in/out-of-the-money options

**Business Applications**:
- **Risk Management**: High gamma positions have unstable delta
- **Trading**: Gamma scalping strategies profit from volatility
- **Market Making**: Gamma risk requires frequent rehedging

### 3. Vega (ν)
**What it measures**: Sensitivity to changes in implied volatility

**Mathematical Definition**:
```
Vega = F × √T × φ(d1) × e^(-r×T)
```

**Practical Meaning**:
- Vega is always positive (higher volatility increases option value)
- Measured in price change per 1% volatility change
- Highest for at-the-money options with longer time to expiry

**Business Applications**:
- **Volatility Trading**: Buy low vol, sell high vol
- **Earnings Plays**: Volatility often drops after earnings announcements
- **Portfolio Management**: Balance vega exposure across positions

### 4. Theta (Θ)
**What it measures**: Time decay (sensitivity to passage of time)

**Mathematical Definition**:
- **Call Theta**: -[F×φ(d1)×σ / (2×√T) + r×K×e^(-r×T)×N(d2)]
- **Put Theta**: -[F×φ(d1)×σ / (2×√T) - r×K×e^(-r×T)×N(-d2)]

**Practical Meaning**:
- Usually negative for options (time decay reduces value)
- Accelerates as expiration approaches
- Highest for at-the-money options near expiry

**Business Applications**:
- **Income Strategies**: Sell options to collect theta
- **Timing**: Avoid buying options before weekends/holidays
- **Strategy Selection**: Consider time decay in multi-leg strategies

### 5. Rho (ρ)
**What it measures**: Sensitivity to changes in risk-free interest rate

**Mathematical Definition**:
- **Call Rho**: K × T × e^(-r×T) × N(d2)
- **Put Rho**: -K × T × e^(-r×T) × N(-d2)

**Practical Meaning**:
- Less important for short-term options
- More significant for long-term options (LEAPS)
- Calls have positive rho, puts have negative rho

**Business Applications**:
- **Interest Rate Risk**: Important for long-dated options
- **Currency Considerations**: More relevant in international markets
- **Carry Trades**: Consider rate differentials

## Advanced Greeks

### Lambda (Λ) - Leverage/Elasticity
**What it measures**: Percentage change in option price relative to percentage change in underlying price

**Formula**: Lambda = Delta × (F / Option_Price)

### Vanna
**What it measures**: Sensitivity of delta to volatility changes

**Formula**: Vanna = -φ(d1) × d2 / σ

### Charm
**What it measures**: Rate of change of delta over time

**Formula**: Charm = -φ(d1) × [2×r×T - d2×σ×√T] / (2×T×σ×√T)

## Module Structure

### Files:
- `src/core/greeks/calculator.py` - Main Greeks calculation engine
- `src/core/greeks/analytics.py` - Advanced analytics and portfolio Greeks
- `src/core/greeks/visualizer.py` - Greeks visualization tools

### Classes:
- `GreeksCalculator` - Main calculation engine
- `PortfolioGreeks` - Portfolio-level Greeks analysis
- `GreeksProfile` - Individual option Greeks container

## Usage Examples

### Single Option Greeks:
```python
from src.core.greeks.calculator import GreeksCalculator

calculator = GreeksCalculator()

greeks = calculator.calculate_greeks(
    futures_price=100.0,
    strike_price=105.0,
    time_to_expiry=0.25,
    volatility=0.20,
    risk_free_rate=0.05,
    option_type='call'
)

print(f"Delta: {greeks.delta:.4f}")
print(f"Gamma: {greeks.gamma:.6f}")
print(f"Vega: {greeks.vega:.4f}")
print(f"Theta: {greeks.theta:.4f}")
print(f"Rho: {greeks.rho:.4f}")
```

### Portfolio Greeks:
```python
from src.core.greeks.analytics import PortfolioGreeks

portfolio = PortfolioGreeks()

# Add positions
portfolio.add_position(
    contract_type='call',
    quantity=10,
    futures_price=100,
    strike_price=105,
    time_to_expiry=0.25,
    volatility=0.20,
    risk_free_rate=0.05
)

total_greeks = portfolio.calculate_total_greeks()
print(f"Portfolio Delta: {total_greeks.delta:.2f}")
```

## NSE-Specific Considerations

### Market Hours Impact:
- Theta decay continues even when markets are closed
- Weekend effect: 2-day time decay over weekend
- Holiday adjustments for Kenyan market calendar

### Currency Effects:
- All Greeks calculated in KES terms
- Interest rate Greeks use CBK policy rate as reference
- Volatility patterns specific to NSE trading

### Contract Specifications:
- Different multipliers for different contracts
- Tick size considerations for practical trading
- Margin requirements affect Greeks interpretation

## Risk Management Applications

### Delta Hedging:
```python
# Example: Delta-neutral portfolio
long_calls_delta = 100 * 0.6  # 100 calls with delta 0.6
futures_to_short = long_calls_delta  # Short 60 futures contracts
net_delta = long_calls_delta - futures_to_short  # Should be ≈ 0
```

### Gamma Scalping:
```python
# High gamma positions need frequent rebalancing
if abs(portfolio_gamma) > gamma_threshold:
    adjust_hedge_ratio()
```

### Volatility Trading:
```python
# Trade based on vega exposure
if implied_vol < historical_vol:
    buy_vega_positive_strategies()  # Buy options
else:
    sell_vega_positive_strategies()  # Sell options
```

## Visualization Features

### Greeks Charts:
- Delta vs. Underlying Price (S-curve)
- Gamma vs. Underlying Price (bell curve)  
- Vega vs. Time to Expiry (decay curve)
- Theta vs. Time (acceleration curve)

### Heatmaps:
- Greeks sensitivity across strike/expiry combinations
- Portfolio Greeks across different market scenarios
- Risk scenario analysis

### Time Series:
- Greeks evolution over time
- Historical Greeks patterns
- Volatility impact on Greeks

## Performance Optimization

### Calculation Efficiency:
- Vectorized operations using NumPy
- Cached normal distribution calculations
- Batch processing for multiple options
- Memory-efficient data structures

### Accuracy Considerations:
- Numerical precision for near-expiry options
- Handling of extreme parameters
- Boundary condition checking
- Interpolation for smooth Greeks curves

## Common Pitfalls and Solutions

### Near Expiration:
- **Problem**: Gamma and theta explode near expiry
- **Solution**: Use time-weighted Greeks for risk management

### Deep Out-of-the-Money:
- **Problem**: Greeks become very small and lose meaning
- **Solution**: Use percentage Greeks or combine with notional amounts

### High Volatility Environments:
- **Problem**: Vega becomes dominant risk factor
- **Solution**: Focus on volatility Greeks (vanna, volga)

### Interest Rate Changes:
- **Problem**: Rho often ignored but can be significant
- **Solution**: Monitor central bank policy for rate-sensitive portfolios

## Integration with Other Modules

### Pricing Engine:
- Uses same Black-76 framework for consistency
- Shared validation and utility functions
- Common data structures

### Machine Learning:
- Greeks used as features for ML models
- Predicted volatility affects vega calculations
- Regime detection impacts Greeks stability

### Risk Management:
- Greeks feed into VaR calculations
- Stress testing uses Greeks sensitivities  
- Portfolio optimization considers Greeks constraints

This documentation provides the foundation for understanding and using the Greeks calculation engine effectively in the NSE options pricing context.