"""
Market service - handles market status and NSE futures data.
"""
import os
import pandas as pd
import pytz
from datetime import datetime
from typing import Optional, List


class MarketService:
    """Service for market status and NSE futures data."""

    MARKET_TIMEZONE = 'Africa/Nairobi'
    MARKET_OPEN_HOUR = 9  # 9:00 AM
    MARKET_CLOSE_HOUR = 15  # 3:00 PM

    @staticmethod
    def get_market_status() -> dict:
        """
        Get current NSE market status.

        Returns:
            dict: Market status information
        """
        # Get current time in Nairobi timezone
        tz = pytz.timezone(MarketService.MARKET_TIMEZONE)
        now = datetime.now(tz)

        # Check if it's a weekday (Monday=0, Sunday=6)
        is_weekday = now.weekday() < 5

        # Get current hour
        current_hour = now.hour
        current_minute = now.minute

        # Determine if market is open
        is_open = (
            is_weekday and
            current_hour >= MarketService.MARKET_OPEN_HOUR and
            current_hour < MarketService.MARKET_CLOSE_HOUR
        )

        # Calculate time message
        if is_open:
            # Calculate time until close
            close_time = now.replace(hour=MarketService.MARKET_CLOSE_HOUR, minute=0, second=0)
            time_diff = close_time - now
            hours = time_diff.seconds // 3600
            minutes = (time_diff.seconds % 3600) // 60
            message = f"Closes in {hours}h {minutes}m"
            status = "OPEN"
        else:
            if not is_weekday:
                message = "Closed - Weekend"
            elif current_hour < MarketService.MARKET_OPEN_HOUR:
                # Calculate time until open
                open_time = now.replace(hour=MarketService.MARKET_OPEN_HOUR, minute=0, second=0)
                time_diff = open_time - now
                hours = time_diff.seconds // 3600
                minutes = (time_diff.seconds % 3600) // 60
                message = f"Opens in {hours}h {minutes}m"
            else:
                message = "Closed - After hours"
            status = "CLOSED"

        return {
            'status': status,
            'message': message,
            'current_time': now.isoformat(),
            'market_open': f"{MarketService.MARKET_OPEN_HOUR:02d}:00",
            'market_close': f"{MarketService.MARKET_CLOSE_HOUR:02d}:00",
            'is_trading_day': is_weekday
        }

    @staticmethod
    def get_futures_data(
        contracts: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        data_file: Optional[str] = None
    ) -> dict:
        """
        Load and filter NSE futures market data from CSV.

        Args:
            contracts: List of contract symbols to filter
            types: List of contract types to filter
            data_file: Path to CSV data file

        Returns:
            dict: Filtered futures data
        """
        try:
            # Get data file path from config or environment
            if data_file is None:
                from flask import current_app
                data_file = current_app.config.get('NSE_DATA_FILE')

            if not data_file or not os.path.exists(data_file):
                return {
                    'data': [],
                    'total': 0,
                    'message': 'NSE data file not found'
                }

            # Load CSV
            df = pd.read_csv(data_file)

            # Apply filters
            if contracts:
                df = df[df['Contract'].isin(contracts)]

            if types:
                df = df[df['Type'].isin(types)]

            # Convert to records
            records = df.to_dict('records')

            return {
                'data': records,
                'total': len(records),
                'contracts_available': df['Contract'].unique().tolist() if not df.empty else [],
                'types_available': df['Type'].unique().tolist() if not df.empty else []
            }

        except FileNotFoundError:
            return {
                'data': [],
                'total': 0,
                'message': 'NSE data file not found'
            }
        except Exception as e:
            return {
                'data': [],
                'total': 0,
                'message': f'Error loading data: {str(e)}'
            }
