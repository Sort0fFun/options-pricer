"""
Utility functions and constants for NSE options pricing.

This module contains market-specific data, helper functions, and constants
used throughout the pricing engine.
"""

import numpy as np
from datetime import datetime, time
from typing import Dict, List, Tuple

from .contracts import NSE_FUTURES
import calendar



# NSE trading hours (East Africa Time)
TRADING_HOURS = {
    'market_open': time(9, 0),    # 9:00 AM
    'market_close': time(15, 0),  # 3:00 PM
    'timezone': 'EAT',            # East Africa Time
    'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
}

# Standard expiry months (quarterly cycle)
EXPIRY_MONTHS = {
    'Q1': 3,   # March
    'Q2': 6,   # June  
    'Q3': 9,   # September
    'Q4': 12   # December
}

# Kenya-specific financial constants
KENYA_MARKET_DATA = {
    'currency': 'KES',
    'central_bank': 'Central Bank of Kenya',
    'benchmark_rate': 'CBK Rate',
    'typical_vol_range': (0.15, 0.40),  # 15% to 40% annual volatility
    'typical_rate_range': (0.08, 0.14),  # 8% to 14% annual rates
    'market_holidays': [
        'New Year\'s Day', 'Good Friday', 'Easter Monday',
        'Labour Day', 'Madaraka Day', 'Mashujaa Day', 
        'Jamhuri Day', 'Christmas Day', 'Boxing Day'
    ]
}


def calculate_time_to_expiry(expiry_date: datetime, current_date: datetime = None) -> float:
    """
    Calculate time to expiry in years from dates.
    
    Args:
        expiry_date: Option expiration date
        current_date: Current date (defaults to today)
        
    Returns:
        Time to expiry in decimal years
    """
    if current_date is None:
        current_date = datetime.now()
    
    if expiry_date <= current_date:
        raise ValueError("Expiry date must be in the future")
    
    days_to_expiry = (expiry_date - current_date).days
    return days_to_expiry / 365.25


def get_quarterly_expiry_dates(year: int) -> List[datetime]:
    """
    Get quarterly expiry dates for a given year (NSE convention).
    
    Options typically expire on the third Friday of the expiry month.
    
    Args:
        year: Year for which to calculate expiry dates
        
    Returns:
        List of datetime objects for quarterly expiries
    """
    expiry_dates = []
    
    for month in [3, 6, 9, 12]:  # March, June, September, December
        # Find third Friday of the month
        third_friday = get_third_friday(year, month)
        expiry_dates.append(third_friday)
    
    return expiry_dates


def get_third_friday(year: int, month: int) -> datetime:
    """
    Get the third Friday of a given month and year.
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        datetime object for the third Friday
    """
    # Get first day of month
    first_day = datetime(year, month, 1)
    
    # Find first Friday
    days_until_friday = (4 - first_day.weekday()) % 7
    first_friday = first_day.replace(day=1 + days_until_friday)
    
    # Add two weeks to get third Friday
    third_friday = first_friday.replace(day=first_friday.day + 14)
    
    return third_friday


def format_currency(amount: float, currency: str = 'KES') -> str:
    """
    Format amount as currency string for display.
    
    Args:
        amount: Amount to format
        currency: Currency code (default: KES)
        
    Returns:
        Formatted currency string
    """
    if currency.upper() == 'KES':
        return f"KES {amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def calculate_contract_value(option_price: float, multiplier: int) -> float:
    """
    Calculate total contract value based on option price and multiplier.
    
    Args:
        option_price: Per-unit option price
        multiplier: Contract multiplier
        
    Returns:
        Total contract value
    """
    return option_price * multiplier


def get_business_days_to_expiry(current_date: datetime, expiry_date: datetime) -> int:
    """
    Calculate number of business days to expiry (excluding weekends and holidays).
    
    Args:
        current_date: Current date
        expiry_date: Expiry date
        
    Returns:
        Number of business days
    """
    business_days = np.busday_count(
        current_date.date(), 
        expiry_date.date(),
        weekmask='1111100'  # Monday-Friday
    )
    return int(business_days)


def annualize_volatility(daily_vol: float) -> float:
    """
    Convert daily volatility to annual volatility.
    
    Args:
        daily_vol: Daily volatility (decimal)
        
    Returns:
        Annual volatility (decimal)
    """
    return daily_vol * np.sqrt(252)  # 252 trading days per year


def daily_volatility(annual_vol: float) -> float:
    """
    Convert annual volatility to daily volatility.
    
    Args:
        annual_vol: Annual volatility (decimal)
        
    Returns:
        Daily volatility (decimal)
    """
    return annual_vol / np.sqrt(252)


def calculate_implied_forward_rate(
    spot_price: float, 
    futures_price: float, 
    time_to_expiry: float
) -> float:
    """
    Calculate implied risk-free rate from spot and futures prices.
    
    Formula: r = ln(F/S) / T
    
    Args:
        spot_price: Current spot price
        futures_price: Current futures price
        time_to_expiry: Time to expiry in years
        
    Returns:
        Implied risk-free rate (annual)
    """
    return np.log(futures_price / spot_price) / time_to_expiry


def generate_strike_ladder(
    current_price: float, 
    num_strikes: int = 11, 
    spacing_pct: float = 0.05
) -> List[float]:
    """
    Generate a ladder of strike prices around the current price.
    
    Args:
        current_price: Current underlying price
        num_strikes: Number of strikes to generate (should be odd)
        spacing_pct: Percentage spacing between strikes
        
    Returns:
        List of strike prices
    """
    if num_strikes % 2 == 0:
        num_strikes += 1  # Ensure odd number for symmetry
    
    center_index = num_strikes // 2
    strikes = []
    
    for i in range(num_strikes):
        multiplier = 1 + (i - center_index) * spacing_pct
        strike = current_price * multiplier
        strikes.append(round(strike, 2))
    
    return strikes


def calculate_moneyness(spot_price: float, strike_price: float) -> Dict[str, float]:
    """
    Calculate various moneyness metrics for an option.
    
    Args:
        spot_price: Current underlying price
        strike_price: Strike price
        
    Returns:
        Dictionary with moneyness metrics
    """
    return {
        'absolute_moneyness': spot_price - strike_price,
        'relative_moneyness': spot_price / strike_price,
        'log_moneyness': np.log(spot_price / strike_price),
        'percentage_moneyness': (spot_price - strike_price) / strike_price
    }


def is_market_open(current_time: datetime = None) -> bool:
    """
    Check if NSE market is currently open.
    
    Args:
        current_time: Time to check (defaults to now)
        
    Returns:
        True if market is open, False otherwise
    """
    if current_time is None:
        current_time = datetime.now()
    
    # Check if it's a weekday
    if current_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check if within trading hours
    current_time_only = current_time.time()
    return (TRADING_HOURS['market_open'] <= current_time_only <= 
            TRADING_HOURS['market_close'])


def round_to_tick_size(price: float, tick_size: float) -> float:
    """
    Round price to the nearest valid tick size.
    
    Args:
        price: Price to round
        tick_size: Minimum price increment
        
    Returns:
        Price rounded to tick size
    """
    return round(price / tick_size) * tick_size


def get_contract_multiplier(symbol: str) -> int:
    """
    Get the contract multiplier for a given NSE symbol.
    
    Args:
        symbol: NSE contract symbol
        
    Returns:
        Contract multiplier
        
    Raises:
        KeyError: If symbol is not found
    """
    return NSE_FUTURES[symbol.upper()]['contract_size']


def validate_trading_hours(target_time: datetime = None) -> Tuple[bool, str]:
    """
    Validate if a given time is within trading hours.
    
    Args:
        target_time: Time to validate (defaults to now)
        
    Returns:
        Tuple of (is_valid, message)
    """
    if target_time is None:
        target_time = datetime.now()
    
    if target_time.weekday() >= 5:
        return False, "Market is closed on weekends"
    
    time_only = target_time.time()
    
    if time_only < TRADING_HOURS['market_open']:
        return False, f"Market opens at {TRADING_HOURS['market_open']}"
    
    if time_only > TRADING_HOURS['market_close']:
        return False, f"Market closed at {TRADING_HOURS['market_close']}"
    
    return True, "Market is open"


# Constants for calculations
DAYS_PER_YEAR = 365.25
TRADING_DAYS_PER_YEAR = 252
SECONDS_PER_DAY = 86400
MINUTES_PER_TRADING_DAY = 360  # 6 hours * 60 minutes

# Numerical constants
EPSILON = 1e-10  # Small number for numerical stability
MAX_ITERATIONS = 100  # For iterative calculations
CONVERGENCE_TOLERANCE = 1e-6