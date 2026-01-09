"""
Pydantic models for PnL API validation.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class StrategyLeg(BaseModel):
    """Model for a single option leg in a strategy."""
    option_type: str = Field(..., description="Option type: call or put")
    strike: float = Field(..., gt=0, description="Strike price")
    premium: float = Field(..., ge=0, description="Option premium")
    quantity: int = Field(default=1, ge=1, description="Number of contracts")
    position_type: str = Field(default='long', description="Position type: long or short")


class StrategyConfig(BaseModel):
    """Model for strategy configuration."""
    legs: List[StrategyLeg] = Field(..., min_length=1, description="List of strategy legs")


class MarketParams(BaseModel):
    """Model for market parameters."""
    current_price: float = Field(..., gt=0, description="Current asset price")
    price_range_pct: float = Field(default=50, gt=0, le=100, description="Price range percentage")
    time_to_expiry: float = Field(default=0.0822, gt=0, le=1.0, description="Time to expiry in years")


class AnalyzeRequest(BaseModel):
    """Request model for analyzing custom strategy."""
    strategy: StrategyConfig
    market_params: MarketParams


class StrategyBuilderRequest(BaseModel):
    """Request model for building pre-defined strategy."""
    strategy_name: str = Field(..., description="Name of the strategy")
    parameters: Dict = Field(..., description="Strategy parameters")
