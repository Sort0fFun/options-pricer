"""
Feature Engineering for Machine Learning Models

This module creates comprehensive features from raw market data
for use in volatility prediction and regime detection models.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Technical analysis
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available. Some technical indicators will be simplified.")

from ..utils.validation import validate_timeseries_data

logger = logging.getLogger(__name__)


class FeatureEngine:
    """
    Feature engineering engine for NSE market data.
    
    Creates comprehensive features including:
    - Price-based features (returns, volatility)
    - Volume-based features
    - Technical indicators
    - Time-based features
    - Market microstructure features
    """
    
    def __init__(self):
        """Initialize feature engine."""
        self.feature_names = []
        self.is_fitted = False
        
    def generate_features(
        self, 
        data: pd.DataFrame,
        include_technical: bool = True,
        include_time: bool = True,
        include_volume: bool = True
    ) -> pd.DataFrame:
        """
        Generate comprehensive feature set from market data.
        
        Args:
            data: DataFrame with columns ['date', 'price', 'volume']
            include_technical: Include technical indicators
            include_time: Include time-based features
            include_volume: Include volume-based features
            
        Returns:
            DataFrame with engineered features
        """
        try:
            # Validate input data
            validate_timeseries_data(data)
            
            # Start with copy of original data
            features = data.copy()
            
            # Ensure proper date handling
            if 'date' in features.columns:
                features['date'] = pd.to_datetime(features['date'])
                features = features.set_index('date')
            
            # Basic price features
            features = self._add_price_features(features)
            
            # Volume features
            if include_volume and 'volume' in features.columns:
                features = self._add_volume_features(features)
            
            # Technical indicators
            if include_technical:
                features = self._add_technical_indicators(features)
            
            # Time-based features
            if include_time:
                features = self._add_time_features(features)
            
            # Market microstructure features
            features = self._add_microstructure_features(features)
            
            # Remove original price column but keep returns
            if 'price' in features.columns:
                features = features.drop('price', axis=1)
            
            # Remove rows with NaN values
            features = features.dropna()
            
            # Store feature names
            self.feature_names = list(features.columns)
            self.is_fitted = True
            
            logger.info(f"Generated {len(self.feature_names)} features from {len(data)} observations")
            
            return features
            
        except Exception as e:
            logger.error(f"Error in feature generation: {e}")
            raise
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add price-based features.
        
        Args:
            df: Input dataframe with price column
            
        Returns:
            DataFrame with additional price features
        """
        # Log returns
        df['returns'] = np.log(df['price'] / df['price'].shift(1))
        
        # Absolute returns
        df['abs_returns'] = np.abs(df['returns'])
        
        # Squared returns (proxy for volatility)
        df['squared_returns'] = df['returns'] ** 2
        
        # Lagged returns
        for lag in [1, 2, 3, 5]:
            df[f'returns_lag_{lag}'] = df['returns'].shift(lag)
        
        # Rolling statistics
        for window in [5, 10, 20, 30]:
            # Rolling mean returns
            df[f'returns_ma_{window}'] = df['returns'].rolling(window).mean()
            
            # Rolling volatility
            df[f'volatility_{window}'] = df['returns'].rolling(window).std()
            
            # Rolling skewness
            df[f'skewness_{window}'] = df['returns'].rolling(window).skew()
            
            # Rolling kurtosis
            df[f'kurtosis_{window}'] = df['returns'].rolling(window).kurt()
        
        # Price momentum
        for window in [5, 10, 20]:
            df[f'momentum_{window}'] = (df['price'] / df['price'].shift(window)) - 1
        
        # Price relative to moving averages
        for window in [10, 20, 50]:
            ma = df['price'].rolling(window).mean()
            df[f'price_vs_ma_{window}'] = (df['price'] / ma) - 1
        
        # High-low range (using approximation)
        df['hl_range'] = df['abs_returns']  # Simplified proxy
        
        # Price gaps (weekend/overnight effects)
        df['price_gap'] = df['returns'].where(df.index.weekday == 0, 0)  # Monday gaps
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features."""
        
        # Volume changes
        df['volume_change'] = df['volume'].pct_change()
        
        # Volume relative to moving average
        for window in [5, 10, 20]:
            vol_ma = df['volume'].rolling(window).mean()
            df[f'volume_ratio_{window}'] = df['volume'] / vol_ma
        
        # Volume-price correlation
        for window in [10, 20]:
            df[f'volume_price_corr_{window}'] = df['volume'].rolling(window).corr(df['price'])
        
        # Volume spikes
        vol_std = df['volume'].rolling(20).std()
        vol_mean = df['volume'].rolling(20).mean()
        df['volume_spike'] = (df['volume'] - vol_mean) / vol_std
        
        # On-balance volume approximation
        obv = (df['volume'] * np.sign(df['returns'])).cumsum()
        df['obv'] = obv
        df['obv_ma_10'] = obv.rolling(10).mean()
        
        # Volume-weighted average price approximation
        df['vwap_approx'] = (df['price'] * df['volume']).rolling(20).sum() / df['volume'].rolling(20).sum()
        df['price_vs_vwap'] = (df['price'] / df['vwap_approx']) - 1
        
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators."""
        
        price = df['price'].values
        
        if TALIB_AVAILABLE:
            # RSI
            df['rsi'] = talib.RSI(price, timeperiod=14)
            
            # MACD
            macd, macd_signal, macd_hist = talib.MACD(price)
            df['macd'] = macd
            df['macd_signal'] = macd_signal
            df['macd_histogram'] = macd_hist
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(price)
            df['bb_upper'] = bb_upper
            df['bb_lower'] = bb_lower
            df['bb_width'] = (bb_upper - bb_lower) / bb_middle
            df['bb_position'] = (price - bb_lower) / (bb_upper - bb_lower)
            
            # Average True Range
            high = price * (1 + df['abs_returns'])  # Approximation
            low = price * (1 - df['abs_returns'])   # Approximation
            df['atr'] = talib.ATR(high, low, price, timeperiod=14)
            
        else:
            # Simplified versions without TA-Lib
            
            # Simple RSI approximation
            delta = df['price'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta).where(delta < 0, 0).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Simple MACD
            ema_12 = df['price'].ewm(span=12).mean()
            ema_26 = df['price'].ewm(span=26).mean()
            df['macd'] = ema_12 - ema_26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # Simple Bollinger Bands
            bb_middle = df['price'].rolling(20).mean()
            bb_std = df['price'].rolling(20).std()
            df['bb_upper'] = bb_middle + (2 * bb_std)
            df['bb_lower'] = bb_middle - (2 * bb_std)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / bb_middle
            df['bb_position'] = (df['price'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Stochastic oscillator approximation
        high_20 = df['price'].rolling(20).max()
        low_20 = df['price'].rolling(20).min()
        df['stoch_k'] = 100 * (df['price'] - low_20) / (high_20 - low_20)
        df['stoch_d'] = df['stoch_k'].rolling(3).mean()
        
        # Williams %R
        df['williams_r'] = -100 * (high_20 - df['price']) / (high_20 - low_20)
        
        # Commodity Channel Index approximation
        typical_price = df['price']  # Simplified (normally (H+L+C)/3)
        sma_tp = typical_price.rolling(20).mean()
        mad = typical_price.rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())))
        df['cci'] = (typical_price - sma_tp) / (0.015 * mad)
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features."""
        
        # Day of week (Monday effect, etc.)
        df['day_of_week'] = df.index.dayofweek
        df['is_monday'] = (df.index.dayofweek == 0).astype(int)
        df['is_friday'] = (df.index.dayofweek == 4).astype(int)
        
        # Month of year (seasonal effects)
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        
        # NSE-specific calendar effects
        df['is_quarter_end'] = df.index.to_series().apply(
            lambda x: x.month in [3, 6, 9, 12] and x.day > 25
        ).astype(int)
        
        # Kenyan holiday approximations (simplified)
        # In practice, would use proper holiday calendar
        df['is_year_end'] = (df.index.month == 12).astype(int)
        df['is_new_year'] = (df.index.month == 1).astype(int)
        
        # Time to expiry effects (quarterly options)
        # Calculate days to next quarter end
        def days_to_quarter_end(date):
            quarter_ends = {
                1: datetime(date.year, 3, 31),
                2: datetime(date.year, 6, 30),
                3: datetime(date.year, 9, 30),
                4: datetime(date.year, 12, 31)
            }
            current_quarter = (date.month - 1) // 3 + 1
            next_quarter_end = quarter_ends[current_quarter]
            if date > next_quarter_end:
                # Move to next quarter
                if current_quarter == 4:
                    next_quarter_end = datetime(date.year + 1, 3, 31)
                else:
                    next_quarter = current_quarter + 1
                    next_quarter_end = quarter_ends[next_quarter]
            return (next_quarter_end - date).days
        
        df['days_to_expiry'] = df.index.to_series().apply(days_to_quarter_end)
        df['time_to_expiry_norm'] = df['days_to_expiry'] / 90  # Normalize to quarter length
        
        # Cyclical encoding for time features
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def _add_microstructure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market microstructure features."""
        
        # Realized volatility measures
        for window in [5, 10, 20]:
            df[f'realized_vol_{window}'] = df['squared_returns'].rolling(window).sum()
        
        # Jump detection (simplified)
        vol_threshold = df['returns'].rolling(20).std() * 3
        df['jump_indicator'] = (df['abs_returns'] > vol_threshold).astype(int)
        
        # Volatility regime indicators
        short_vol = df['returns'].rolling(10).std()
        long_vol = df['returns'].rolling(30).std()
        df['vol_regime'] = (short_vol / long_vol) - 1
        
        # Return autocorrelation
        for lag in [1, 2, 5]:
            df[f'autocorr_lag_{lag}'] = df['returns'].rolling(20).apply(
                lambda x: x.autocorr(lag=lag) if len(x) > lag else np.nan
            )
        
        # Volatility clustering measure
        df['vol_clustering'] = df['abs_returns'].rolling(10).std()
        
        # Market stress indicators
        # Based on extreme returns
        df['stress_indicator'] = (df['abs_returns'] > df['abs_returns'].rolling(60).quantile(0.95)).astype(int)
        
        # Liquidity proxy (inverse of volatility)
        df['liquidity_proxy'] = 1 / (df['volatility_20'] + 1e-6)
        
        return df
    
    def get_feature_importance(self, target: pd.Series) -> pd.DataFrame:
        """
        Calculate feature importance using correlation analysis.
        
        Args:
            target: Target variable (e.g., future volatility)
            
        Returns:
            DataFrame with feature importance scores
        """
        if not self.is_fitted:
            raise ValueError("Feature engine must be fitted first")
        
        # Calculate correlations with target
        correlations = []
        for feature in self.feature_names:
            try:
                corr = np.abs(target.corr(target.shift(-1)))  # Simplified
                correlations.append({
                    'feature': feature,
                    'importance': corr,
                    'abs_correlation': abs(corr)
                })
            except:
                correlations.append({
                    'feature': feature,
                    'importance': 0.0,
                    'abs_correlation': 0.0
                })
        
        importance_df = pd.DataFrame(correlations)
        importance_df = importance_df.sort_values('abs_correlation', ascending=False)
        
        return importance_df
    
    def select_top_features(
        self, 
        features: pd.DataFrame, 
        target: pd.Series, 
        top_k: int = 20
    ) -> pd.DataFrame:
        """
        Select top k most important features.
        
        Args:
            features: Feature dataframe
            target: Target variable
            top_k: Number of top features to select
            
        Returns:
            DataFrame with selected features
        """
        # Calculate feature importance
        importance = self.get_feature_importance(target)
        
        # Select top features
        top_features = importance.head(top_k)['feature'].tolist()
        
        # Return selected features
        selected_features = features[top_features]
        
        logger.info(f"Selected {len(top_features)} top features")
        
        return selected_features
    
    def transform_for_lstm(
        self, 
        features: pd.DataFrame, 
        sequence_length: int = 60
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Transform features for LSTM input.
        
        Args:
            features: Feature dataframe
            sequence_length: Length of input sequences
            
        Returns:
            Tuple of (transformed_features, feature_names)
        """
        # Select numeric features only
        numeric_features = features.select_dtypes(include=[np.number])
        
        # Handle missing values
        numeric_features = numeric_features.fillna(method='ffill').fillna(0)
        
        # Scale features to [0, 1] range for LSTM
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(numeric_features)
        
        # Create sequences
        sequences = []
        for i in range(sequence_length, len(scaled_features)):
            sequences.append(scaled_features[i-sequence_length:i])
        
        sequences = np.array(sequences)
        
        return sequences, list(numeric_features.columns)


# Utility functions
def engineer_basic_features(price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Quick feature engineering for basic use cases.
    
    Args:
        price_data: DataFrame with price data
        
    Returns:
        DataFrame with basic features
    """
    engine = FeatureEngine()
    return engine.generate_features(
        price_data, 
        include_technical=False,
        include_time=False,
        include_volume=False
    )


def validate_features_for_prediction(features: pd.DataFrame) -> bool:
    """
    Validate that features are suitable for prediction.
    
    Args:
        features: Feature dataframe
        
    Returns:
        True if features are valid
    """
    # Check for excessive missing values
    missing_pct = features.isnull().sum() / len(features)
    if any(missing_pct > 0.5):
        logger.warning("Some features have >50% missing values")
        return False
    
    # Check for infinite values
    if features.replace([np.inf, -np.inf], np.nan).isnull().sum().sum() > 0:
        logger.warning("Features contain infinite values")
        return False
    
    # Check for constant features
    constant_features = features.nunique() == 1
    if any(constant_features):
        logger.warning(f"Found {sum(constant_features)} constant features")
    
    return True



