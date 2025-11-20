"""
Greeks Calculator for Black-76 Options

This module calculates the risk sensitivities (Greeks) for European options
on futures contracts using the Black-76 model framework.
"""

import numpy as np
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from scipy.stats import norm

from ..pricing.black76 import Black76Pricer, OptionContract, PricingResult
from ..pricing.validators import validate_pricing_inputs, PricingError

logger = logging.getLogger(__name__)


@dataclass
class GreeksProfile:
    """
    Container for all Greeks values for a single option.
    
    Attributes:
        delta: Price sensitivity to underlying futures price changes
        gamma: Rate of change of delta (delta sensitivity)  
        vega: Sensitivity to volatility changes (per 1% vol change)
        theta: Time decay (per day)
        rho: Sensitivity to interest rate changes (per 1% rate change)
        lambda_: Leverage/elasticity (percentage sensitivity)
        contract: Original option contract
        calculation_time: Time taken for calculations
    """
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    lambda_: float
    contract: OptionContract
    calculation_time: float = 0.0


@dataclass 
class AdvancedGreeks:
    """
    Container for second-order and exotic Greeks.
    
    Attributes:
        vanna: Delta sensitivity to volatility changes
        charm: Delta sensitivity to time passage
        vomma: Vega sensitivity to volatility changes (volga)
        speed: Gamma sensitivity to underlying price changes
        zomma: Gamma sensitivity to volatility changes
        color: Gamma sensitivity to time passage
    """
    vanna: float
    charm: float
    vomma: float
    speed: float
    zomma: float
    color: float


class GreeksCalculator:
    """
    Main Greeks calculation engine for Black-76 options.
    
    This class provides comprehensive Greeks calculations including
    first-order Greeks (delta, gamma, vega, theta, rho) and advanced
    second-order Greeks for sophisticated risk management.
    """
    
    def __init__(self, pricer: Optional[Black76Pricer] = None):
        """
        Initialize Greeks calculator.
        
        Args:
            pricer: Optional Black76Pricer instance (creates new one if None)
        """
        self.pricer = pricer or Black76Pricer()
        logger.info("GreeksCalculator initialized")
    
    def _standard_normal_pdf(self, x: float) -> float:
        """Calculate standard normal probability density function."""
        return np.exp(-0.5 * x * x) / np.sqrt(2 * np.pi)
    
    def calculate_delta(
        self,
        d1: float,
        option_type: str,
        risk_free_rate: float,
        time_to_expiry: float
    ) -> float:
        """
        Calculate delta for Black-76 options.
        
        Args:
            d1: Black-76 d1 parameter
            option_type: 'call' or 'put'
            risk_free_rate: Annual risk-free rate
            time_to_expiry: Time to expiry in years
            
        Returns:
            Delta value
        """
        discount_factor = np.exp(-risk_free_rate * time_to_expiry)
        
        if option_type.lower() == 'call':
            return discount_factor * norm.cdf(d1)
        else:  # put
            return discount_factor * (norm.cdf(d1) - 1)
    
    def calculate_gamma(
        self,
        d1: float,
        futures_price: float,
        volatility: float,
        time_to_expiry: float,
        risk_free_rate: float
    ) -> float:
        """
        Calculate gamma (same for calls and puts).
        
        Args:
            d1: Black-76 d1 parameter
            futures_price: Current futures price
            volatility: Annual volatility
            time_to_expiry: Time to expiry in years
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Gamma value
        """
        discount_factor = np.exp(-risk_free_rate * time_to_expiry)
        phi_d1 = self._standard_normal_pdf(d1)
        
        return (discount_factor * phi_d1) / (futures_price * volatility * np.sqrt(time_to_expiry))
    
    def calculate_vega(
        self,
        d1: float,
        futures_price: float,
        time_to_expiry: float,
        risk_free_rate: float
    ) -> float:
        """
        Calculate vega (same for calls and puts).
        
        Returns vega per 1% volatility change (divide by 100 for 1 point change).
        
        Args:
            d1: Black-76 d1 parameter
            futures_price: Current futures price
            time_to_expiry: Time to expiry in years
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Vega per 1% volatility change
        """
        discount_factor = np.exp(-risk_free_rate * time_to_expiry)
        phi_d1 = self._standard_normal_pdf(d1)
        
        # Multiply by 0.01 to get sensitivity per 1% vol change
        return discount_factor * futures_price * np.sqrt(time_to_expiry) * phi_d1 * 0.01
    
    def calculate_theta(
        self,
        d1: float,
        d2: float,
        futures_price: float,
        strike_price: float,
        volatility: float,
        time_to_expiry: float,
        risk_free_rate: float,
        option_type: str
    ) -> float:
        """
        Calculate theta (time decay per day).
        
        Args:
            d1, d2: Black-76 d1 and d2 parameters
            futures_price: Current futures price
            strike_price: Strike price
            volatility: Annual volatility
            time_to_expiry: Time to expiry in years
            risk_free_rate: Annual risk-free rate
            option_type: 'call' or 'put'
            
        Returns:
            Theta per day
        """
        discount_factor = np.exp(-risk_free_rate * time_to_expiry)
        phi_d1 = self._standard_normal_pdf(d1)
        
        # Common term
        term1 = -discount_factor * futures_price * phi_d1 * volatility / (2 * np.sqrt(time_to_expiry))
        
        if option_type.lower() == 'call':
            term2 = -risk_free_rate * discount_factor * strike_price * norm.cdf(d2)
            theta_annual = term1 + term2
        else:  # put
            term2 = risk_free_rate * discount_factor * strike_price * norm.cdf(-d2)
            theta_annual = term1 + term2
        
        # Convert to daily theta (divide by 365)
        return theta_annual / 365.25
    
    def calculate_rho(
        self,
        d2: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        option_type: str
    ) -> float:
        """
        Calculate rho (sensitivity to 1% interest rate change).
        
        Args:
            d2: Black-76 d2 parameter
            strike_price: Strike price
            time_to_expiry: Time to expiry in years
            risk_free_rate: Annual risk-free rate
            option_type: 'call' or 'put'
            
        Returns:
            Rho per 1% rate change
        """
        discount_factor = np.exp(-risk_free_rate * time_to_expiry)
        
        if option_type.lower() == 'call':
            rho_raw = strike_price * time_to_expiry * discount_factor * norm.cdf(d2)
        else:  # put
            rho_raw = -strike_price * time_to_expiry * discount_factor * norm.cdf(-d2)
        
        # Convert to per 1% rate change
        return rho_raw * 0.01
    
    def calculate_lambda(
        self,
        delta: float,
        futures_price: float,
        option_price: float
    ) -> float:
        """
        Calculate lambda (leverage/elasticity).
        
        Lambda measures the percentage change in option price
        relative to percentage change in underlying price.
        
        Args:
            delta: Option delta
            futures_price: Current futures price
            option_price: Current option price
            
        Returns:
            Lambda (leverage ratio)
        """
        if option_price <= 0:
            return 0.0
        
        return delta * futures_price / option_price
    
    def calculate_greeks(
        self,
        futures_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float,
        option_type: str,
        contract_symbol: Optional[str] = None
    ) -> GreeksProfile:
        """
        Calculate all Greeks for an option.
        
        Args:
            futures_price: Current futures price
            strike_price: Strike price
            time_to_expiry: Time to expiry in years
            volatility: Annual volatility
            risk_free_rate: Annual risk-free rate
            option_type: 'call' or 'put'
            contract_symbol: Optional contract symbol
            
        Returns:
            GreeksProfile with all Greeks values
        """
        import time
        start_time = time.time()
        
        # Validate inputs
        validate_pricing_inputs(
            futures_price, strike_price, time_to_expiry,
            volatility, risk_free_rate, option_type
        )
        
        # Create contract object
        contract = OptionContract(
            futures_price=futures_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            volatility=volatility,
            risk_free_rate=risk_free_rate,
            option_type=option_type,
            contract_symbol=contract_symbol
        )
        
        # Get pricing result for d1, d2 values
        pricing_result = self.pricer.price_option(contract)
        option_price = pricing_result.option_price
        d1 = pricing_result.d1
        d2 = pricing_result.d2
        
        # Calculate all Greeks
        delta = self.calculate_delta(d1, option_type, risk_free_rate, time_to_expiry)
        
        gamma = self.calculate_gamma(
            d1, futures_price, volatility, time_to_expiry, risk_free_rate
        )
        
        vega = self.calculate_vega(d1, futures_price, time_to_expiry, risk_free_rate)
        
        theta = self.calculate_theta(
            d1, d2, futures_price, strike_price, volatility,
            time_to_expiry, risk_free_rate, option_type
        )
        
        rho = self.calculate_rho(
            d2, strike_price, time_to_expiry, risk_free_rate, option_type
        )
        
        lambda_ = self.calculate_lambda(delta, futures_price, option_price)
        
        calculation_time = time.time() - start_time
        
        return GreeksProfile(
            delta=delta,
            gamma=gamma,
            vega=vega,
            theta=theta,
            rho=rho,
            lambda_=lambda_,
            contract=contract,
            calculation_time=calculation_time
        )
    
    def calculate_advanced_greeks(
        self,
        d1: float,
        d2: float,
        futures_price: float,
        strike_price: float,
        volatility: float,
        time_to_expiry: float,
        risk_free_rate: float,
        option_type: str
    ) -> AdvancedGreeks:
        """
        Calculate advanced second-order Greeks.
        
        Args:
            d1, d2: Black-76 d1 and d2 parameters
            futures_price: Current futures price
            strike_price: Strike price
            volatility: Annual volatility
            time_to_expiry: Time to expiry in years
            risk_free_rate: Annual risk-free rate
            option_type: 'call' or 'put'
            
        Returns:
            AdvancedGreeks object
        """
        discount_factor = np.exp(-risk_free_rate * time_to_expiry)
        phi_d1 = self._standard_normal_pdf(d1)
        sqrt_t = np.sqrt(time_to_expiry)
        
        # Vanna: delta sensitivity to volatility
        vanna = -discount_factor * phi_d1 * d2 / volatility
        
        # Charm: delta sensitivity to time
        term1 = -discount_factor * phi_d1 * (2 * risk_free_rate * time_to_expiry - d2 * volatility * sqrt_t)
        charm = term1 / (2 * time_to_expiry * volatility * sqrt_t)
        
        # Vomma (Volga): vega sensitivity to volatility
        vomma = discount_factor * futures_price * sqrt_t * phi_d1 * d1 * d2 / volatility
        
        # Speed: gamma sensitivity to underlying price
        speed = -self.calculate_gamma(d1, futures_price, volatility, time_to_expiry, risk_free_rate)
        speed = speed / futures_price * (d1 / (volatility * sqrt_t) + 1)
        
        # Zomma: gamma sensitivity to volatility
        gamma = self.calculate_gamma(d1, futures_price, volatility, time_to_expiry, risk_free_rate)
        zomma = gamma * (d1 * d2 - 1) / volatility
        
        # Color: gamma sensitivity to time
        term1 = -discount_factor * phi_d1 / (2 * futures_price * time_to_expiry * volatility * sqrt_t)
        term2 = 2 * risk_free_rate * time_to_expiry + 1 + d1 * (2 * risk_free_rate * time_to_expiry - d2 * volatility * sqrt_t) / (volatility * sqrt_t)
        color = term1 * term2
        
        return AdvancedGreeks(
            vanna=vanna,
            charm=charm,
            vomma=vomma,
            speed=speed,
            zomma=zomma,
            color=color
        )
    
    def calculate_batch_greeks(self, contracts: List[Dict]) -> List[GreeksProfile]:
        """
        Calculate Greeks for multiple options efficiently.
        
        Args:
            contracts: List of contract parameter dictionaries
            
        Returns:
            List of GreeksProfile objects
        """
        results = []
        
        for contract_data in contracts:
            try:
                greeks = self.calculate_greeks(
                    futures_price=contract_data['F'],
                    strike_price=contract_data['K'],
                    time_to_expiry=contract_data['T'],
                    volatility=contract_data['vol'],
                    risk_free_rate=contract_data['r'],
                    option_type=contract_data['type'],
                    contract_symbol=contract_data.get('symbol')
                )
                results.append(greeks)
                
            except Exception as e:
                logger.error(f"Error calculating Greeks for contract {contract_data}: {e}")
                continue
        
        return results
    
    def calculate_portfolio_greeks(
        self,
        positions: List[Dict],
        include_advanced: bool = False
    ) -> Dict[str, float]:
        """
        Calculate aggregate Greeks for a portfolio of positions.
        
        Args:
            positions: List of position dictionaries with contract details and quantities
            include_advanced: Whether to include advanced Greeks
            
        Returns:
            Dictionary with aggregate Greeks
        """
        total_greeks = {
            'delta': 0.0,
            'gamma': 0.0,
            'vega': 0.0,
            'theta': 0.0,
            'rho': 0.0,
            'lambda': 0.0
        }
        
        total_option_value = 0.0
        
        for position in positions:
            try:
                # Calculate Greeks for this position
                greeks = self.calculate_greeks(
                    futures_price=position['F'],
                    strike_price=position['K'],
                    time_to_expiry=position['T'],
                    volatility=position['vol'],
                    risk_free_rate=position['r'],
                    option_type=position['type']
                )
                
                # Get position size
                quantity = position.get('quantity', 1)
                multiplier = position.get('multiplier', 1)
                total_contracts = quantity * multiplier
                
                # Calculate option value for this position
                option_price = self.pricer.price_option(greeks.contract).option_price
                position_value = option_price * total_contracts
                total_option_value += position_value
                
                # Add weighted Greeks to totals
                total_greeks['delta'] += greeks.delta * total_contracts
                total_greeks['gamma'] += greeks.gamma * total_contracts
                total_greeks['vega'] += greeks.vega * total_contracts
                total_greeks['theta'] += greeks.theta * total_contracts
                total_greeks['rho'] += greeks.rho * total_contracts
                
            except Exception as e:
                logger.error(f"Error processing position {position}: {e}")
                continue
        
        # Calculate portfolio lambda
        if total_option_value > 0:
            # Weight lambda by position values
            weighted_lambda = 0.0
            for position in positions:
                try:
                    greeks = self.calculate_greeks(
                        position['F'], position['K'], position['T'],
                        position['vol'], position['r'], position['type']
                    )
                    option_price = self.pricer.price_option(greeks.contract).option_price
                    quantity = position.get('quantity', 1) * position.get('multiplier', 1)
                    position_value = option_price * quantity
                    weight = position_value / total_option_value
                    weighted_lambda += greeks.lambda_ * weight
                except:
                    continue
            total_greeks['lambda'] = weighted_lambda
        
        return total_greeks
    
    def sensitivity_analysis(
        self,
        base_contract: Dict,
        parameter: str,
        shock_range: float = 0.1,
        num_points: int = 21
    ) -> Dict:
        """
        Perform sensitivity analysis on Greeks to parameter changes.
        
        Args:
            base_contract: Base contract parameters
            parameter: Parameter to shock ('F', 'vol', 'T', 'r')
            shock_range: Range of shocks as percentage (e.g., 0.1 for ±10%)
            num_points: Number of points in the analysis
            
        Returns:
            Dictionary with shocked values and corresponding Greeks
        """
        results = {
            'shocked_values': [],
            'greeks': []
        }
        
        base_value = base_contract[parameter]
        shock_values = np.linspace(
            base_value * (1 - shock_range),
            base_value * (1 + shock_range),
            num_points
        )
        
        for shock_value in shock_values:
            shocked_contract = base_contract.copy()
            shocked_contract[parameter] = shock_value
            
            try:
                greeks = self.calculate_greeks(
                    futures_price=shocked_contract['F'],
                    strike_price=shocked_contract['K'],
                    time_to_expiry=shocked_contract['T'],
                    volatility=shocked_contract['vol'],
                    risk_free_rate=shocked_contract['r'],
                    option_type=shocked_contract['type']
                )
                
                results['shocked_values'].append(shock_value)
                results['greeks'].append(greeks)
                
            except Exception as e:
                logger.error(f"Error in sensitivity analysis at {parameter}={shock_value}: {e}")
                continue
        
        return results


# Convenience functions
def quick_greeks(F: float, K: float, T: float, vol: float, r: float, opt_type: str) -> GreeksProfile:
    """Quick Greeks calculation function."""
    calculator = GreeksCalculator()
    return calculator.calculate_greeks(F, K, T, vol, r, opt_type)