"""
NSE Data Service

Service for loading and processing NSE derivatives data from CSV files.
Handles data cleaning, symbol extraction, and price calculations.
"""

import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

import pandas as pd
import numpy as np

from backend.models.nse_symbols import NSE_SYMBOLS

logger = logging.getLogger(__name__)


class NSEDataService:
    """Service for handling NSE derivatives data loading and processing."""
    
    _instance = None
    _data_path = None
    
    def __init__(self, csv_path: str = None):
        """
        Initialize NSE Data Service.
        
        Args:
            csv_path: Path to the NSE derivatives CSV file
        """
        if csv_path is None:
            base_dir = Path(__file__).parent.parent.parent
            csv_path = base_dir / "data" / "nse_derivatives.csv"
        
        self.csv_path = str(csv_path)
        self._data = None
        self._symbols_cache = {}
        
    @classmethod
    def init_app(cls, app):
        """Initialize service with Flask app."""
        data_path = app.config.get('NSE_DATA_PATH', 'data/nse_derivatives.csv')
        cls._data_path = data_path
        cls._instance = cls(data_path)
        logger.info(f"NSE Data Service initialized with: {data_path}")
        
    @classmethod
    def get_instance(cls) -> 'NSEDataService':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(cls._data_path)
        return cls._instance
        
    def load_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load and parse NSE data from CSV.
        
        Args:
            force_reload: Force reload from disk even if cached
            
        Returns:
            Cleaned DataFrame with NSE derivatives data
        """
        if self._data is not None and not force_reload:
            return self._data
            
        if not os.path.exists(self.csv_path):
            logger.warning(f"NSE data file not found: {self.csv_path}")
            return pd.DataFrame()
        
        try:
            # Read CSV - skip first header line
            df = pd.read_csv(self.csv_path, skiprows=1, on_bad_lines='skip')
            logger.info(f"Loaded {len(df)} rows from {self.csv_path}")
            
            # Check columns and rename if needed
            # The CSV may have columns like: Contract Type, ISIN, Listing Date, Expiry Date, Days to, MTM, Previous, etc.
            if df.columns[0] != 'Contract Type' and len(df.columns) >= 2:
                # Try to fix column names
                expected_cols = ['Contract Type', 'ISIN', 'Listing Date', 'Expiry Date', 'Days to', 
                                'MTM', 'Previous', 'Total Volume', 'Total', 'Open Interest']
                if len(df.columns) >= len(expected_cols):
                    df.columns = expected_cols[:len(df.columns)]
            
            # Clean data - remove header rows, empty rows, and section headers
            if 'Contract Type' in df.columns:
                df = df[df['Contract Type'].notna()]
                # Remove rows that are section headers or contain metadata
                df = df[~df['Contract Type'].astype(str).str.contains(
                    'DERIVATIVES|PRICELIST|Contract Type|NAIROBI|INDEX \\(|Single Stock|Jan-|Feb-|Mar-|Apr-|May-|Jun-|Jul-|Aug-|Sep-|Oct-|Nov-|Dec-', 
                    case=False, 
                    na=False,
                    regex=True
                )]
                # Keep rows that look like actual date entries (start with digit or contain KE)
                df = df[
                    df['Contract Type'].astype(str).str.match(r'^\d|^KE', na=False) |
                    df['ISIN'].astype(str).str.startswith('KE', na=False) if 'ISIN' in df.columns else True
                ]
            
            # Handle the special CSV format where Contract Type column contains expiry dates
            # and actual contract info is in a header row above
            if 'Contract Type' in df.columns:
                # Try to extract symbol from the data pattern
                df['Symbol'] = self._extract_symbol_from_context(df)
            
            # Clean numeric columns - handle comma formatting and spaces
            numeric_cols = ['MTM', 'Previous', 'Open Interest', 'Days to', 'Total Volume', 'Total']
            for col in numeric_cols:
                if col in df.columns:
                    # Remove commas, spaces, quotes
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '').str.replace('"', '').str.strip()
                    df[col] = df[col].replace(['-', '', 'nan', 'None', 'NaN'], np.nan)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Rename columns for consistency
            column_mapping = {
                'MTM': 'MTM Price',
                'Previous': 'Previous Price',
                'Days to': 'Days to Expiry',
                'Expiry': 'Expiry Date',
                'Listing': 'Listing Date',
                'Expiry Date': 'Expiry Date',
                'Listing Date': 'Listing Date'
            }
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            # Parse dates - handle various formats
            for date_col in ['Expiry Date', 'Listing Date']:
                if date_col in df.columns:
                    # First try the Contract Type column as it might contain dates
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce', format='mixed')
            
            # Also try to parse Contract Type as a date for expiry
            if 'Contract Type' in df.columns and 'Expiry Date' not in df.columns:
                df['Expiry Date'] = pd.to_datetime(df['Contract Type'], errors='coerce', format='mixed')
            
            # Calculate returns where we have valid prices
            if 'MTM Price' in df.columns and 'Previous Price' in df.columns:
                df['Daily Return'] = np.where(
                    df['Previous Price'] > 0,
                    (df['MTM Price'] - df['Previous Price']) / df['Previous Price'],
                    np.nan
                )
                df['Log Return'] = np.where(
                    (df['MTM Price'] > 0) & (df['Previous Price'] > 0),
                    np.log(df['MTM Price'] / df['Previous Price']),
                    np.nan
                )
            
            # Filter out rows without valid price data
            df = df.dropna(subset=['MTM Price', 'Previous Price'])
            
            self._data = df
            logger.info(f"Processed {len(df)} valid rows")
            return self._data
            
        except Exception as e:
            logger.error(f"Error loading NSE data: {e}")
            return pd.DataFrame()
    
    def _extract_symbol_from_context(self, df: pd.DataFrame) -> pd.Series:
        """
        Extract symbols by tracking section headers in the data.
        The CSV has section headers like 'INDEX (N25I)' followed by data rows.
        """
        symbols = []
        current_symbol = None
        
        # Read the original file to get section context
        try:
            with open(self.csv_path, 'r') as f:
                lines = f.readlines()
            
            # Build a mapping of row indices to symbols
            current_sym = None
            row_to_symbol = {}
            data_row_idx = 0
            
            for line in lines:
                line_upper = line.upper().strip()
                
                # Check for section headers
                for sym in NSE_SYMBOLS.keys():
                    if f'({sym})' in line_upper or f' {sym},' in line_upper:
                        current_sym = sym
                        break
                
                # Check for INDEX patterns
                if 'INDEX (N25I)' in line_upper or 'INDEX(N25I)' in line_upper:
                    current_sym = 'N25I'
                elif 'INDEX (25MN)' in line_upper or '(25MN)' in line_upper:
                    current_sym = '25MN'
                elif 'INDEX (10MN)' in line_upper or '(10MN)' in line_upper:
                    current_sym = '10MN'
                
                # If line looks like a data row (starts with date or KE)
                if line.strip() and (line[0].isdigit() or line.startswith('KE')):
                    if current_sym:
                        row_to_symbol[data_row_idx] = current_sym
                    data_row_idx += 1
            
            # Apply to dataframe
            for idx in range(len(df)):
                symbols.append(row_to_symbol.get(idx, None))
                
        except Exception as e:
            logger.warning(f"Could not extract symbols from context: {e}")
            # Fall back to extraction from Contract Type
            symbols = df['Contract Type'].apply(self._extract_symbol).tolist()
        
        return pd.Series(symbols, index=df.index)
    
    def _extract_symbol(self, contract_type) -> Optional[str]:
        """Extract symbol from contract type string."""
        if pd.isna(contract_type):
            return None
        
        contract_str = str(contract_type).upper()
        
        # Check for known symbols
        for symbol in NSE_SYMBOLS.keys():
            if symbol in contract_str:
                return symbol
        
        # Handle special cases for index types
        if 'INDEX' in contract_str or 'N25' in contract_str:
            if 'N25I' in contract_str or 'N25 INDEX' in contract_str:
                return 'N25I'
            elif '25MN' in contract_str or '25 MINI' in contract_str:
                return '25MN'
            elif '10MN' in contract_str or '10 MINI' in contract_str:
                return '10MN'
        
        # Try to extract from parentheses format: "Single Stock Futures (SCOM)"
        if '(' in contract_str and ')' in contract_str:
            match = contract_str.split('(')[-1].replace(')', '').strip()
            if match in NSE_SYMBOLS:
                return match
        
        return None
    
    def get_dropdown_options(self) -> List[Dict]:
        """Get formatted options for dropdown menu."""
        df = self.load_data()
        
        if df.empty:
            # Return default symbols if no data loaded
            return [
                {
                    "value": k,
                    "label": f"{k} - {v['name']}",
                    "type": v["type"],
                    "sector": v.get("sector", "")
                }
                for k, v in NSE_SYMBOLS.items()
            ]
        
        available_symbols = df['Symbol'].dropna().unique().tolist()
        
        options = []
        for symbol in available_symbols:
            if symbol in NSE_SYMBOLS:
                info = NSE_SYMBOLS[symbol]
                options.append({
                    "value": symbol,
                    "label": f"{symbol} - {info['name']}",
                    "type": info['type'],
                    "sector": info.get("sector", "")
                })
            else:
                options.append({
                    "value": symbol,
                    "label": symbol,
                    "type": "UNKNOWN",
                    "sector": ""
                })
        
        return sorted(options, key=lambda x: x['value'])
    
    def get_symbol_data(self, symbol: str) -> pd.DataFrame:
        """Get all data for a specific symbol."""
        df = self.load_data()
        if df.empty:
            return pd.DataFrame()
        return df[df['Symbol'] == symbol.upper()].copy()
    
    def get_latest_prices(self, symbol: str) -> Optional[Dict]:
        """Get latest price data for a symbol."""
        df = self.get_symbol_data(symbol)
        if df.empty:
            return None
        
        # Get latest by expiry date or just last row
        if 'Expiry Date' in df.columns and df['Expiry Date'].notna().any():
            latest = df.sort_values('Expiry Date').iloc[-1]
        else:
            latest = df.iloc[-1]
        
        symbol_info = NSE_SYMBOLS.get(symbol.upper(), {})
        
        return {
            'symbol': symbol.upper(),
            'name': symbol_info.get('name', symbol),
            'type': symbol_info.get('type', 'UNKNOWN'),
            'sector': symbol_info.get('sector', ''),
            'mtm_price': float(latest['MTM Price']) if pd.notna(latest['MTM Price']) else None,
            'previous_price': float(latest['Previous Price']) if pd.notna(latest['Previous Price']) else None,
            'daily_return': float(latest['Daily Return']) if pd.notna(latest.get('Daily Return')) else 0,
            'expiry_date': latest['Expiry Date'].strftime('%Y-%m-%d') if pd.notna(latest.get('Expiry Date')) else None,
            'days_to_expiry': int(latest['Days to Expiry']) if pd.notna(latest.get('Days to Expiry')) else None,
            'open_interest': float(latest['Open Interest']) if pd.notna(latest.get('Open Interest')) else 0,
            'isin': latest.get('ISIN') if 'ISIN' in latest else None,
            'contract_type': latest.get('Contract Type', '')
        }
    
    def get_price_series(self, symbol: str) -> pd.DataFrame:
        """Get price time series for a symbol."""
        df = self.get_symbol_data(symbol)
        if df.empty:
            return pd.DataFrame()
        
        cols = ['Expiry Date', 'MTM Price', 'Previous Price', 'Daily Return', 'Log Return', 'Open Interest']
        available_cols = [c for c in cols if c in df.columns]
        
        return df[available_cols].sort_values('Expiry Date').reset_index(drop=True)
    
    def get_all_expiries(self, symbol: str) -> List[Dict]:
        """Get all available expiry contracts for a symbol."""
        df = self.get_symbol_data(symbol)
        if df.empty:
            return []
        
        expiries = []
        for _, row in df.iterrows():
            expiries.append({
                'expiry_date': row['Expiry Date'].strftime('%Y-%m-%d') if pd.notna(row.get('Expiry Date')) else None,
                'days_to_expiry': int(row['Days to Expiry']) if pd.notna(row.get('Days to Expiry')) else None,
                'mtm_price': float(row['MTM Price']) if pd.notna(row['MTM Price']) else None,
                'previous_price': float(row['Previous Price']) if pd.notna(row['Previous Price']) else None,
                'isin': row.get('ISIN', ''),
                'contract_type': row.get('Contract Type', '')
            })
        
        # Sort by days to expiry
        return sorted(expiries, key=lambda x: x.get('days_to_expiry') or 999)
    
    def get_returns_for_volatility(self, symbol: str) -> np.ndarray:
        """
        Get return series suitable for volatility modeling.
        
        Returns log returns scaled to percentage.
        """
        df = self.get_symbol_data(symbol)
        if df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
        
        # Get log returns
        returns = df['Log Return'].dropna().values
        
        if len(returns) < 4:
            raise ValueError(f"Insufficient data for {symbol}. Need at least 4 observations, got {len(returns)}")
        
        # Scale to percentage for GARCH modeling
        return returns * 100
    
    def get_prices_for_arima(self, symbol: str) -> np.ndarray:
        """Get price series suitable for ARIMA modeling."""
        df = self.get_symbol_data(symbol)
        if df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
        
        prices = df['MTM Price'].dropna().values
        
        if len(prices) < 4:
            raise ValueError(f"Insufficient data for {symbol}. Need at least 4 observations, got {len(prices)}")
        
        return prices
    
    def get_symbols_with_data(self) -> List[Dict]:
        """Get list of symbols that have sufficient data for forecasting."""
        df = self.load_data()
        if df.empty:
            return []
        
        available = []
        for symbol in df['Symbol'].dropna().unique():
            symbol_df = df[df['Symbol'] == symbol]
            valid_returns = symbol_df['Log Return'].dropna()
            
            if len(valid_returns) >= 4:
                info = NSE_SYMBOLS.get(symbol, {})
                available.append({
                    'value': symbol,
                    'label': f"{symbol} - {info.get('name', symbol)}",
                    'type': info.get('type', 'UNKNOWN'),
                    'sector': info.get('sector', ''),
                    'observations': len(valid_returns)
                })
        
        return sorted(available, key=lambda x: x['value'])
