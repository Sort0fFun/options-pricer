"""
NSE Trading Calendar Utilities

This module provides calendar functionality for the Nairobi Securities Exchange,
including trading days, holidays, and market schedules.
"""

import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class NSECalendar:
    """
    Trading calendar for the Nairobi Securities Exchange.
    
    Handles NSE-specific holidays, trading hours, and business day calculations.
    """
    
    def __init__(self):
        """Initialize NSE calendar with standard holidays and trading rules."""
        self.trading_start_time = "09:00"
        self.trading_end_time = "15:00"
        self.timezone = "Africa/Nairobi"  # East Africa Time (EAT)
        
        # Initialize holiday calendar
        self.fixed_holidays = self._get_fixed_holidays()
        self.variable_holidays = self._get_variable_holidays()
    
    def _get_fixed_holidays(self) -> Set[str]:
        """Get fixed holidays that occur on the same date each year."""
        return {
            "01-01",  # New Year's Day
            "05-01",  # Labour Day
            "06-01",  # Madaraka Day
            "10-20",  # Mashujaa Day (Heroes' Day)
            "12-12",  # Jamhuri Day (Independence Day)
            "12-25",  # Christmas Day
            "12-26",  # Boxing Day
        }
    
    def _get_variable_holidays(self) -> Set[str]:
        """Get variable holidays that change dates each year."""
        # These would need to be calculated or looked up for each year
        # For simplicity, we'll include some common ones
        return {
            # These dates would vary by year - this is a simplified example
            "easter_friday",  # Good Friday (varies each year)
            "easter_monday",  # Easter Monday (varies each year)
            "eid_al_fitr",    # Eid al-Fitr (varies each year)
            "eid_al_adha",    # Eid al-Adha (varies each year)
        }
    
    def is_trading_day(self, date_to_check: datetime) -> bool:
        """
        Check if a given date is a trading day.
        
        Args:
            date_to_check: Date to check
            
        Returns:
            True if it's a trading day, False otherwise
        """
        # Check if weekend
        if date_to_check.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if holiday
        if self.is_holiday(date_to_check):
            return False
        
        return True
    
    def is_holiday(self, date_to_check: datetime) -> bool:
        """
        Check if a given date is a Kenyan public holiday.
        
        Args:
            date_to_check: Date to check
            
        Returns:
            True if it's a holiday, False otherwise
        """
        # Format date as MM-DD for fixed holiday checking
        date_str = date_to_check.strftime("%m-%d")
        
        # Check fixed holidays
        if date_str in self.fixed_holidays:
            return True
        
        # Check for specific variable holidays (simplified)
        # In a full implementation, you would calculate Easter dates, etc.
        year = date_to_check.year
        
        # Easter calculation (simplified - you'd want a proper Easter calculation)
        easter_dates = self._get_easter_dates(year)
        if date_to_check.date() in easter_dates:
            return True
        
        # Check for holidays that fall on weekend and are observed on Monday
        if date_to_check.weekday() == 0:  # Monday
            # Check if previous Friday or weekend had a holiday
            for days_back in [1, 2, 3]:
                check_date = date_to_check - timedelta(days=days_back)
                check_str = check_date.strftime("%m-%d")
                if check_str in self.fixed_holidays and check_date.weekday() >= 5:
                    return True  # Holiday observed on Monday
        
        return False
    
    def _get_easter_dates(self, year: int) -> Set[date]:
        """
        Get Easter-related holiday dates for a given year.
        
        Args:
            year: Year to calculate Easter dates for
            
        Returns:
            Set of Easter-related holiday dates
        """
        # Simplified Easter calculation (you'd want to use a proper library)
        # This is just a placeholder - actual Easter calculation is complex
        
        # For demonstration, we'll use approximate dates
        # In practice, you'd use a library like dateutil or calculate properly
        easter_dates = set()
        
        # These are approximate and would need proper calculation
        if year == 2024:
            easter_sunday = date(2024, 3, 31)
        elif year == 2025:
            easter_sunday = date(2025, 4, 20)
        else:
            # Fallback approximation (not accurate)
            easter_sunday = date(year, 4, 15)  # Very rough approximation
        
        # Add Good Friday (2 days before Easter Sunday)
        good_friday = easter_sunday - timedelta(days=2)
        easter_dates.add(good_friday)
        
        # Add Easter Monday (1 day after Easter Sunday)
        easter_monday = easter_sunday + timedelta(days=1)
        easter_dates.add(easter_monday)
        
        return easter_dates
    
    def get_trading_days(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[datetime]:
        """
        Get list of trading days between two dates.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of trading day dates
        """
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_trading_day(current_date):
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def get_business_days_count(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> int:
        """
        Count business days between two dates.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Number of business days
        """
        return len(self.get_trading_days(start_date, end_date))
    
    def add_business_days(
        self, 
        start_date: datetime, 
        days_to_add: int
    ) -> datetime:
        """
        Add business days to a date.
        
        Args:
            start_date: Starting date
            days_to_add: Number of business days to add
            
        Returns:
            Date after adding business days
        """
        current_date = start_date
        days_added = 0
        
        while days_added < days_to_add:
            current_date += timedelta(days=1)
            if self.is_trading_day(current_date):
                days_added += 1
        
        return current_date
    
    def get_next_trading_day(self, date_to_check: datetime) -> datetime:
        """
        Get the next trading day after a given date.
        
        Args:
            date_to_check: Date to start from
            
        Returns:
            Next trading day
        """
        next_day = date_to_check + timedelta(days=1)
        
        while not self.is_trading_day(next_day):
            next_day += timedelta(days=1)
        
        return next_day
    
    def get_previous_trading_day(self, date_to_check: datetime) -> datetime:
        """
        Get the previous trading day before a given date.
        
        Args:
            date_to_check: Date to start from
            
        Returns:
            Previous trading day
        """
        prev_day = date_to_check - timedelta(days=1)
        
        while not self.is_trading_day(prev_day):
            prev_day -= timedelta(days=1)
        
        return prev_day
    
    def is_market_open(self, check_datetime: Optional[datetime] = None) -> bool:
        """
        Check if NSE market is currently open.
        
        Args:
            check_datetime: Datetime to check (defaults to now)
            
        Returns:
            True if market is open, False otherwise
        """
        if check_datetime is None:
            check_datetime = datetime.now()
        
        # Check if it's a trading day
        if not self.is_trading_day(check_datetime):
            return False
        
        # Check if within trading hours
        current_time = check_datetime.time()
        start_time = datetime.strptime(self.trading_start_time, "%H:%M").time()
        end_time = datetime.strptime(self.trading_end_time, "%H:%M").time()
        
        return start_time <= current_time <= end_time
    
    def get_market_hours(self) -> dict:
        """
        Get NSE market trading hours.
        
        Returns:
            Dictionary with market hours information
        """
        return {
            "start_time": self.trading_start_time,
            "end_time": self.trading_end_time,
            "timezone": self.timezone,
            "trading_days": "Monday-Friday",
            "total_hours": 6.0  # 9 AM to 3 PM = 6 hours
        }
    
    def get_options_expiry_dates(self, year: int) -> List[datetime]:
        """
        Get quarterly options expiry dates for NSE.
        
        Options typically expire on the last Friday of March, June, September, December.
        
        Args:
            year: Year to get expiry dates for
            
        Returns:
            List of expiry dates
        """
        expiry_dates = []
        
        # Quarterly months
        for month in [3, 6, 9, 12]:  # March, June, September, December
            # Find last Friday of the month
            last_day = date(year, month, 1)
            
            # Get last day of month
            if month == 12:
                last_day = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(year, month + 1, 1) - timedelta(days=1)
            
            # Find last Friday
            while last_day.weekday() != 4:  # Friday = 4
                last_day -= timedelta(days=1)
            
            # Convert to datetime and add to list
            expiry_dates.append(datetime.combine(last_day, datetime.min.time()))
        
        return expiry_dates
    
    def get_trading_calendar_dataframe(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Get a DataFrame with trading calendar information.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with calendar information
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        calendar_data = []
        
        for date in dates:
            calendar_data.append({
                'date': date,
                'is_trading_day': self.is_trading_day(date),
                'is_weekend': date.weekday() >= 5,
                'is_holiday': self.is_holiday(date),
                'day_of_week': date.strftime('%A'),
                'month': date.month,
                'quarter': f"Q{(date.month-1)//3 + 1}"
            })
        
        return pd.DataFrame(calendar_data)
    
    def get_time_to_expiry(
        self, 
        current_date: datetime, 
        expiry_date: datetime,
        method: str = 'calendar'
    ) -> float:
        """
        Calculate time to expiry in years.
        
        Args:
            current_date: Current date
            expiry_date: Expiry date
            method: 'calendar' for calendar days, 'business' for business days
            
        Returns:
            Time to expiry in years
        """
        if method == 'calendar':
            days_diff = (expiry_date - current_date).days
            return days_diff / 365.25
        
        elif method == 'business':
            business_days = self.get_business_days_count(current_date, expiry_date)
            return business_days / 252  # 252 trading days per year
        
        else:
            raise ValueError("Method must be 'calendar' or 'business'")
    
    def adjust_for_holidays(self, date_list: List[datetime]) -> List[datetime]:
        """
        Adjust a list of dates to ensure they fall on trading days.
        
        Args:
            date_list: List of dates to adjust
            
        Returns:
            List of adjusted dates (moved to next trading day if needed)
        """
        adjusted_dates = []
        
        for date in date_list:
            if self.is_trading_day(date):
                adjusted_dates.append(date)
            else:
                # Move to next trading day
                adjusted_dates.append(self.get_next_trading_day(date))
        
        return adjusted_dates


# Global calendar instance
nse_calendar = NSECalendar()


# Convenience functions
def is_nse_trading_day(date_to_check: datetime) -> bool:
    """Check if a date is an NSE trading day."""
    return nse_calendar.is_trading_day(date_to_check)


def get_nse_trading_days(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Get NSE trading days between two dates."""
    return nse_calendar.get_trading_days(start_date, end_date)


def is_nse_market_open(check_datetime: Optional[datetime] = None) -> bool:
    """Check if NSE market is currently open."""
    return nse_calendar.is_market_open(check_datetime)


def get_next_nse_expiry(current_date: datetime) -> datetime:
    """Get the next quarterly options expiry date."""
    year = current_date.year
    expiry_dates = nse_calendar.get_options_expiry_dates(year)
    
    # Find next expiry
    for expiry in expiry_dates:
        if expiry > current_date:
            return expiry
    
    # If no expiry found this year, get first expiry of next year
    next_year_expiries = nse_calendar.get_options_expiry_dates(year + 1)
    return next_year_expiries[0]