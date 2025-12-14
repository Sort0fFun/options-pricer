"""
Black-76 Options Pricing Engine for NSE Futures

This module implements the Black-76 model for pricing European-style options
on futures contracts, specifically adapted for the Nairobi Securities Exchange.

The Black-76 model extends the Black-Scholes framework to handle futures contracts
by using the futures price directly and discounting the entire payoff at the 
risk-free rate.

Black-76 Formulas:
    Call: C = e^(-r*T) * [F * N(d1) - K * N(d2)]
    Put:  P = e^(-r*T) * [K * N(-d2) - F * N(-d1)]
    
    Where:
        d1 = [ln(F/K) + (sigma^2/2)*T] / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        
        F = current underlying forward/futures price
        K = strike price
        r = continuously compounded risk-free interest rate
        T = time in years until expiration
        sigma = implied volatility for the underlying forward price
        N() = standard normal cumulative distribution function

Reference:
    Black, Fischer (1976). The pricing of commodity contracts, 
    Journal of Financial Economics, 3, 167-179.
    https://www.glynholton.com/notes/black_1976/
"""

import numpy as np
import logging
from typing import Union, Dict, List, Optional
from scipy.stats import norm

from .validators import validate_pricing_inputs, PricingError
from .contracts import NSE_FUTURES
from .utils import TRADING_HOURS, EXPIRY_MONTHS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptionContract:
    """
    Data structure representing an option contract with all necessary parameters.
    
    Attributes:
        futures_price: Current price of the underlying futures contract (KES)
        strike_price: Exercise price of the option (KES)
        time_to_expiry: Time until expiration in years (decimal)
        volatility: Annual volatility of the futures price (decimal, e.g., 0.20 for 20%)
        risk_free_rate: Risk-free interest rate (decimal, e.g., 0.05 for 5%)
        option_type: 'call' or 'put'
        contract_symbol: NSE futures contract symbol (e.g., 'SCOM', 'NSE25')
    """
    def __init__(self, futures_price, strike_price, time_to_expiry, volatility, 
                 risk_free_rate, option_type, contract_symbol=None):
        self.futures_price = futures_price
        self.strike_price = strike_price
        self.time_to_expiry = time_to_expiry
        self.volatility = volatility
        self.risk_free_rate = risk_free_rate
        self.option_type = option_type
        self.contract_symbol = contract_symbol


class PricingResult:
    """
    Structured result from option pricing calculations.
    
    Attributes:
        option_price: Calculated fair value of the option (KES)
        d1, d2: Intermediate calculation values from Black-76 model
        nd1, nd2: Normal distribution values N(d1) and N(d2)
        contract: Original option contract details
        calculation_time: Time taken for calculation (seconds)
    """
    def __init__(self, option_price, d1, d2, nd1, nd2, contract, calculation_time):
        self.option_price = option_price
        self.d1 = d1
        self.d2 = d2
        self.nd1 = nd1
        self.nd2 = nd2
        self.contract = contract
        self.calculation_time = calculation_time


class Black76Pricer:
    """
    Main pricing engine implementing the Black-76 model for NSE futures options.
    
    This class provides methods for pricing individual options, batch pricing,
    and various utility functions for option valuation in the Kenyan market context.
    """
    
    def __init__(self):
        """Initialize the pricing engine with NSE market parameters."""
        self.supported_contracts = NSE_FUTURES
        self.trading_hours = TRADING_HOURS
        self.expiry_months = EXPIRY_MONTHS
        logger.info("Black76Pricer initialized for NSE market")
    
    def _calculate_d1_d2(
        self, 
        futures_price, 
        strike_price, 
        time_to_expiry, 
        volatility
    ):
        """
        Calculate d1 and d2 parameters for the Black-76 model.
        
        These are the key intermediate values used in the normal distribution
        functions that determine option prices.
        
        Args:
            futures_price: Current futures price
            strike_price: Option strike price
            time_to_expiry: Time to expiration in years
            volatility: Annual volatility
            
        Returns:
            Tuple of (d1, d2) values
        """
        sqrt_t = np.sqrt(time_to_expiry)
        vol_sqrt_t = volatility * sqrt_t
        
        d1 = (np.log(futures_price / strike_price) + 0.5 * volatility**2 * time_to_expiry) / vol_sqrt_t
        d2 = d1 - vol_sqrt_t
        
        return d1, d2
    
    def price_call(
        self,
        futures_price,
        strike_price,
        time_to_expiry,
        volatility,
        risk_free_rate,
        contract_symbol=None
    ):
        """
        Price a European call option using the Black-76 model.
        
        Formula: C = e^(-r*T) * [F * N(d1) - K * N(d2)]
        
        Args:
            futures_price: Current futures price (KES)
            strike_price: Strike price (KES)
            time_to_expiry: Time to expiry in years
            volatility: Annual volatility (e.g., 0.20 for 20%)
            risk_free_rate: Risk-free rate (e.g., 0.05 for 5%)
            contract_symbol: Optional NSE contract symbol
            
        Returns:
            Call option price in KES
            
        Raises:
            PricingError: If input validation fails
        """
        # Validate inputs
        validate_pricing_inputs(
            futures_price, strike_price, time_to_expiry, 
            volatility, risk_free_rate
        )
        
        # Calculate d1 and d2
        d1, d2 = self._calculate_d1_d2(
            futures_price, strike_price, time_to_expiry, volatility
        )
        
        # Calculate normal distribution values
        nd1 = norm.cdf(d1)
        nd2 = norm.cdf(d2)
        
        # Black-76 call formula
        discount_factor = np.exp(-risk_free_rate * time_to_expiry)
        call_price = discount_factor * (futures_price * nd1 - strike_price * nd2)
        
        return call_price
    
    def price_put(
        self,
        futures_price,
        strike_price,
        time_to_expiry,
        volatility,
        risk_free_rate,
        contract_symbol=None
    ):
        """
        Price a European put option using the Black-76 model.
        
        Formula: P = e^(-r*T) * [K * N(-d2) - F * N(-d1)]
        
        Args:
            futures_price: Current futures price (KES)
            strike_price: Strike price (KES)
            time_to_expiry: Time to expiry in years
            volatility: Annual volatility (e.g., 0.20 for 20%)
            risk_free_rate: Risk-free rate (e.g., 0.05 for 5%)
            contract_symbol: Optional NSE contract symbol
            
        Returns:
            Put option price in KES
            
        Raises:
            PricingError: If input validation fails
        """
        # Validate inputs
        validate_pricing_inputs(
            futures_price, strike_price, time_to_expiry, 
            volatility, risk_free_rate
        )
        
        # Calculate d1 and d2
        d1, d2 = self._calculate_d1_d2(
            futures_price, strike_price, time_to_expiry, volatility
        )
        
        # Calculate normal distribution values
        n_minus_d1 = norm.cdf(-d1)
        n_minus_d2 = norm.cdf(-d2)
        
        # Black-76 put formula
        discount_factor = np.exp(-risk_free_rate * time_to_expiry)
        put_price = discount_factor * (strike_price * n_minus_d2 - futures_price * n_minus_d1)
        
        return put_price
    
    def price_option(self, contract):
        """
        Price an option using the OptionContract data structure.
        
        Args:
            contract: OptionContract with all pricing parameters
            
        Returns:
            PricingResult with detailed pricing information
        """
        import time
        start_time = time.time()
        
        # Calculate d1 and d2
        d1, d2 = self._calculate_d1_d2(
            contract.futures_price, contract.strike_price, 
            contract.time_to_expiry, contract.volatility
        )
        
        # Calculate option price based on type
        if contract.option_type.lower() == 'call':
            option_price = self.price_call(
                contract.futures_price, contract.strike_price,
                contract.time_to_expiry, contract.volatility,
                contract.risk_free_rate, contract.contract_symbol
            )
            nd1 = norm.cdf(d1)
            nd2 = norm.cdf(d2)
        elif contract.option_type.lower() == 'put':
            option_price = self.price_put(
                contract.futures_price, contract.strike_price,
                contract.time_to_expiry, contract.volatility,
                contract.risk_free_rate, contract.contract_symbol
            )
            nd1 = norm.cdf(-d1)
            nd2 = norm.cdf(-d2)
        else:
            raise PricingError("Invalid option type: {}. Use 'call' or 'put'.".format(contract.option_type))
        
        calculation_time = time.time() - start_time
        
        return PricingResult(
            option_price=option_price,
            d1=d1,
            d2=d2,
            nd1=nd1,
            nd2=nd2,
            contract=contract,
            calculation_time=calculation_time
        )
    
    def price_batch(self, contracts):
        """
        Price multiple options efficiently in a batch operation.
        
        Args:
            contracts: List of dictionaries with option parameters
                      Required keys: F, K, T, vol, r, type
                      Optional keys: symbol
                      
        Returns:
            List of PricingResult objects
        """
        results = []
        
        for contract_data in contracts:
            try:
                contract = OptionContract(
                    futures_price=contract_data['F'],
                    strike_price=contract_data['K'], 
                    time_to_expiry=contract_data['T'],
                    volatility=contract_data['vol'],
                    risk_free_rate=contract_data['r'],
                    option_type=contract_data['type'],
                    contract_symbol=contract_data.get('symbol')
                )
                result = self.price_option(contract)
                results.append(result)
                
            except Exception as e:
                logger.error("Error pricing contract {}: {}".format(contract_data, e))
                # Continue with other contracts
                continue
        
        return results
    
    def calculate_intrinsic_value(
        self, 
        futures_price, 
        strike_price, 
        option_type
    ):
        """
        Calculate the intrinsic value of an option.
        
        Intrinsic value is the immediate exercise value of the option.
        
        Args:
            futures_price: Current futures price
            strike_price: Strike price  
            option_type: 'call' or 'put'
            
        Returns:
            Intrinsic value (always >= 0)
        """
        if option_type.lower() == 'call':
            return max(0, futures_price - strike_price)
        elif option_type.lower() == 'put':
            return max(0, strike_price - futures_price)
        else:
            raise PricingError("Invalid option type: {}".format(option_type))
    
    def calculate_time_value(
        self,
        option_price,
        intrinsic_value
    ):
        """
        Calculate the time value component of an option price.
        
        Time value = Option Price - Intrinsic Value
        
        Args:
            option_price: Current option price
            intrinsic_value: Intrinsic value of the option
            
        Returns:
            Time value component
        """
        return max(0, option_price - intrinsic_value)
    
    def get_contract_info(self, symbol):
        """
        Get information about a specific NSE futures contract.
        
        Args:
            symbol: Contract symbol (e.g., 'SCOM', 'NSE25')
            
        Returns:
            Dictionary with contract information
            
        Raises:
            PricingError: If contract symbol is not supported
        """
        if symbol not in self.supported_contracts:
            raise PricingError("Unsupported contract: {}. Supported: {}".format(symbol, list(self.supported_contracts.keys())))
        
        return self.supported_contracts[symbol]


# Convenience functions for quick pricing
def quick_call_price(F, K, T, vol, r):
    """Quick call option pricing function."""
    pricer = Black76Pricer()
    return pricer.price_call(F, K, T, vol, r)


def quick_put_price(F, K, T, vol, r):
    """Quick put option pricing function.""" 
    pricer = Black76Pricer()
    return pricer.price_put(F, K, T, vol, r)