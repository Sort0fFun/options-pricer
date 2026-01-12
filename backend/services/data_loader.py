"""
Data Loading Utilities for Volatility Forecasting

This module handles loading and decompression of Databento GLBX-MDP3 trade data
from .zst compressed files, creating OHLCV bars, and caching processed data.
"""

import os
import io
import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from functools import lru_cache

import zstandard as zstd
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads and processes Databento trade data from .zst compressed files.
    """

    def __init__(self, data_dir: str, cache_dir: Optional[str] = None):
        """
        Initialize data loader.

        Args:
            data_dir: Directory containing .zst trade data files
            cache_dir: Directory for caching processed data (optional)
        """
        self.data_dir = Path(data_dir)
        self.cache_dir = Path(cache_dir) if cache_dir else None

        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache directory: {self.cache_dir}")

    def load_zst_file(self, filepath: Path) -> pd.DataFrame:
        """
        Load a single zstd compressed CSV file.

        Args:
            filepath: Path to the .zst compressed CSV file

        Returns:
            DataFrame with trade data
        """
        try:
            with open(filepath, 'rb') as f:
                dctx = zstd.ZstdDecompressor()
                reader = dctx.stream_reader(f)
                chunks = []

                while True:
                    chunk = reader.read(1024 * 1024 * 10)  # 10MB chunks
                    if not chunk:
                        break
                    chunks.append(chunk)

                data = b''.join(chunks)

            df = pd.read_csv(io.BytesIO(data))
            logger.debug(f"Loaded {len(df):,} records from {filepath.name}")
            return df

        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            raise

    def load_symbol_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Load all trade data for a specific symbol.

        Args:
            symbol: Futures symbol (e.g., 'NQZ5')
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with filtered trade data
        """
        # Check cache first
        if use_cache and self.cache_dir:
            cache_file = self.cache_dir / f"{symbol}_raw_data.parquet"
            if cache_file.exists():
                logger.info(f"Loading {symbol} from cache")
                df = pd.read_parquet(cache_file)

                # Apply date filters if specified
                if start_date or end_date:
                    df['ts_event'] = pd.to_datetime(df['ts_event'])
                    if start_date:
                        df = df[df['ts_event'] >= start_date]
                    if end_date:
                        df = df[df['ts_event'] <= end_date]

                return df

        # Load from .zst files
        logger.info(f"Loading {symbol} from .zst files")
        files = sorted(self.data_dir.glob('glbx-mdp3-*.zst'))

        if not files:
            raise FileNotFoundError(
                f"No .zst files found in {self.data_dir}. "
                f"Expected files like: glbx-mdp3-20250928.trades.csv.zst"
            )

        logger.info(f"Found {len(files)} data files")

        # Load and filter data
        all_dfs = []
        for filepath in files:
            try:
                df = self.load_zst_file(filepath)

                if len(df) == 0 or 'symbol' not in df.columns:
                    continue

                # Filter by symbol
                df_filtered = df[df['symbol'] == symbol].copy()

                if len(df_filtered) > 0:
                    all_dfs.append(df_filtered)
                    logger.debug(f"{filepath.name}: {len(df_filtered):,} {symbol} trades")

            except Exception as e:
                logger.warning(f"Skipping {filepath.name}: {e}")
                continue

        if not all_dfs:
            raise ValueError(f"No data found for symbol {symbol}")

        # Combine all data
        combined = pd.concat(all_dfs, ignore_index=True)
        combined['ts_event'] = pd.to_datetime(combined['ts_event'])
        combined = combined.sort_values('ts_event').reset_index(drop=True)

        logger.info(f"Loaded {len(combined):,} trades for {symbol}")
        logger.info(f"Date range: {combined['ts_event'].min()} to {combined['ts_event'].max()}")

        # Save to cache
        if self.cache_dir:
            cache_file = self.cache_dir / f"{symbol}_raw_data.parquet"
            combined.to_parquet(cache_file, compression='snappy')
            logger.info(f"Cached data to {cache_file}")

        # Apply date filters if specified
        if start_date or end_date:
            if start_date:
                combined = combined[combined['ts_event'] >= start_date]
            if end_date:
                combined = combined[combined['ts_event'] <= end_date]

        return combined

    def create_ohlcv_bars(
        self,
        trade_data: pd.DataFrame,
        freq: str = '5min',
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Aggregate tick data into OHLCV bars.

        Args:
            trade_data: DataFrame with columns ['ts_event', 'price', 'size', 'side']
            freq: Bar frequency (e.g., '5min', '1min', '1H')
            use_cache: Whether to use cached bars if available

        Returns:
            DataFrame with OHLCV bars and microstructure features
        """
        if trade_data.empty:
            raise ValueError("Trade data is empty")

        # Check cache
        if use_cache and self.cache_dir and 'symbol' in trade_data.columns:
            symbol = trade_data['symbol'].iloc[0]
            cache_file = self.cache_dir / f"{symbol}_bars_{freq}.parquet"

            if cache_file.exists():
                logger.info(f"Loading {symbol} bars from cache")
                return pd.read_parquet(cache_file)

        # Create bars
        df = trade_data.copy()
        df = df.set_index('ts_event')

        # Calculate signed volume for order flow imbalance
        df['signed_volume'] = df['size'] * df['side'].map({'B': 1, 'A': -1, 'N': 0})

        # Aggregate into bars
        bars = df.groupby(pd.Grouper(freq=freq)).agg({
            'price': ['first', 'max', 'min', 'last', 'std', 'count'],
            'size': ['sum', 'mean', 'max', 'std'],
            'signed_volume': 'sum'
        })

        # Flatten column names
        bars.columns = [
            'open', 'high', 'low', 'close', 'price_std', 'tick_count',
            'volume', 'avg_trade_size', 'max_trade_size', 'trade_size_std',
            'order_flow_imbalance'
        ]

        # Remove bars with no volume
        bars = bars[bars['volume'] > 0].copy()

        # Calculate returns
        bars['return'] = bars['close'].pct_change()
        bars['log_return'] = np.log(bars['close'] / bars['close'].shift(1))

        # Calculate bar characteristics
        bars['range'] = (bars['high'] - bars['low']) / bars['close']
        bars['body'] = abs(bars['close'] - bars['open']) / bars['close']
        bars['upper_wick'] = (bars['high'] - bars[['open', 'close']].max(axis=1)) / bars['close']
        bars['lower_wick'] = (bars[['open', 'close']].min(axis=1) - bars['low']) / bars['close']
        bars['ofi_normalized'] = bars['order_flow_imbalance'] / bars['volume']

        logger.info(f"Created {len(bars):,} bars at {freq} frequency")
        logger.info(f"Date range: {bars.index.min()} to {bars.index.max()}")

        # Cache bars
        if self.cache_dir and 'symbol' in trade_data.columns:
            symbol = trade_data['symbol'].iloc[0]
            cache_file = self.cache_dir / f"{symbol}_bars_{freq}.parquet"
            bars.to_parquet(cache_file, compression='snappy')
            logger.info(f"Cached bars to {cache_file}")

        return bars

    def get_available_symbols(self) -> List[str]:
        """
        Get list of available symbols from data files.

        Returns:
            List of symbol strings
        """
        files = list(self.data_dir.glob('glbx-mdp3-*.zst'))[:5]  # Sample first 5 files

        symbols = set()
        for filepath in files:
            try:
                df = self.load_zst_file(filepath)
                if 'symbol' in df.columns:
                    symbols.update(df['symbol'].unique())
            except Exception as e:
                logger.warning(f"Error reading {filepath}: {e}")
                continue

        return sorted(list(symbols))

    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cached data.

        Args:
            symbol: If specified, clear only this symbol's cache. Otherwise clear all.
        """
        if not self.cache_dir:
            return

        if symbol:
            # Clear specific symbol
            for file in self.cache_dir.glob(f"{symbol}_*.parquet"):
                file.unlink()
                logger.info(f"Deleted cache file: {file}")
        else:
            # Clear all cache
            for file in self.cache_dir.glob("*.parquet"):
                file.unlink()
                logger.info(f"Deleted cache file: {file}")


# Singleton instance
_data_loader = None


def get_data_loader(data_dir: str, cache_dir: Optional[str] = None) -> DataLoader:
    """
    Get or create singleton DataLoader instance.

    Args:
        data_dir: Directory containing .zst files
        cache_dir: Directory for caching

    Returns:
        DataLoader instance
    """
    global _data_loader

    if _data_loader is None:
        _data_loader = DataLoader(data_dir, cache_dir)

    return _data_loader
