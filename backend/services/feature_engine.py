"""
Feature Engineering Module for Volatility Forecasting

This module generates all features used in the v2_enhanced volatility forecasting model,
including advanced volatility estimators, return features, microstructure features, and more.
"""

import logging
from typing import Dict, List

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class FeatureEngine:
    """
    Generates features for volatility prediction matching the training notebook.
    """

    def __init__(self):
        """Initialize feature engine."""
        self.feature_columns = []

    def calculate_realized_volatility(self, returns: pd.Series, window: int) -> pd.Series:
        """
        Calculate realized volatility using rolling window.

        Args:
            returns: Return series
            window: Rolling window size

        Returns:
            Series of realized volatilities
        """
        return returns.rolling(window=window).std()

    def calculate_parkinson_volatility(
        self,
        high: pd.Series,
        low: pd.Series,
        window: int
    ) -> pd.Series:
        """
        Parkinson volatility estimator - uses high-low range.

        Args:
            high: High prices
            low: Low prices
            window: Rolling window size

        Returns:
            Series of Parkinson volatility estimates
        """
        log_hl = np.log(high / low)
        return np.sqrt((log_hl ** 2).rolling(window=window).mean() / (4 * np.log(2)))

    def calculate_garman_klass_volatility(
        self,
        open_: pd.Series,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        window: int
    ) -> pd.Series:
        """
        Garman-Klass volatility estimator.

        Args:
            open_: Open prices
            high: High prices
            low: Low prices
            close: Close prices
            window: Rolling window size

        Returns:
            Series of Garman-Klass volatility estimates
        """
        log_hl = np.log(high / low) ** 2
        log_co = np.log(close / open_) ** 2
        return np.sqrt(
            (0.5 * log_hl - (2 * np.log(2) - 1) * log_co).rolling(window=window).mean()
        )

    def calculate_rogers_satchell_volatility(
        self,
        open_: pd.Series,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        window: int
    ) -> pd.Series:
        """
        Rogers-Satchell volatility estimator (drift-independent).

        Args:
            open_: Open prices
            high: High prices
            low: Low prices
            close: Close prices
            window: Rolling window size

        Returns:
            Series of Rogers-Satchell volatility estimates
        """
        log_ho = np.log(high / open_)
        log_hc = np.log(high / close)
        log_lo = np.log(low / open_)
        log_lc = np.log(low / close)
        return np.sqrt(
            (log_ho * log_hc + log_lo * log_lc).rolling(window=window).mean()
        )

    def calculate_yang_zhang_volatility(
        self,
        open_: pd.Series,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        window: int
    ) -> pd.Series:
        """
        Yang-Zhang volatility estimator (handles overnight gaps).

        Args:
            open_: Open prices
            high: High prices
            low: Low prices
            close: Close prices
            window: Rolling window size

        Returns:
            Series of Yang-Zhang volatility estimates
        """
        # Overnight volatility
        log_co = np.log(open_ / close.shift(1))
        overnight_vol = log_co.rolling(window=window).var()

        # Open to close volatility (Rogers-Satchell)
        rs_vol = self.calculate_rogers_satchell_volatility(
            open_, high, low, close, window
        ) ** 2

        # Close to close volatility
        log_cc = np.log(close / close.shift(1))
        close_vol = log_cc.rolling(window=window).var()

        # Yang-Zhang combination
        k = 0.34 / (1.34 + (window + 1) / (window - 1))
        yang_zhang = overnight_vol + k * close_vol + (1 - k) * rs_vol

        return np.sqrt(yang_zhang)

    def generate_volatility_features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Generate all volatility-based features.

        Args:
            bars: DataFrame with OHLCV bars

        Returns:
            DataFrame with volatility features added
        """
        df = bars.copy()

        logger.info("Generating volatility features...")

        # Basic realized volatility
        for window in [6, 12, 24, 48, 96]:
            df[f'rvol_{window}'] = self.calculate_realized_volatility(
                df['log_return'], window
            )

        # Parkinson volatility
        for window in [6, 12, 24, 48]:
            df[f'parkinson_{window}'] = self.calculate_parkinson_volatility(
                df['high'], df['low'], window
            )

        # Garman-Klass volatility
        for window in [6, 12, 24, 48]:
            df[f'gk_{window}'] = self.calculate_garman_klass_volatility(
                df['open'], df['high'], df['low'], df['close'], window
            )

        # Rogers-Satchell volatility
        for window in [12, 24, 48]:
            df[f'rs_{window}'] = self.calculate_rogers_satchell_volatility(
                df['open'], df['high'], df['low'], df['close'], window
            )

        # Yang-Zhang volatility
        for window in [12, 24, 48]:
            df[f'yz_{window}'] = self.calculate_yang_zhang_volatility(
                df['open'], df['high'], df['low'], df['close'], window
            )

        # Volatility dynamics
        df['vol_of_vol'] = df['rvol_12'].rolling(12).std()
        df['vol_ratio_12_48'] = df['rvol_12'] / df['rvol_48']
        df['vol_ratio_6_24'] = df['rvol_6'] / df['rvol_24']

        # Volatility regime persistence
        vol_percentile = df['rvol_24'].rolling(window=96).apply(
            lambda x: (x.iloc[-1] > x).sum() / len(x) if len(x) > 0 else 0.5
        )
        df['vol_percentile_96'] = vol_percentile
        df['high_vol_regime'] = (vol_percentile > 0.75).astype(int)
        df['low_vol_regime'] = (vol_percentile < 0.25).astype(int)

        logger.info(f"Generated {len([c for c in df.columns if 'vol' in c.lower()])} volatility features")

        return df

    def generate_return_features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Generate return-based features.

        Args:
            bars: DataFrame with OHLCV bars

        Returns:
            DataFrame with return features added
        """
        df = bars.copy()

        logger.info("Generating return features...")

        # Lagged returns
        for lag in [1, 2, 3, 6, 12]:
            df[f'return_lag_{lag}'] = df['log_return'].shift(lag)

        # Cumulative returns
        for window in [6, 12, 24]:
            df[f'cum_return_{window}'] = df['log_return'].rolling(window).sum()

        # Return momentum
        df['return_momentum'] = df['cum_return_6'] - df['cum_return_12'].shift(6)

        # Absolute return moving averages
        for window in [6, 12, 24]:
            df[f'abs_return_ma_{window}'] = df['log_return'].abs().rolling(window).mean()

        # Higher moments
        df['return_skew_24'] = df['log_return'].rolling(24).skew()
        df['return_kurt_24'] = df['log_return'].rolling(24).kurt()

        logger.info(f"Generated {len([c for c in df.columns if 'return' in c])} return features")

        return df

    def generate_range_features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Generate range-based features.

        Args:
            bars: DataFrame with OHLCV bars

        Returns:
            DataFrame with range features added
        """
        df = bars.copy()

        logger.info("Generating range features...")

        # Range moving averages
        for window in [6, 12, 24]:
            df[f'range_ma_{window}'] = df['range'].rolling(window).mean()

        # Range vs moving average
        df['range_vs_ma'] = df['range'] / df['range_ma_12']

        # Maximum range
        for window in [12, 24, 48]:
            df[f'range_max_{window}'] = df['range'].rolling(window).max()

        logger.info(f"Generated {len([c for c in df.columns if 'range' in c])} range features")

        return df

    def generate_volume_features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Generate volume-based features.

        Args:
            bars: DataFrame with OHLCV bars

        Returns:
            DataFrame with volume features added
        """
        df = bars.copy()

        logger.info("Generating volume features...")

        # Volume moving averages
        for window in [6, 12, 24, 48]:
            df[f'volume_ma_{window}'] = df['volume'].rolling(window).mean()

        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume_ma_24']
        df['volume_trend'] = df['volume_ma_6'] / df['volume_ma_24']
        df['volume_std_24'] = df['volume'].rolling(24).std()

        logger.info(f"Generated {len([c for c in df.columns if 'volume' in c])} volume features")

        return df

    def generate_microstructure_features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Generate microstructure features.

        Args:
            bars: DataFrame with OHLCV bars

        Returns:
            DataFrame with microstructure features added
        """
        df = bars.copy()

        logger.info("Generating microstructure features...")

        # Tick count features
        for window in [6, 12, 24]:
            df[f'tick_count_ma_{window}'] = df['tick_count'].rolling(window).mean()

        df['tick_intensity_ratio'] = df['tick_count'] / df['tick_count_ma_24']

        # Trade size features
        for window in [6, 12, 24]:
            df[f'avg_size_ma_{window}'] = df['avg_trade_size'].rolling(window).mean()

        # Order flow imbalance
        for window in [6, 12, 24]:
            df[f'ofi_ma_{window}'] = df['ofi_normalized'].rolling(window).mean()

        df['ofi_std_24'] = df['ofi_normalized'].rolling(24).std()

        for window in [6, 12, 24]:
            df[f'ofi_cum_{window}'] = df['order_flow_imbalance'].rolling(window).sum()

        logger.info(f"Generated {len([c for c in df.columns if 'ofi' in c or 'tick' in c or 'size' in c])} microstructure features")

        return df

    def generate_time_features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Generate time-based features.

        Args:
            bars: DataFrame with datetime index

        Returns:
            DataFrame with time features added
        """
        df = bars.copy()

        logger.info("Generating time features...")

        # Hour of day
        df['hour'] = df.index.hour
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

        # Day of week
        df['dow'] = df.index.dayofweek
        df['dow_sin'] = np.sin(2 * np.pi * df['dow'] / 5)
        df['dow_cos'] = np.cos(2 * np.pi * df['dow'] / 5)

        # US trading hours (14:00 - 20:00 UTC)
        df['is_us_hours'] = ((df['hour'] >= 14) & (df['hour'] <= 20)).astype(int)

        logger.info("Generated 7 time features")

        return df

    def generate_interaction_features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Generate interaction features.

        Args:
            bars: DataFrame with existing features

        Returns:
            DataFrame with interaction features added
        """
        df = bars.copy()

        logger.info("Generating interaction features...")

        # Volatility x Volume
        df['vol_x_volume'] = df['rvol_12'] * df['volume_ratio']

        # Order flow x Volatility
        df['ofi_x_vol'] = df['ofi_normalized'].abs() * df['rvol_12']

        logger.info("Generated 2 interaction features")

        return df

    def generate_all_features(self, bars: pd.DataFrame) -> pd.DataFrame:
        """
        Generate all features for volatility prediction.

        Args:
            bars: DataFrame with OHLCV bars

        Returns:
            DataFrame with all features
        """
        logger.info("Generating all features...")

        df = bars.copy()

        # Generate feature groups
        df = self.generate_volatility_features(df)
        df = self.generate_return_features(df)
        df = self.generate_range_features(df)
        df = self.generate_volume_features(df)
        df = self.generate_microstructure_features(df)
        df = self.generate_time_features(df)
        df = self.generate_interaction_features(df)

        # Store feature columns for later use
        self.feature_columns = self.get_feature_columns(df)

        logger.info(f"Total features generated: {len(self.feature_columns)}")

        return df

    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of feature columns (excluding OHLCV and other non-feature columns).

        Args:
            df: DataFrame with features

        Returns:
            List of feature column names
        """
        exclude = [
            'open', 'high', 'low', 'close', 'volume', 'log_return', 'return',
            'target_vol_up', 'target_vol_level', 'target_vol_ratio',
            'price_std', 'tick_count', 'avg_trade_size', 'max_trade_size',
            'trade_size_std', 'order_flow_imbalance', 'range', 'body',
            'upper_wick', 'lower_wick', 'ofi_normalized', 'hour', 'dow'
        ]

        return [c for c in df.columns if c not in exclude]
