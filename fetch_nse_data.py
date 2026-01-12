#!/usr/bin/env python3
"""
Complete NSE Data Fetching Examples
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class NSEDataFetcher:
    """Utility class for fetching NSE data"""
    
    # NSE stocks available on yfinance
    AVAILABLE_NSE_STOCKS = {
        'SCOM': 'SCOM.NS',      # Safaricom
        'EQTY': 'EQTY.NS',      # Equity Group
        'KCBG': 'KCB.NS',       # KCB Group
        'ABSA': 'ABSA.NS',      # ABSA Bank
    }
    
    @classmethod
    def list_available_symbols(cls):
        """List all available NSE symbols"""
        return list(cls.AVAILABLE_NSE_STOCKS.keys())
    
    @classmethod
    def fetch_daily_data(cls, symbol: str, period: str = '1y') -> pd.DataFrame:
        """
        Fetch daily OHLCV data for NSE stock
        
        Args:
            symbol: NSE symbol (e.g., 'SCOM')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
        
        Returns:
            DataFrame with columns: open, high, low, close, volume, returns, volatility
        """
        if symbol not in cls.AVAILABLE_NSE_STOCKS:
            raise ValueError(f"Unknown symbol: {symbol}. Available: {list(cls.AVAILABLE_NSE_STOCKS.keys())}")
        
        yf_symbol = cls.AVAILABLE_NSE_STOCKS[symbol]
        print(f"Fetching {period} of {symbol} ({yf_symbol})...")
        
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period=period)
        
        # Rename columns to lowercase
        data.columns = [col.lower() for col in data.columns]
        
        # Add technical features
        data['returns'] = data['close'].pct_change()
        data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
        data['volatility_20'] = data['returns'].rolling(20).std() * np.sqrt(252)  # Annualized
        data['volatility_60'] = data['returns'].rolling(60).std() * np.sqrt(252)
        data['sma_20'] = data['close'].rolling(20).mean()
        data['sma_50'] = data['close'].rolling(50).mean()
        
        print(f"✓ Fetched {len(data)} days of data")
        return data
    
    @classmethod
    def fetch_intraday_data(cls, symbol: str, interval: str = '1h', days: int = 30) -> pd.DataFrame:
        """
        Fetch intraday data for NSE stock
        
        Args:
            symbol: NSE symbol
            interval: Time interval ('1m', '5m', '15m', '30m', '60m', '1h')
            days: Number of days of data (limited by yfinance)
        
        Returns:
            DataFrame with intraday data
        """
        if symbol not in cls.AVAILABLE_NSE_STOCKS:
            raise ValueError(f"Unknown symbol: {symbol}")
        
        yf_symbol = cls.AVAILABLE_NSE_STOCKS[symbol]
        print(f"Fetching {days} days of {interval} data for {symbol}...")
        
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period=f"{days}d", interval=interval)
        
        data.columns = [col.lower() for col in data.columns]
        data['returns'] = data['close'].pct_change()
        
        print(f"✓ Fetched {len(data)} {interval} bars")
        return data
    
    @classmethod
    def fetch_multiple_symbols(cls, symbols: list = None, period: str = '6mo') -> dict:
        """
        Fetch data for multiple NSE symbols at once
        
        Args:
            symbols: List of NSE symbols (if None, fetches all available)
            period: Time period
        
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        if symbols is None:
            symbols = cls.list_available_symbols()
        
        print(f"Fetching {len(symbols)} symbols for {period}...")
        data = {}
        
        for symbol in symbols:
            try:
                data[symbol] = cls.fetch_daily_data(symbol, period=period)
            except Exception as e:
                print(f"✗ Failed to fetch {symbol}: {e}")
        
        return data
    
    @classmethod
    def fetch_with_info(cls, symbol: str, period: str = '1y') -> dict:
        """
        Fetch data and get stock info
        
        Args:
            symbol: NSE symbol
            period: Time period
        
        Returns:
            Dictionary with data and stock info
        """
        if symbol not in cls.AVAILABLE_NSE_STOCKS:
            raise ValueError(f"Unknown symbol: {symbol}")
        
        yf_symbol = cls.AVAILABLE_NSE_STOCKS[symbol]
        ticker = yf.Ticker(yf_symbol)
        
        # Get data
        data = cls.fetch_daily_data(symbol, period=period)
        
        # Get info
        info = ticker.info if hasattr(ticker, 'info') else {}
        
        return {
            'data': data,
            'symbol': symbol,
            'yfinance_symbol': yf_symbol,
            'current_price': data['close'].iloc[-1],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'rows': len(data),
            'info': info,
        }


# ============================================================================
# EXAMPLES
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Fetch Daily Data for Single Stock")
    print("="*70)
    
    scom_data = NSEDataFetcher.fetch_daily_data('SCOM', period='1y')
    print(scom_data.tail(10))
    print(f"\nStatistics:")
    print(f"Current Price: KES {scom_data['close'].iloc[-1]:.2f}")
    print(f"52-week High: KES {scom_data['close'].max():.2f}")
    print(f"52-week Low: KES {scom_data['close'].min():.2f}")
    print(f"Average Volume: {scom_data['volume'].mean():,.0f}")
    print(f"Current Volatility (20d): {scom_data['volatility_20'].iloc[-1]:.1%}")
    
    # =====================================================================
    print("\n" + "="*70)
    print("EXAMPLE 2: Fetch Multiple Symbols")
    print("="*70)
    
    data_dict = NSEDataFetcher.fetch_multiple_symbols(
        symbols=['SCOM', 'EQTY', 'KCBG'],
        period='6mo'
    )
    
    for symbol, data in data_dict.items():
        print(f"\n{symbol}:")
        print(f"  Price: KES {data['close'].iloc[-1]:.2f}")
        print(f"  Volatility: {data['volatility_20'].iloc[-1]:.1%}")
        print(f"  Latest Return: {data['returns'].iloc[-1]:.2%}")
    
    # =====================================================================
    print("\n" + "="*70)
    print("EXAMPLE 3: Intraday Data")
    print("="*70)
    
    try:
        intraday = NSEDataFetcher.fetch_intraday_data('SCOM', interval='1h', days=5)
        print(intraday.tail(10))
    except Exception as e:
        print(f"Note: Intraday data may have limited availability: {e}")
    
    # =====================================================================
    print("\n" + "="*70)
    print("EXAMPLE 4: Data with Information")
    print("="*70)
    
    result = NSEDataFetcher.fetch_with_info('EQTY', period='6mo')
    print(f"Symbol: {result['symbol']}")
    print(f"Current Price: KES {result['current_price']:.2f}")
    print(f"Data Points: {result['rows']}")
    print(f"Latest Data:\n{result['data'].tail(5)}")
    
    # =====================================================================
    print("\n" + "="*70)
    print("EXAMPLE 5: Export Data to CSV")
    print("="*70)
    
    scom_data = NSEDataFetcher.fetch_daily_data('SCOM', period='1y')
    scom_data.to_csv('nse_scom_data.csv')
    print("✓ Exported SCOM data to nse_scom_data.csv")
    
    # =====================================================================
    print("\n" + "="*70)
    print("EXAMPLE 6: Use with Volatility Forecaster")
    print("="*70)
    
    try:
        from backend.services.volatility_service import VolatilityForecasterService
        from backend.services.feature_engine import FeatureEngine
        
        # Fetch data
        data = NSEDataFetcher.fetch_daily_data('SCOM', period='6mo')
        
        # Generate features (example)
        print(f"Data shape for ML model: {data[['open', 'high', 'low', 'close', 'volume']].shape}")
        print("✓ Ready to use with VolatilityForecasterService")
        
    except ImportError:
        print("(Volatility service not available in this context)")
