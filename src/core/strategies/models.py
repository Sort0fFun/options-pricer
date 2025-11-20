"""
Strategy Builder Data Models

This module defines the core data structures for multi-leg option strategies,
including position management, P&L calculations, and risk metrics.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import numpy as np
from datetime import datetime, date


class PositionType(Enum):
    """Position type enumeration."""
    LONG = "long"
    SHORT = "short"


class OptionType(Enum):
    """Option type enumeration."""
    CALL = "call"
    PUT = "put"


@dataclass
class OptionLeg:
    """
    Represents a single option leg in a multi-leg strategy.
    
    Attributes:
        contract_symbol: NSE contract symbol (e.g., 'SCOM', 'KCB')
        option_type: 'call' or 'put'
        position_type: 'long' or 'short'
        strike_price: Strike price of the option
        quantity: Number of contracts
        expiry_date: Expiration date
        entry_price: Price at which position was entered (optional)
        multiplier: Contract multiplier (default 100)
    """
    contract_symbol: str
    option_type: OptionType
    position_type: PositionType
    strike_price: float
    quantity: int
    expiry_date: date
    entry_price: Optional[float] = None
    multiplier: int = 100
    
    def __post_init__(self):
        """Validate leg parameters after initialization."""
        if self.strike_price <= 0:
            raise ValueError("Strike price must be positive")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.multiplier <= 0:
            raise ValueError("Multiplier must be positive")


@dataclass
class GreeksResult:
    """Greeks calculation result for a single leg or strategy."""
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    lambda_: float = 0.0  # leverage ratio
    
    def __add__(self, other: 'GreeksResult') -> 'GreeksResult':
        """Add two Greeks results together."""
        return GreeksResult(
            delta=self.delta + other.delta,
            gamma=self.gamma + other.gamma,
            vega=self.vega + other.vega,
            theta=self.theta + other.theta,
            rho=self.rho + other.rho,
            lambda_=self.lambda_ + other.lambda_
        )
    
    def __mul__(self, scalar: float) -> 'GreeksResult':
        """Multiply Greeks by a scalar (for quantity)."""
        return GreeksResult(
            delta=self.delta * scalar,
            gamma=self.gamma * scalar,
            vega=self.vega * scalar,
            theta=self.theta * scalar,
            rho=self.rho * scalar,
            lambda_=self.lambda_ * scalar
        )


@dataclass
class PnLResult:
    """P&L calculation result."""
    option_price: float
    intrinsic_value: float
    time_value: float
    net_premium: float  # Positive = credit received, Negative = debit paid
    pnl: float  # Current P&L based on current option price vs entry price
    
    def __add__(self, other: 'PnLResult') -> 'PnLResult':
        """Add two P&L results together."""
        return PnLResult(
            option_price=self.option_price + other.option_price,
            intrinsic_value=self.intrinsic_value + other.intrinsic_value,
            time_value=self.time_value + other.time_value,
            net_premium=self.net_premium + other.net_premium,
            pnl=self.pnl + other.pnl
        )


@dataclass
class StrategyAnalysis:
    """Comprehensive strategy analysis results."""
    total_cost: float  # Net debit/credit (negative = debit, positive = credit)
    max_profit: float
    max_loss: float
    breakeven_points: List[float]
    risk_reward_ratio: float
    probability_of_profit: float
    days_to_expiry: int
    strategy_greeks: GreeksResult
    
    # Additional risk metrics
    margin_requirement: Optional[float] = None
    buying_power_reduction: Optional[float] = None
    maximum_risk_percentage: Optional[float] = None


@dataclass
class StrategyPosition:
    """
    Represents a complete multi-leg option strategy.
    
    This is the main class that holds all legs of a strategy and provides
    methods for calculating P&L, Greeks, and risk metrics.
    """
    name: str
    legs: List[OptionLeg] = field(default_factory=list)
    description: str = ""
    market_outlook: str = ""  # bullish, bearish, neutral, volatile
    created_date: datetime = field(default_factory=datetime.now)
    
    def add_leg(self, leg: OptionLeg) -> None:
        """Add a leg to the strategy."""
        self.legs.append(leg)
    
    def remove_leg(self, index: int) -> None:
        """Remove a leg from the strategy."""
        if 0 <= index < len(self.legs):
            self.legs.pop(index)
    
    def get_unique_contracts(self) -> List[str]:
        """Get list of unique contract symbols in the strategy."""
        return list(set(leg.contract_symbol for leg in self.legs))
    
    def get_unique_expiries(self) -> List[date]:
        """Get list of unique expiry dates in the strategy."""
        return list(set(leg.expiry_date for leg in self.legs))
    
    def is_single_expiry(self) -> bool:
        """Check if all legs have the same expiry date."""
        return len(self.get_unique_expiries()) == 1
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the strategy for consistency and completeness.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if not self.legs:
            errors.append("Strategy must have at least one leg")
        
        if not self.name.strip():
            errors.append("Strategy must have a name")
        
        # Check for duplicate legs (same contract, type, strike, expiry)
        leg_signatures = []
        for leg in self.legs:
            signature = (
                leg.contract_symbol,
                leg.option_type,
                leg.strike_price,
                leg.expiry_date
            )
            if signature in leg_signatures:
                errors.append(f"Duplicate leg detected: {leg.contract_symbol} {leg.option_type.value} {leg.strike_price}")
            leg_signatures.append(signature)
        
        # Warn about complex multi-expiry strategies
        if len(self.get_unique_expiries()) > 2:
            errors.append("Warning: Strategy has more than 2 expiry dates - complexity may affect accuracy")
        
        return len(errors) == 0, errors
    
    def get_total_quantity(self) -> int:
        """Get total number of contracts in the strategy."""
        return sum(leg.quantity for leg in self.legs)
    
    def get_net_delta_exposure(self) -> str:
        """Get a description of the strategy's directional exposure."""
        # This would be calculated with actual Greeks in implementation
        call_legs = sum(1 for leg in self.legs if leg.option_type == OptionType.CALL)
        put_legs = sum(1 for leg in self.legs if leg.option_type == OptionType.PUT)
        
        if call_legs > put_legs:
            return "Bullish bias (more calls)"
        elif put_legs > call_legs:
            return "Bearish bias (more puts)"
        else:
            return "Neutral (balanced calls/puts)"


# Pre-defined strategy templates
STRATEGY_TEMPLATES = {
    "Long Straddle": {
        "description": "Buy call and put at same strike - profits from large moves in either direction",
        "market_outlook": "High volatility expected",
        "legs": [
            {"option_type": "call", "position_type": "long", "strike_offset": 0},
            {"option_type": "put", "position_type": "long", "strike_offset": 0}
        ],
        "risk_level": "Medium",
        "max_profit": "Unlimited",
        "max_loss": "Net premium paid"
    },
    
    "Short Straddle": {
        "description": "Sell call and put at same strike - profits from low volatility",
        "market_outlook": "Low volatility expected",
        "legs": [
            {"option_type": "call", "position_type": "short", "strike_offset": 0},
            {"option_type": "put", "position_type": "short", "strike_offset": 0}
        ],
        "risk_level": "High",
        "max_profit": "Net premium received",
        "max_loss": "Unlimited"
    },
    
    "Long Strangle": {
        "description": "Buy out-of-money call and put - cheaper than straddle",
        "market_outlook": "High volatility expected, wider range",
        "legs": [
            {"option_type": "call", "position_type": "long", "strike_offset": 5},
            {"option_type": "put", "position_type": "long", "strike_offset": -5}
        ],
        "risk_level": "Medium",
        "max_profit": "Unlimited",
        "max_loss": "Net premium paid"
    },
    
    "Bull Call Spread": {
        "description": "Buy lower strike call, sell higher strike call - moderately bullish",
        "market_outlook": "Moderately bullish",
        "legs": [
            {"option_type": "call", "position_type": "long", "strike_offset": -2},
            {"option_type": "call", "position_type": "short", "strike_offset": 3}
        ],
        "risk_level": "Low",
        "max_profit": "Strike difference - net premium",
        "max_loss": "Net premium paid"
    },
    
    "Bear Put Spread": {
        "description": "Buy higher strike put, sell lower strike put - moderately bearish",
        "market_outlook": "Moderately bearish",
        "legs": [
            {"option_type": "put", "position_type": "long", "strike_offset": 2},
            {"option_type": "put", "position_type": "short", "strike_offset": -3}
        ],
        "risk_level": "Low",
        "max_profit": "Strike difference - net premium",
        "max_loss": "Net premium paid"
    },
    
    "Iron Condor": {
        "description": "Sell strangle, buy wider strangle - profits from range-bound movement",
        "market_outlook": "Low volatility, range-bound",
        "legs": [
            {"option_type": "put", "position_type": "long", "strike_offset": -10},
            {"option_type": "put", "position_type": "short", "strike_offset": -5},
            {"option_type": "call", "position_type": "short", "strike_offset": 5},
            {"option_type": "call", "position_type": "long", "strike_offset": 10}
        ],
        "risk_level": "Medium",
        "max_profit": "Net premium received",
        "max_loss": "Wing width - net premium"
    },
    
    "Protective Put": {
        "description": "Own stock + buy put - insurance against downside",
        "market_outlook": "Bullish with downside protection",
        "legs": [
            {"option_type": "put", "position_type": "long", "strike_offset": -5}
        ],
        "risk_level": "Low",
        "max_profit": "Unlimited (minus put premium)",
        "max_loss": "Strike price - stock price + put premium"
    },
    
    "Covered Call": {
        "description": "Own stock + sell call - generate income with upside cap",
        "market_outlook": "Neutral to moderately bullish",
        "legs": [
            {"option_type": "call", "position_type": "short", "strike_offset": 5}
        ],
        "risk_level": "Low",
        "max_profit": "Strike price - stock price + call premium",
        "max_loss": "Stock price - call premium"
    }
}