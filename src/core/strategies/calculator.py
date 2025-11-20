"""
Strategy Calculator

This module provides comprehensive calculation capabilities for multi-leg option strategies,
including P&L analysis, Greeks aggregation, payoff diagrams, and risk metrics.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import date, datetime
import logging

from .models import (
    StrategyPosition, OptionLeg, GreeksResult, PnLResult, StrategyAnalysis,
    PositionType, OptionType
)

try:
    from ..pricing.black76 import Black76Pricer
    from ..greeks.calculator import GreeksCalculator
    PRICING_AVAILABLE = True
except ImportError:
    PRICING_AVAILABLE = False
    
logger = logging.getLogger(__name__)


class StrategyCalculator:
    """
    Main calculator for option strategy analysis.
    
    Provides methods to calculate P&L, Greeks, breakeven points, and comprehensive
    risk metrics for multi-leg option strategies.
    """
    
    def __init__(self, pricer=None, greeks_calc=None):
        """
        Initialize strategy calculator.
        
        Args:
            pricer: Black76Pricer instance (optional)
            greeks_calc: GreeksCalculator instance (optional)
        """
        self.pricer = pricer
        self.greeks_calc = greeks_calc
        
        if PRICING_AVAILABLE and not pricer:
            try:
                self.pricer = Black76Pricer()
            except Exception as e:
                logger.warning(f"Could not initialize Black76Pricer: {e}")
        
        if PRICING_AVAILABLE and not greeks_calc:
            try:
                self.greeks_calc = GreeksCalculator()
            except Exception as e:
                logger.warning(f"Could not initialize GreeksCalculator: {e}")
    
    def calculate_leg_pnl(
        self,
        leg: OptionLeg,
        futures_price: float,
        volatility: float,
        risk_free_rate: float,
        current_date: Optional[date] = None
    ) -> PnLResult:
        """
        Calculate P&L for a single option leg.
        
        Args:
            leg: Option leg to calculate
            futures_price: Current futures price
            volatility: Implied volatility
            risk_free_rate: Risk-free rate
            current_date: Current date for time calculation
            
        Returns:
            PnLResult with current option value and P&L
        """
        if not self.pricer:
            # Fallback calculation using simplified Black-Scholes approximation
            return self._calculate_leg_pnl_fallback(leg, futures_price, volatility, risk_free_rate)
        
        try:
            # Calculate time to expiry
            if current_date is None:
                current_date = date.today()
            
            days_to_expiry = (leg.expiry_date - current_date).days
            time_to_expiry = max(days_to_expiry / 365.0, 0.001)  # Minimum 1 day
            
            # Calculate current option price
            if leg.option_type == OptionType.CALL:
                option_price = self.pricer.price_call(
                    futures_price=futures_price,
                    strike_price=leg.strike_price,
                    time_to_expiry=time_to_expiry,
                    volatility=volatility,
                    risk_free_rate=risk_free_rate
                )
            else:  # PUT
                option_price = self.pricer.price_put(
                    futures_price=futures_price,
                    strike_price=leg.strike_price,
                    time_to_expiry=time_to_expiry,
                    volatility=volatility,
                    risk_free_rate=risk_free_rate
                )
            
            # Calculate intrinsic value
            if leg.option_type == OptionType.CALL:
                intrinsic_value = max(0, futures_price - leg.strike_price)
            else:  # PUT
                intrinsic_value = max(0, leg.strike_price - futures_price)
            
            # Time value
            time_value = option_price - intrinsic_value
            
            # Net premium calculation
            if leg.position_type == PositionType.LONG:
                net_premium = -option_price * leg.quantity * leg.multiplier  # Debit
                if leg.entry_price:
                    pnl = (option_price - leg.entry_price) * leg.quantity * leg.multiplier
                else:
                    pnl = 0.0
            else:  # SHORT
                net_premium = option_price * leg.quantity * leg.multiplier  # Credit
                if leg.entry_price:
                    pnl = (leg.entry_price - option_price) * leg.quantity * leg.multiplier
                else:
                    pnl = 0.0
            
            return PnLResult(
                option_price=option_price,
                intrinsic_value=intrinsic_value,
                time_value=time_value,
                net_premium=net_premium,
                pnl=pnl
            )
            
        except Exception as e:
            logger.error(f"Error calculating leg P&L: {e}")
            return self._calculate_leg_pnl_fallback(leg, futures_price, volatility, risk_free_rate)
    
    def _calculate_leg_pnl_fallback(
        self,
        leg: OptionLeg,
        futures_price: float,
        volatility: float,
        risk_free_rate: float
    ) -> PnLResult:
        """Fallback P&L calculation using simplified formulas."""
        # Simple intrinsic value calculation
        if leg.option_type == OptionType.CALL:
            intrinsic_value = max(0, futures_price - leg.strike_price)
        else:
            intrinsic_value = max(0, leg.strike_price - futures_price)
        
        # Rough time value estimation
        time_value = max(0, leg.strike_price * volatility * 0.1)  # Simplified
        option_price = intrinsic_value + time_value
        
        # Net premium
        if leg.position_type == PositionType.LONG:
            net_premium = -option_price * leg.quantity * leg.multiplier
            pnl = 0.0  # Can't calculate without entry price
        else:
            net_premium = option_price * leg.quantity * leg.multiplier
            pnl = 0.0
        
        return PnLResult(
            option_price=option_price,
            intrinsic_value=intrinsic_value,
            time_value=time_value,
            net_premium=net_premium,
            pnl=pnl
        )
    
    def calculate_leg_greeks(
        self,
        leg: OptionLeg,
        futures_price: float,
        volatility: float,
        risk_free_rate: float,
        current_date: Optional[date] = None
    ) -> GreeksResult:
        """Calculate Greeks for a single option leg."""
        if not self.greeks_calc:
            return self._calculate_leg_greeks_fallback(leg, futures_price)
        
        try:
            # Calculate time to expiry
            if current_date is None:
                current_date = date.today()
            
            days_to_expiry = (leg.expiry_date - current_date).days
            time_to_expiry = max(days_to_expiry / 365.0, 0.001)
            
            # Calculate Greeks
            greeks = self.greeks_calc.calculate_greeks(
                futures_price=futures_price,
                strike_price=leg.strike_price,
                time_to_expiry=time_to_expiry,
                volatility=volatility,
                risk_free_rate=risk_free_rate,
                option_type=leg.option_type.value
            )
            
            # Adjust for position type and quantity
            multiplier = leg.quantity * leg.multiplier
            if leg.position_type == PositionType.SHORT:
                multiplier *= -1
            
            return GreeksResult(
                delta=greeks.delta * multiplier,
                gamma=greeks.gamma * multiplier,
                vega=greeks.vega * multiplier,
                theta=greeks.theta * multiplier,
                rho=greeks.rho * multiplier,
                lambda_=greeks.lambda_ * multiplier
            )
            
        except Exception as e:
            logger.error(f"Error calculating leg Greeks: {e}")
            return self._calculate_leg_greeks_fallback(leg, futures_price)
    
    def _calculate_leg_greeks_fallback(self, leg: OptionLeg, futures_price: float) -> GreeksResult:
        """Fallback Greeks calculation with simplified approximations."""
        # Simplified delta approximation
        if leg.option_type == OptionType.CALL:
            delta = 0.5 if futures_price >= leg.strike_price else 0.2
        else:
            delta = -0.5 if futures_price <= leg.strike_price else -0.2
        
        # Simplified other Greeks
        gamma = 0.01
        vega = leg.strike_price * 0.001
        theta = -0.1
        rho = leg.strike_price * 0.0001
        
        # Adjust for position
        multiplier = leg.quantity * leg.multiplier
        if leg.position_type == PositionType.SHORT:
            multiplier *= -1
        
        return GreeksResult(
            delta=delta * multiplier,
            gamma=gamma * multiplier,
            vega=vega * multiplier,
            theta=theta * multiplier,
            rho=rho * multiplier,
            lambda_=0.0
        )
    
    def calculate_strategy_pnl(
        self,
        strategy: StrategyPosition,
        futures_price: float,
        volatility: float,
        risk_free_rate: float,
        current_date: Optional[date] = None
    ) -> PnLResult:
        """Calculate total P&L for the entire strategy."""
        total_pnl = PnLResult(0, 0, 0, 0, 0)
        
        for leg in strategy.legs:
            leg_pnl = self.calculate_leg_pnl(
                leg, futures_price, volatility, risk_free_rate, current_date
            )
            total_pnl = total_pnl + leg_pnl
        
        return total_pnl
    
    def calculate_strategy_greeks(
        self,
        strategy: StrategyPosition,
        futures_price: float,
        volatility: float,
        risk_free_rate: float,
        current_date: Optional[date] = None
    ) -> GreeksResult:
        """Calculate aggregated Greeks for the entire strategy."""
        total_greeks = GreeksResult(0, 0, 0, 0, 0, 0)
        
        for leg in strategy.legs:
            leg_greeks = self.calculate_leg_greeks(
                leg, futures_price, volatility, risk_free_rate, current_date
            )
            total_greeks = total_greeks + leg_greeks
        
        return total_greeks
    
    def calculate_payoff_diagram(
        self,
        strategy: StrategyPosition,
        price_range: Optional[Tuple[float, float]] = None,
        num_points: int = 100,
        volatility: float = 0.2,
        risk_free_rate: float = 0.05
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate payoff diagram for the strategy.
        
        Args:
            strategy: Strategy to analyze
            price_range: (min_price, max_price) or None for auto-range
            num_points: Number of points to calculate
            volatility: Volatility for option pricing
            risk_free_rate: Risk-free rate
            
        Returns:
            (price_array, payoff_array) tuple
        """
        if not strategy.legs:
            return np.array([]), np.array([])
        
        # Auto-generate price range if not provided
        if price_range is None:
            strikes = [leg.strike_price for leg in strategy.legs]
            min_strike = min(strikes)
            max_strike = max(strikes)
            range_width = max_strike - min_strike
            
            if range_width == 0:  # All same strike
                range_width = min_strike * 0.4
            
            min_price = min_strike - range_width * 0.5
            max_price = max_strike + range_width * 0.5
        else:
            min_price, max_price = price_range
        
        # Generate price array
        prices = np.linspace(min_price, max_price, num_points)
        payoffs = np.zeros(num_points)
        
        # Calculate payoff at each price point
        for i, price in enumerate(prices):
            strategy_pnl = self.calculate_strategy_pnl(
                strategy, price, volatility, risk_free_rate
            )
            payoffs[i] = strategy_pnl.net_premium  # Net P&L at expiry
        
        return prices, payoffs
    
    def find_breakeven_points(
        self,
        strategy: StrategyPosition,
        volatility: float = 0.2,
        risk_free_rate: float = 0.05,
        tolerance: float = 0.01
    ) -> List[float]:
        """Find breakeven points where strategy P&L = 0."""
        if not strategy.legs:
            return []
        
        try:
            # Get payoff diagram
            prices, payoffs = self.calculate_payoff_diagram(
                strategy, volatility=volatility, risk_free_rate=risk_free_rate
            )
            
            if len(prices) == 0:
                return []
            
            # Find zero crossings
            breakevens = []
            for i in range(1, len(payoffs)):
                if (payoffs[i-1] <= 0 <= payoffs[i]) or (payoffs[i-1] >= 0 >= payoffs[i]):
                    # Linear interpolation to find more precise breakeven
                    if abs(payoffs[i] - payoffs[i-1]) > 1e-10:
                        ratio = -payoffs[i-1] / (payoffs[i] - payoffs[i-1])
                        breakeven = prices[i-1] + ratio * (prices[i] - prices[i-1])
                        breakevens.append(breakeven)
            
            # Remove duplicates and sort
            unique_breakevens = []
            for be in breakevens:
                if not any(abs(be - existing) < tolerance for existing in unique_breakevens):
                    unique_breakevens.append(be)
            
            return sorted(unique_breakevens)
            
        except Exception as e:
            logger.error(f"Error finding breakeven points: {e}")
            return []
    
    def analyze_strategy(
        self,
        strategy: StrategyPosition,
        current_futures_price: float,
        volatility: float = 0.2,
        risk_free_rate: float = 0.05,
        current_date: Optional[date] = None
    ) -> StrategyAnalysis:
        """
        Perform comprehensive analysis of the strategy.
        
        Returns detailed risk metrics, breakeven points, and Greeks.
        """
        if current_date is None:
            current_date = date.today()
        
        # Calculate current P&L and Greeks
        current_pnl = self.calculate_strategy_pnl(
            strategy, current_futures_price, volatility, risk_free_rate, current_date
        )
        
        strategy_greeks = self.calculate_strategy_greeks(
            strategy, current_futures_price, volatility, risk_free_rate, current_date
        )
        
        # Find breakeven points
        breakevens = self.find_breakeven_points(strategy, volatility, risk_free_rate)
        
        # Calculate max profit/loss using payoff diagram
        prices, payoffs = self.calculate_payoff_diagram(strategy, volatility=volatility)
        
        if len(payoffs) > 0:
            max_profit = float(np.max(payoffs))
            max_loss = float(np.min(payoffs))
            
            # Handle unlimited profit/loss
            if max_profit > 1e6:
                max_profit = float('inf')
            if max_loss < -1e6:
                max_loss = float('-inf')
        else:
            max_profit = 0.0
            max_loss = 0.0
        
        # Calculate risk/reward ratio
        if max_loss != 0 and not np.isinf(max_loss):
            risk_reward_ratio = abs(max_profit / max_loss) if not np.isinf(max_profit) else float('inf')
        else:
            risk_reward_ratio = float('inf')
        
        # Calculate days to expiry (using nearest expiry)
        expiry_dates = strategy.get_unique_expiries()
        if expiry_dates:
            nearest_expiry = min(expiry_dates)
            days_to_expiry = (nearest_expiry - current_date).days
        else:
            days_to_expiry = 0
        
        # Estimate probability of profit (simplified)
        if len(payoffs) > 0:
            profitable_points = np.sum(payoffs > 0)
            probability_of_profit = profitable_points / len(payoffs)
        else:
            probability_of_profit = 0.5
        
        return StrategyAnalysis(
            total_cost=current_pnl.net_premium,
            max_profit=max_profit,
            max_loss=max_loss,
            breakeven_points=breakevens,
            risk_reward_ratio=risk_reward_ratio,
            probability_of_profit=probability_of_profit,
            days_to_expiry=days_to_expiry,
            strategy_greeks=strategy_greeks
        )


class StrategyBuilder:
    """Helper class for building common option strategies."""
    
    @staticmethod
    def create_straddle(
        contract_symbol: str,
        strike_price: float,
        expiry_date: date,
        position_type: PositionType = PositionType.LONG,
        quantity: int = 1
    ) -> StrategyPosition:
        """Create a straddle strategy (buy/sell call and put at same strike)."""
        strategy = StrategyPosition(
            name=f"{'Long' if position_type == PositionType.LONG else 'Short'} Straddle",
            market_outlook="High volatility" if position_type == PositionType.LONG else "Low volatility"
        )
        
        # Add call leg
        call_leg = OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.CALL,
            position_type=position_type,
            strike_price=strike_price,
            quantity=quantity,
            expiry_date=expiry_date
        )
        strategy.add_leg(call_leg)
        
        # Add put leg
        put_leg = OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.PUT,
            position_type=position_type,
            strike_price=strike_price,
            quantity=quantity,
            expiry_date=expiry_date
        )
        strategy.add_leg(put_leg)
        
        return strategy
    
    @staticmethod
    def create_strangle(
        contract_symbol: str,
        call_strike: float,
        put_strike: float,
        expiry_date: date,
        position_type: PositionType = PositionType.LONG,
        quantity: int = 1
    ) -> StrategyPosition:
        """Create a strangle strategy (buy/sell OTM call and put)."""
        strategy = StrategyPosition(
            name=f"{'Long' if position_type == PositionType.LONG else 'Short'} Strangle",
            market_outlook="High volatility" if position_type == PositionType.LONG else "Low volatility"
        )
        
        # Add call leg (higher strike)
        call_leg = OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.CALL,
            position_type=position_type,
            strike_price=max(call_strike, put_strike),
            quantity=quantity,
            expiry_date=expiry_date
        )
        strategy.add_leg(call_leg)
        
        # Add put leg (lower strike)
        put_leg = OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.PUT,
            position_type=position_type,
            strike_price=min(call_strike, put_strike),
            quantity=quantity,
            expiry_date=expiry_date
        )
        strategy.add_leg(put_leg)
        
        return strategy
    
    @staticmethod
    def create_bull_call_spread(
        contract_symbol: str,
        lower_strike: float,
        higher_strike: float,
        expiry_date: date,
        quantity: int = 1
    ) -> StrategyPosition:
        """Create a bull call spread (buy lower strike call, sell higher strike call)."""
        strategy = StrategyPosition(
            name="Bull Call Spread",
            market_outlook="Moderately bullish"
        )
        
        # Buy lower strike call
        long_call = OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.CALL,
            position_type=PositionType.LONG,
            strike_price=lower_strike,
            quantity=quantity,
            expiry_date=expiry_date
        )
        strategy.add_leg(long_call)
        
        # Sell higher strike call
        short_call = OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.CALL,
            position_type=PositionType.SHORT,
            strike_price=higher_strike,
            quantity=quantity,
            expiry_date=expiry_date
        )
        strategy.add_leg(short_call)
        
        return strategy
    
    @staticmethod
    def create_bear_put_spread(
        contract_symbol: str,
        lower_strike: float,
        higher_strike: float,
        expiry_date: date,
        quantity: int = 1
    ) -> StrategyPosition:
        """Create a bear put spread (buy higher strike put, sell lower strike put)."""
        strategy = StrategyPosition(
            name="Bear Put Spread",
            market_outlook="Moderately bearish"
        )
        
        # Buy higher strike put
        long_put = OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.PUT,
            position_type=PositionType.LONG,
            strike_price=higher_strike,
            quantity=quantity,
            expiry_date=expiry_date
        )
        strategy.add_leg(long_put)
        
        # Sell lower strike put
        short_put = OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.PUT,
            position_type=PositionType.SHORT,
            strike_price=lower_strike,
            quantity=quantity,
            expiry_date=expiry_date
        )
        strategy.add_leg(short_put)
        
        return strategy
    
    @staticmethod
    def create_iron_condor(
        contract_symbol: str,
        put_strike_low: float,
        put_strike_high: float,
        call_strike_low: float,
        call_strike_high: float,
        expiry_date: date,
        quantity: int = 1
    ) -> StrategyPosition:
        """Create an iron condor strategy."""
        strategy = StrategyPosition(
            name="Iron Condor",
            market_outlook="Low volatility, range-bound"
        )
        
        # Buy low put
        strategy.add_leg(OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.PUT,
            position_type=PositionType.LONG,
            strike_price=put_strike_low,
            quantity=quantity,
            expiry_date=expiry_date
        ))
        
        # Sell high put
        strategy.add_leg(OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.PUT,
            position_type=PositionType.SHORT,
            strike_price=put_strike_high,
            quantity=quantity,
            expiry_date=expiry_date
        ))
        
        # Sell low call
        strategy.add_leg(OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.CALL,
            position_type=PositionType.SHORT,
            strike_price=call_strike_low,
            quantity=quantity,
            expiry_date=expiry_date
        ))
        
        # Buy high call
        strategy.add_leg(OptionLeg(
            contract_symbol=contract_symbol,
            option_type=OptionType.CALL,
            position_type=PositionType.LONG,
            strike_price=call_strike_high,
            quantity=quantity,
            expiry_date=expiry_date
        ))
        
        return strategy