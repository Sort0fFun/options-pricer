#!/usr/bin/env python3
"""
Using NSE Symbols with Volatility Forecaster

This example shows how to use the volatility forecaster service with NSE symbols
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.volatility_service import VolatilityForecasterService
from backend.services.feature_engine import FeatureEngine
from src.core.pricing.black76 import Black76Pricer


class NSEVolatilityForecast:
    """
    Volatility forecasting workflow for NSE symbols.
    """
    
    def __init__(self, model_path: str, data_dir: str):
        """
        Initialize the NSE volatility forecaster.
        
        Args:
            model_path: Path to joblib model (e.g., 'volatility_forecaster_v2_enhanced.joblib')
            data_dir: Directory containing trade data files
        """
        self.model_path = model_path
        self.data_dir = data_dir
        self.vol_service = VolatilityForecasterService(
            model_path=model_path,
            data_dir=data_dir,
            cache_dir='cache/volatility'
        )
        self.feature_engine = FeatureEngine()
        self.pricer = Black76Pricer()
        
        # NSE symbol to yfinance mapping
        self.nse_symbols = {
            'SCOM': 'SCOM.NS',
            'EQTY': 'EQTY.NS',
            'KCBG': 'KCB.NS',
            'ABSA': 'ABSA.NS',
        }
    
    def fetch_nse_data(self, symbol: str, days: int = 60) -> pd.DataFrame:
        """
        Fetch recent NSE data from yfinance.
        
        Args:
            symbol: NSE symbol (e.g., 'SCOM')
            days: Number of days of historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        if symbol not in self.nse_symbols:
            raise ValueError(f"Symbol not supported: {symbol}")
        
        yf_symbol = self.nse_symbols[symbol]
        print(f"Fetching {days} days of {symbol} ({yf_symbol}) data...")
        
        try:
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period=f"{days}d")
            
            # Rename columns to lowercase
            data.columns = [col.lower() for col in data.columns]
            
            # Add technical features
            data['returns'] = data['close'].pct_change()
            data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
            data['sma_20'] = data['close'].rolling(20).mean()
            data['sma_50'] = data['close'].rolling(50).mean()
            data['rsi'] = self._calculate_rsi(data['close'])
            data['atr'] = self._calculate_atr(data)
            
            print(f"Fetched {len(data)} rows for {symbol}")
            return data
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, df, period=14):
        """Calculate Average True Range."""
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift()),
                abs(df['low'] - df['close'].shift())
            )
        )
        return df['tr'].rolling(period).mean()
    
    def forecast_volatility(self, symbol: str, horizon_days: int = 12):
        """
        Forecast volatility for an NSE symbol.
        
        Args:
            symbol: NSE symbol
            horizon_days: Forecast horizon
            
        Returns:
            Dictionary with forecast results
        """
        print(f"\n{'='*60}")
        print(f"Volatility Forecast for {symbol}")
        print(f"{'='*60}")
        
        try:
            # Fetch recent data
            data = self.fetch_nse_data(symbol, days=90)
            
            if data.empty:
                return None
            
            # Calculate recent statistics
            recent_returns = data['returns'].dropna().tail(30)
            hist_vol_30 = recent_returns.std() * np.sqrt(252)  # Annualized
            hist_vol_20 = data['returns'].dropna().tail(20).std() * np.sqrt(252)
            hist_vol_60 = data['returns'].dropna().tail(60).std() * np.sqrt(252)
            
            current_price = data['close'].iloc[-1]
            sma_20 = data['sma_20'].iloc[-1]
            sma_50 = data['sma_50'].iloc[-1]
            rsi = data['rsi'].iloc[-1]
            
            # Make volatility prediction
            vol_prediction = self.vol_service.predict_volatility(
                symbol=symbol,
                futures_price=current_price,
                horizon_days=horizon_days
            )
            
            # Calculate trend
            trend = "Uptrend" if sma_20 > sma_50 else "Downtrend"
            trend_strength = abs(sma_20 - sma_50) / sma_50 * 100
            
            # Compile results
            results = {
                'symbol': symbol,
                'current_price': current_price,
                'timestamp': datetime.now().isoformat(),
                'historical_volatility': {
                    '20_day': hist_vol_20,
                    '30_day': hist_vol_30,
                    '60_day': hist_vol_60,
                },
                'predicted_volatility': vol_prediction.predicted_volatility,
                'confidence_interval': vol_prediction.confidence_interval,
                'model_confidence': vol_prediction.model_confidence,
                'technical_indicators': {
                    'trend': trend,
                    'trend_strength_%': trend_strength,
                    'rsi': rsi,
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                },
                'contributing_models': vol_prediction.contributing_models,
                'model_version': vol_prediction.model_version,
                'horizon_days': horizon_days,
            }
            
            # Print summary
            print(f"\n📊 Current Price: KES {current_price:.2f}")
            print(f"📈 Trend: {trend} ({trend_strength:.1f}%)")
            print(f"📉 RSI: {rsi:.1f}")
            
            print(f"\n📊 Historical Volatility:")
            print(f"   20-day: {hist_vol_20:.1%}")
            print(f"   30-day: {hist_vol_30:.1%}")
            print(f"   60-day: {hist_vol_60:.1%}")
            
            print(f"\n🔮 ML Predicted Volatility: {vol_prediction.predicted_volatility:.1%}")
            print(f"   Confidence Interval: {vol_prediction.confidence_interval[0]:.1%} - {vol_prediction.confidence_interval[1]:.1%}")
            print(f"   Model Confidence: {vol_prediction.model_confidence:.1%}")
            
            print(f"\n🤖 Contributing Models:")
            for model_name, pred_vol in vol_prediction.contributing_models.items():
                print(f"   {model_name}: {pred_vol:.1%}")
            
            return results
            
        except Exception as e:
            print(f"Error forecasting volatility: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def price_option_with_forecast(
        self, 
        symbol: str, 
        strike_price: float, 
        days_to_expiry: int,
        option_type: str = 'Call'
    ) -> dict:
        """
        Price an NSE option using the forecasted volatility.
        
        Args:
            symbol: NSE symbol
            strike_price: Strike price in KES
            days_to_expiry: Days until option expiry
            option_type: 'Call' or 'Put'
            
        Returns:
            Dictionary with pricing results
        """
        print(f"\n{'='*60}")
        print(f"Option Pricing for {symbol}")
        print(f"{'='*60}")
        
        # Get volatility forecast
        vol_results = self.forecast_volatility(symbol, horizon_days=days_to_expiry)
        
        if vol_results is None:
            return None
        
        current_price = vol_results['current_price']
        predicted_vol = vol_results['predicted_volatility']
        
        # Risk-free rate (Kenya T-bill or central bank rate)
        risk_free_rate = 0.12  # Approximate CBR or T-bill rate
        
        # Price using Black-76 model
        time_to_expiry = days_to_expiry / 365
        
        if option_type.lower() == 'call':
            option_price = self.pricer.price_call(
                current_price,
                strike_price,
                time_to_expiry,
                predicted_vol,
                risk_free_rate
            )
        else:
            option_price = self.pricer.price_put(
                current_price,
                strike_price,
                time_to_expiry,
                predicted_vol,
                risk_free_rate
            )
        
        # Calculate Greeks
        delta = self.pricer.delta(
            current_price,
            strike_price,
            time_to_expiry,
            predicted_vol,
            risk_free_rate,
            option_type.lower()
        )
        
        gamma = self.pricer.gamma(
            current_price,
            strike_price,
            time_to_expiry,
            predicted_vol,
            risk_free_rate
        )
        
        vega = self.pricer.vega(
            current_price,
            strike_price,
            time_to_expiry,
            predicted_vol,
            risk_free_rate
        )
        
        results = {
            'symbol': symbol,
            'option_type': option_type,
            'current_price': current_price,
            'strike_price': strike_price,
            'days_to_expiry': days_to_expiry,
            'option_price': option_price,
            'volatility_used': predicted_vol,
            'greeks': {
                'delta': delta,
                'gamma': gamma,
                'vega': vega,
            },
            'intrinsic_value': max(current_price - strike_price, 0) if option_type.lower() == 'call' else max(strike_price - current_price, 0),
            'time_value': option_price - max(current_price - strike_price, 0) if option_type.lower() == 'call' else option_price - max(strike_price - current_price, 0),
        }
        
        print(f"\n💰 Option Price: KES {option_price:.2f}")
        print(f"   Intrinsic Value: KES {results['intrinsic_value']:.2f}")
        print(f"   Time Value: KES {results['time_value']:.2f}")
        
        print(f"\n📊 Greeks:")
        print(f"   Delta: {delta:.4f}")
        print(f"   Gamma: {gamma:.4f}")
        print(f"   Vega: {vega:.4f}")
        
        print(f"\n📈 Volatility Used: {predicted_vol:.1%}")
        
        return results


# Example usage
if __name__ == "__main__":
    # Path to your volatility model
    model_path = "volatility_forecaster_v2_enhanced.joblib"
    data_dir = "data"
    
    # Initialize forecaster
    forecaster = NSEVolatilityForecast(model_path, data_dir)
    
    # Example 1: Just forecast volatility
    print("\n" + "="*60)
    print("EXAMPLE 1: Volatility Forecast")
    print("="*60)
    vol_forecast = forecaster.forecast_volatility('SCOM', horizon_days=12)
    
    # Example 2: Price an option using forecasted volatility
    print("\n" + "="*60)
    print("EXAMPLE 2: Option Pricing with ML Volatility")
    print("="*60)
    option_price = forecaster.price_option_with_forecast(
        symbol='SCOM',
        strike_price=30.0,
        days_to_expiry=30,
        option_type='Call'
    )
    
    # Example 3: Try other NSE stocks
    print("\n" + "="*60)
    print("EXAMPLE 3: Other NSE Stocks")
    print("="*60)
    for symbol in ['EQTY', 'KCBG']:
        try:
            vol_forecast = forecaster.forecast_volatility(symbol, horizon_days=12)
        except Exception as e:
            print(f"Could not forecast {symbol}: {e}")
