"""
Pydantic models for pricing API validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class PricingRequest(BaseModel):
    """Request model for option pricing calculation."""
    futures_price: float = Field(..., gt=0, description="Current futures price")
    strike_price: float = Field(..., gt=0, description="Strike price")
    days_to_expiry: int = Field(..., gt=0, le=365, description="Days to expiration")
    volatility: float = Field(..., gt=0, le=2.0, description="Implied volatility (0-2)")
    risk_free_rate: float = Field(..., ge=0, le=1.0, description="Risk-free rate (0-1)")
    option_type: str = Field(default='call', description="Option type: call or put")
    contract_symbol: Optional[str] = Field(None, description="Contract symbol")
    include_fees: bool = Field(default=False, description="Include NSE fees")

    @field_validator('option_type')
    @classmethod
    def validate_option_type(cls, v):
        if v.lower() not in ['call', 'put']:
            raise ValueError('option_type must be "call" or "put"')
        return v.lower()


class HeatmapRequest(BaseModel):
    """Request model for heatmap generation."""
    futures_price: float = Field(..., gt=0)
    strike_price: float = Field(..., gt=0)
    days_to_expiry: int = Field(..., gt=0, le=365)
    volatility: float = Field(..., gt=0, le=2.0)
    risk_free_rate: float = Field(..., ge=0, le=1.0)
    price_range_pct: float = Field(default=20.0, gt=0, le=100)
    vol_range_pct: float = Field(default=50.0, gt=0, le=100)
    grid_size: int = Field(default=12, ge=5, le=30)
