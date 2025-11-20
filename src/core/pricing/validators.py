"""
Input Validation for Options Pricing

This module provides comprehensive validation for all inputs to the pricing engine,
ensuring data quality and preventing calculation errors.
"""

import numpy as np
from typing import Union, Optional


class PricingError(Exception):
    """Custom exception for pricing-related errors."""
    pass


def validate_positive_number(value: float, name: str, min_value: float = 0.0) -> None:
    """
    Validate that a number is positive and finite.
    
    Args:
        value: Number to validate
        name: Name of the parameter for error messages
        min_value: Minimum allowed value (exclusive)
        
    Raises:
        PricingError: If validation fails
    """
    if not isinstance(value, (int, float)):
        raise PricingError(f"{name} must be a number, got {type(value)}")
    
    if not np.isfinite(value):
        raise PricingError(f"{name} must be finite (not NaN or infinity)")
    
    if value <= min_value:
        raise PricingError(f"{name} must be greater than {min_value}, got {value}")


def validate_percentage(value: float, name: str, min_val: float = -1.0, max_val: float = 10.0) -> None:
    """
    Validate a percentage value (like volatility or interest rate).
    
    Args:
        value: Percentage value in decimal form (e.g., 0.20 for 20%)
        name: Name of the parameter
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Raises:
        PricingError: If validation fails
    """
    if not isinstance(value, (int, float)):
        raise PricingError(f"{name} must be a number, got {type(value)}")
    
    if not np.isfinite(value):
        raise PricingError(f"{name} must be finite")
    
    if value < min_val or value > max_val:
        raise PricingError(
            f"{name} must be between {min_val:.1%} and {max_val:.1%}, got {value:.1%}"
        )


def validate_time_to_expiry(time_to_expiry: float) -> None:
    """
    Validate time to expiry parameter.
    
    Args:
        time_to_expiry: Time to expiration in years
        
    Raises:
        PricingError: If validation fails
    """
    validate_positive_number(time_to_expiry, "time_to_expiry")
    
    if time_to_expiry > 5.0:
        raise PricingError(
            f"Time to expiry too long: {time_to_expiry:.2f} years. "
            f"Maximum supported is 5.0 years"
        )
    
    if time_to_expiry < 1/365.25:  # Less than 1 day
        raise PricingError(
            f"Time to expiry too short: {time_to_expiry:.6f} years. "
            f"Minimum is 1 day (0.0027 years)"
        )


def validate_volatility(volatility: float) -> None:
    """
    Validate volatility parameter.
    
    Args:
        volatility: Annual volatility in decimal form
        
    Raises:
        PricingError: If validation fails
    """
    validate_percentage(volatility, "volatility", min_val=0.001, max_val=5.0)
    
    # Additional business logic checks
    if volatility > 2.0:
        import warnings
        warnings.warn(
            f"Very high volatility: {volatility:.1%}. "
            f"Please verify this is correct.",
            UserWarning
        )


def validate_risk_free_rate(risk_free_rate: float) -> None:
    """
    Validate risk-free rate parameter.
    
    Args:
        risk_free_rate: Annual risk-free rate in decimal form
        
    Raises:
        PricingError: If validation fails
    """
    validate_percentage(risk_free_rate, "risk_free_rate", min_val=-0.1, max_val=1.0)
    
    # Kenya-specific checks
    if risk_free_rate < 0:
        import warnings
        warnings.warn(
            f"Negative interest rate: {risk_free_rate:.1%}. "
            f"This is unusual for Kenyan markets.",
            UserWarning
        )


def validate_price_relationship(futures_price: float, strike_price: float) -> None:
    """
    Validate the relationship between futures and strike prices.
    
    Args:
        futures_price: Current futures price
        strike_price: Strike price
        
    Raises:
        PricingError: If validation fails
    """
    price_ratio = futures_price / strike_price
    
    if price_ratio > 10.0:
        raise PricingError(
            f"Futures price ({futures_price:.2f}) is more than 10x strike price "
            f"({strike_price:.2f}). Please verify inputs."
        )
    
    if price_ratio < 0.1:
        raise PricingError(
            f"Futures price ({futures_price:.2f}) is less than 10% of strike price "
            f"({strike_price:.2f}). Please verify inputs."
        )


def validate_option_type(option_type: str) -> str:
    """
    Validate and normalize option type.
    
    Args:
        option_type: Option type string
        
    Returns:
        Normalized option type ('call' or 'put')
        
    Raises:
        PricingError: If option type is invalid
    """
    if not isinstance(option_type, str):
        raise PricingError(f"Option type must be a string, got {type(option_type)}")
    
    option_type = option_type.lower().strip()
    
    if option_type not in ['call', 'put']:
        raise PricingError(
            f"Invalid option type: '{option_type}'. Must be 'call' or 'put'"
        )
    
    return option_type


def validate_pricing_inputs(
    futures_price: float,
    strike_price: float,
    time_to_expiry: float,
    volatility: float,
    risk_free_rate: float,
    option_type: Optional[str] = None
) -> None:
    """
    Comprehensive validation of all pricing inputs.
    
    Args:
        futures_price: Current futures price
        strike_price: Strike price
        time_to_expiry: Time to expiration in years
        volatility: Annual volatility
        risk_free_rate: Annual risk-free rate
        option_type: Optional option type for additional validation
        
    Raises:
        PricingError: If any validation fails
    """
    # Individual parameter validation
    validate_positive_number(futures_price, "futures_price")
    validate_positive_number(strike_price, "strike_price") 
    validate_time_to_expiry(time_to_expiry)
    validate_volatility(volatility)
    validate_risk_free_rate(risk_free_rate)
    
    # Cross-parameter validation
    validate_price_relationship(futures_price, strike_price)
    
    # Option type validation if provided
    if option_type is not None:
        validate_option_type(option_type)


def validate_nse_contract_symbol(symbol: Optional[str]) -> Optional[str]:
    """
    Validate NSE contract symbol.
    
    Args:
        symbol: Contract symbol or None
        
    Returns:
        Validated and normalized symbol or None
        
    Raises:
        PricingError: If symbol is invalid
    """
    if symbol is None:
        return None
    
    if not isinstance(symbol, str):
        raise PricingError(f"Contract symbol must be a string, got {type(symbol)}")
    
    symbol = symbol.upper().strip()
    
    # Valid NSE symbols
    valid_symbols = {
        'SCOM': 'Safaricom',
        'KCB': 'KCB Group', 
        'EQTY': 'Equity Group',
        'ABSA': 'ABSA Bank',
        'NSE25': 'NSE 25 Index',
        'MNSE25': 'Mini NSE 25'
    }
    
    if symbol not in valid_symbols:
        raise PricingError(
            f"Invalid NSE contract symbol: '{symbol}'. "
            f"Valid symbols: {list(valid_symbols.keys())}"
        )
    
    return symbol


def validate_batch_inputs(contracts_data: list) -> None:
    """
    Validate a batch of contract data for batch pricing.
    
    Args:
        contracts_data: List of contract parameter dictionaries
        
    Raises:
        PricingError: If validation fails
    """
    if not isinstance(contracts_data, list):
        raise PricingError("Contracts data must be a list")
    
    if len(contracts_data) == 0:
        raise PricingError("Contracts data cannot be empty")
    
    if len(contracts_data) > 1000:
        raise PricingError(
            f"Too many contracts in batch: {len(contracts_data)}. "
            f"Maximum is 1000 for performance reasons."
        )
    
    required_keys = {'F', 'K', 'T', 'vol', 'r', 'type'}
    
    for i, contract in enumerate(contracts_data):
        if not isinstance(contract, dict):
            raise PricingError(f"Contract {i} must be a dictionary")
        
        missing_keys = required_keys - set(contract.keys())
        if missing_keys:
            raise PricingError(
                f"Contract {i} missing required keys: {missing_keys}"
            )
        
        # Validate individual contract
        try:
            validate_pricing_inputs(
                contract['F'], contract['K'], contract['T'],
                contract['vol'], contract['r'], contract['type']
            )
        except PricingError as e:
            raise PricingError(f"Contract {i} validation failed: {e}")


# Utility functions for common validation patterns
def is_valid_price(price: float) -> bool:
    """Check if a price value is valid."""
    try:
        validate_positive_number(price, "price")
        return True
    except PricingError:
        return False


def is_valid_volatility(vol: float) -> bool:
    """Check if a volatility value is valid."""
    try:
        validate_volatility(vol)
        return True
    except PricingError:
        return False


def is_valid_rate(rate: float) -> bool:
    """Check if an interest rate is valid."""
    try:
        validate_risk_free_rate(rate)
        return True
    except PricingError:
        return False