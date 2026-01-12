#!/usr/bin/env python3
"""
Example: Using NSE symbols with the options pricing model
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# NSE symbol mapping for yfinance
NSE_SYMBOL_MAP = {
    'SCOM': 'SCOM.NS',      # Safaricom
    'EQTY': 'EQTY.NS',      # Equity Group
    'KCBG': 'KCB.NS',       # KCB Group  
    'ABSA': 'ABSA.NS',      # ABSA Bank
    # Add more as needed
}

def fetch_nse_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch NSE stock data using yfinance.
    
    Args:
        symbol: NSE symbol (e.g., 'SCOM')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    
    Returns:
        DataFrame with OHLCV data
    """
    if symbol not in NSE_SYMBOL_MAP:
        raise ValueError(f"Symbol {symbol} not found. Available: {list(NSE_SYMBOL_MAP.keys())}")
    
    yf_symbol = NSE_SYMBOL_MAP[symbol]
    
    try:
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            print(f"No data found for {symbol} ({yf_symbol})")
            return pd.DataFrame()
        
        # Rename columns to match your model's expectations
        data.columns = [col.lower() for col in data.columns]
        data['returns'] = data['close'].pct_change()
        data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
        
        print(f"Loaded {len(data)} rows for {symbol}")
        return data
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def calculate_volatility(data: pd.DataFrame, window: int = 30) -> float:
    """Calculate annualized volatility."""
    if len(data) < window:
        return 0.0
    
    returns = data['returns'].dropna()
    volatility = returns.rolling(window=window).std().iloc[-1] * np.sqrt(252)
    return volatility

# Example usage
if __name__ == "__main__":
    import numpy as np
    
    # Fetch Safaricom data
    symbol = 'SCOM'
    data = fetch_nse_data(symbol, period="6mo")
    
    if not data.empty:
        current_price = data['close'].iloc[-1]
        volatility = calculate_volatility(data)
        
        print(f"\n{symbol} Analysis:")
        print(f"Current Price: KES {current_price:.2f}")
        print(f"30-day Volatility: {volatility:.1%}")
        print(f"Recent High: KES {data['high'].tail(30).max():.2f}")
        print(f"Recent Low: KES {data['low'].tail(30).min():.2f}")
        
        # Use with your pricing model
        from backend.services.volatility_service import VolatilityForecasterService
        
        # This would use your existing volatility forecasting
        vol_service = VolatilityForecasterService()
        predicted_vol = vol_service.predict_volatility(data)
        
        print(f"ML Predicted Volatility: {predicted_vol:.1%}")