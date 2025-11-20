"""
NSE Market Data Simulator

This module generates realistic market data for NSE futures contracts,
including price movements, volume patterns, and market regime effects.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta, time
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

from ..utils.calendar import NSECalendar
from ...core.pricing.contracts import NSE_FUTURES

logger = logging.getLogger(__name__)


@dataclass
class MarketRegime:
    """
    Defines a market regime with specific characteristics.
    
    Attributes:
        name: Regime name (e.g., 'bull', 'bear', 'sideways')
        annual_return: Expected annual return
        annual_volatility: Expected annual volatility
        regime_persistence: Probability of staying in same regime
        correlation_multiplier: How much correlations increase in this regime
    """
    name: str
    annual_return: float
    annual_volatility: float
    regime_persistence: float
    correlation_multiplier: float = 1.0


@dataclass
class SimulationConfig:
    """
    Configuration for market simulation.
    
    Attributes:
        start_date: Simulation start date
        end_date: Simulation end date  
        frequency: Data frequency ('D' for daily, 'H' for hourly)
        contracts: List of contracts to simulate
        base_regime: Starting market regime
        include_weekends: Whether to include weekend data
        random_seed: Random seed for reproducibility
    """
    start_date: datetime
    end_date: datetime
    frequency: str = 'D'
    contracts: List[str] = None
    base_regime: str = 'normal'
    include_weekends: bool = False
    random_seed: Optional[int] = None


class NSEMarketSimulator:
    """
    Main simulator for NSE market data.
    
    This class generates realistic market data including:
    - Correlated price movements across contracts
    - Realistic volume patterns
    - Market regime switches
    - NSE-specific calendar effects
    """
    
    def __init__(self):
        """Initialize the NSE market simulator."""
        self.calendar = NSECalendar()
        self.regimes = self._define_market_regimes()
        self.correlations = self._define_correlations()
        self.current_regime = 'normal'
        
        logger.info("NSE Market Simulator initialized")
    
    def _define_market_regimes(self) -> Dict[str, MarketRegime]:
        """Define different market regimes for NSE."""
        return {
            'bull': MarketRegime(
                name='bull',
                annual_return=0.15,
                annual_volatility=0.20,
                regime_persistence=0.95,
                correlation_multiplier=0.8
            ),
            'bear': MarketRegime(
                name='bear',
                annual_return=-0.10,
                annual_volatility=0.35,
                regime_persistence=0.90,
                correlation_multiplier=1.5
            ),
            'normal': MarketRegime(
                name='normal',
                annual_return=0.08,
                annual_volatility=0.25,
                regime_persistence=0.98,
                correlation_multiplier=1.0
            ),
            'volatile': MarketRegime(
                name='volatile',
                annual_return=0.05,
                annual_volatility=0.45,
                regime_persistence=0.85,
                correlation_multiplier=1.3
            ),
            'crisis': MarketRegime(
                name='crisis',
                annual_return=-0.25,
                annual_volatility=0.60,
                regime_persistence=0.80,
                correlation_multiplier=2.0
            )
        }
    
    def _define_correlations(self) -> Dict[str, Dict[str, float]]:
        """Define correlation matrix for NSE contracts."""
        return {
            'SCOM': {'KCB': 0.3, 'EQTY': 0.25, 'ABSA': 0.2, 'NSE25': 0.7},
            'KCB': {'SCOM': 0.3, 'EQTY': 0.6, 'ABSA': 0.7, 'NSE25': 0.8},
            'EQTY': {'SCOM': 0.25, 'KCB': 0.6, 'ABSA': 0.65, 'NSE25': 0.75},
            'ABSA': {'SCOM': 0.2, 'KCB': 0.7, 'EQTY': 0.65, 'NSE25': 0.7},
            'NSE25': {'SCOM': 0.7, 'KCB': 0.8, 'EQTY': 0.75, 'ABSA': 0.7},
            'MNSE25': {'NSE25': 0.99, 'SCOM': 0.65, 'KCB': 0.75, 'EQTY': 0.7, 'ABSA': 0.65}
        }
    
    def generate_price_data(
        self,
        contract: str,
        start_price: float,
        days: int,
        regime: str = 'normal',
        random_seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate price data for a single contract.
        
        Args:
            contract: NSE contract symbol
            start_price: Starting price
            days: Number of days to simulate
            regime: Market regime
            random_seed: Random seed for reproducibility
            
        Returns:
            DataFrame with price, volume, and other market data
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        if contract not in NSE_FUTURES:
            raise ValueError(f"Unknown contract: {contract}")
        
        if regime not in self.regimes:
            raise ValueError(f"Unknown regime: {regime}")
        
        # Get regime parameters
        regime_params = self.regimes[regime]
        contract_params = NSE_FUTURES[contract]
        
        # Calculate daily parameters
        dt = 1 / 252  # Daily time step
        daily_return = regime_params.annual_return * dt
        daily_volatility = regime_params.annual_volatility * np.sqrt(dt)
        
        # Generate price path using GBM
        prices = self._generate_gbm_path(
            start_price, daily_return, daily_volatility, days
        )
        
        # Generate volume data
        volumes = self._generate_volume_data(
            prices, contract_params['average_volume'], days
        )
        
        # Create date index
        dates = pd.date_range(
            start=datetime.now().date(),
            periods=days,
            freq='D'
        )
        
        # Create DataFrame
        data = pd.DataFrame({
            'date': dates,
            'price': prices,
            'volume': volumes,
            'contract': contract,
            'regime': regime
        })
        
        # Add derived fields
        data['returns'] = data['price'].pct_change()
        data['log_returns'] = np.log(data['price'] / data['price'].shift(1))
        data['high'] = data['price'] * (1 + np.abs(data['returns']) * 0.5)
        data['low'] = data['price'] * (1 - np.abs(data['returns']) * 0.5)
        data['close'] = data['price']
        data['open'] = data['price'].shift(1).fillna(start_price)
        
        # Round prices to tick size
        tick_size = contract_params['tick_size']
        data['price'] = (data['price'] / tick_size).round() * tick_size
        data['high'] = (data['high'] / tick_size).round() * tick_size
        data['low'] = (data['low'] / tick_size).round() * tick_size
        data['close'] = (data['close'] / tick_size).round() * tick_size
        data['open'] = (data['open'] / tick_size).round() * tick_size
        
        return data.dropna()
    
    def _generate_gbm_path(
        self,
        start_price: float,
        mu: float,
        sigma: float,
        n_days: int
    ) -> np.ndarray:
        """
        Generate price path using Geometric Brownian Motion.
        
        Args:
            start_price: Starting price
            mu: Daily drift
            sigma: Daily volatility
            n_days: Number of days
            
        Returns:
            Array of prices
        """
        # Generate random shocks
        shocks = np.random.normal(0, 1, n_days)
        
        # Calculate log returns
        log_returns = (mu - 0.5 * sigma**2) + sigma * shocks
        
        # Convert to prices
        log_prices = np.log(start_price) + np.cumsum(log_returns)
        prices = np.exp(log_prices)
        
        return prices
    
    def _generate_volume_data(
        self,
        prices: np.ndarray,
        base_volume: float,
        n_days: int
    ) -> np.ndarray:
        """
        Generate volume data correlated with price movements.
        
        Args:
            prices: Price series
            base_volume: Base volume level
            n_days: Number of days
            
        Returns:
            Array of volumes
        """
        # Calculate returns for volume correlation
        returns = np.diff(np.log(prices))
        
        # Volume increases with absolute returns
        volume_multiplier = 1 + 2 * np.abs(returns)
        
        # Add random noise to volume
        volume_noise = np.random.lognormal(0, 0.3, len(volume_multiplier))
        
        # Calculate volumes
        volumes = base_volume * volume_multiplier * volume_noise
        
        # Add first day volume
        first_volume = base_volume * np.random.lognormal(0, 0.2)
        volumes = np.concatenate([[first_volume], volumes])
        
        # Ensure positive volumes
        volumes = np.maximum(volumes, base_volume * 0.1)
        
        return volumes.astype(int)
    
    def generate_multi_asset_data(
        self,
        contracts: List[str],
        days: int,
        regime: str = 'normal',
        random_seed: Optional[int] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate correlated data for multiple contracts.
        
        Args:
            contracts: List of contract symbols
            days: Number of days to simulate
            regime: Market regime
            random_seed: Random seed
            
        Returns:
            Dictionary mapping contract to DataFrame
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Get regime parameters
        regime_params = self.regimes[regime]
        
        # Generate correlated random shocks
        n_assets = len(contracts)
        correlation_matrix = self._build_correlation_matrix(contracts, regime_params)
        
        # Cholesky decomposition for correlated random numbers
        try:
            chol = np.linalg.cholesky(correlation_matrix)
            independent_shocks = np.random.normal(0, 1, (days, n_assets))
            correlated_shocks = independent_shocks @ chol.T
        except np.linalg.LinAlgError:
            # Fallback to independent shocks if correlation matrix is invalid
            logger.warning("Invalid correlation matrix, using independent shocks")
            correlated_shocks = np.random.normal(0, 1, (days, n_assets))
        
        # Generate data for each contract
        results = {}
        
        for i, contract in enumerate(contracts):
            contract_params = NSE_FUTURES[contract]
            start_price = contract_params.get('last_price', 100.0)
            
            # Use correlated shocks for this contract
            shocks = correlated_shocks[:, i]
            
            # Calculate price path
            dt = 1 / 252
            daily_return = regime_params.annual_return * dt
            daily_volatility = regime_params.annual_volatility * np.sqrt(dt)
            
            log_returns = (daily_return - 0.5 * daily_volatility**2) + daily_volatility * shocks
            log_prices = np.log(start_price) + np.cumsum(log_returns)
            prices = np.exp(log_prices)
            
            # Generate volume
            volumes = self._generate_volume_data(
                prices, contract_params.get('average_volume', 1000000), days
            )
            
            # Create DataFrame
            dates = pd.date_range(
                start=datetime.now().date(),
                periods=days,
                freq='D'
            )
            
            data = pd.DataFrame({
                'date': dates,
                'price': prices,
                'volume': volumes,
                'contract': contract,
                'regime': regime
            })
            
            # Add derived fields
            data['returns'] = data['price'].pct_change()
            data['log_returns'] = np.log(data['price'] / data['price'].shift(1))
            
            results[contract] = data.dropna()
        
        return results
    
    def _build_correlation_matrix(
        self,
        contracts: List[str],
        regime_params: MarketRegime
    ) -> np.ndarray:
        """
        Build correlation matrix for given contracts and regime.
        
        Args:
            contracts: List of contract symbols
            regime_params: Market regime parameters
            
        Returns:
            Correlation matrix
        """
        n = len(contracts)
        correlation_matrix = np.eye(n)
        
        for i, contract_i in enumerate(contracts):
            for j, contract_j in enumerate(contracts):
                if i != j:
                    # Get base correlation
                    base_corr = self.correlations.get(contract_i, {}).get(contract_j, 0.1)
                    
                    # Adjust for regime
                    adjusted_corr = base_corr * regime_params.correlation_multiplier
                    adjusted_corr = np.clip(adjusted_corr, -0.95, 0.95)
                    
                    correlation_matrix[i, j] = adjusted_corr
        
        # Ensure positive definite
        min_eigenval = np.min(np.linalg.eigvals(correlation_matrix))
        if min_eigenval < 0:
            correlation_matrix += (-min_eigenval + 0.01) * np.eye(n)
        
        return correlation_matrix
    
    def generate_regime_switching_data(
        self,
        contract: str,
        days: int,
        regime_probabilities: Dict[str, float] = None,
        random_seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate data with regime switching.
        
        Args:
            contract: Contract symbol
            days: Number of days
            regime_probabilities: Probabilities for each regime
            random_seed: Random seed
            
        Returns:
            DataFrame with regime-switching data
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        if regime_probabilities is None:
            regime_probabilities = {
                'normal': 0.7,
                'bull': 0.1,
                'bear': 0.1,
                'volatile': 0.08,
                'crisis': 0.02
            }
        
        # Generate regime sequence
        regimes = self._generate_regime_sequence(days, regime_probabilities)
        
        # Generate price data regime by regime
        contract_params = NSE_FUTURES[contract]
        start_price = contract_params.get('last_price', 100.0)
        
        all_data = []
        current_price = start_price
        
        regime_starts = [0] + [i for i in range(1, len(regimes)) if regimes[i] != regimes[i-1]] + [len(regimes)]
        
        for i in range(len(regime_starts) - 1):
            start_idx = regime_starts[i]
            end_idx = regime_starts[i + 1]
            regime = regimes[start_idx]
            regime_days = end_idx - start_idx
            
            # Generate data for this regime
            regime_data = self.generate_price_data(
                contract, current_price, regime_days, regime
            )
            
            # Update current price for next regime
            current_price = regime_data['price'].iloc[-1]
            
            # Adjust dates
            if all_data:
                last_date = all_data[-1]['date'].iloc[-1]
                new_dates = pd.date_range(
                    start=last_date + timedelta(days=1),
                    periods=regime_days,
                    freq='D'
                )
                regime_data['date'] = new_dates
            
            all_data.append(regime_data)
        
        # Combine all data
        combined_data = pd.concat(all_data, ignore_index=True)
        
        return combined_data
    
    def _generate_regime_sequence(
        self,
        days: int,
        regime_probabilities: Dict[str, float]
    ) -> List[str]:
        """
        Generate sequence of market regimes.
        
        Args:
            days: Number of days
            regime_probabilities: Regime probabilities
            
        Returns:
            List of regime names
        """
        regimes = list(regime_probabilities.keys())
        probabilities = list(regime_probabilities.values())
        
        # Start with a random regime
        current_regime = np.random.choice(regimes, p=probabilities)
        regime_sequence = [current_regime]
        
        for _ in range(days - 1):
            # Check if we stay in current regime
            persistence = self.regimes[current_regime].regime_persistence
            
            if np.random.random() < persistence:
                # Stay in current regime
                regime_sequence.append(current_regime)
            else:
                # Switch regime
                current_regime = np.random.choice(regimes, p=probabilities)
                regime_sequence.append(current_regime)
        
        return regime_sequence
    
    def generate_intraday_data(
        self,
        contract: str,
        trading_date: datetime,
        start_price: float,
        regime: str = 'normal'
    ) -> pd.DataFrame:
        """
        Generate intraday (hourly) data for a single trading day.
        
        Args:
            contract: Contract symbol
            trading_date: Trading date
            start_price: Starting price for the day
            regime: Market regime
            
        Returns:
            DataFrame with intraday data
        """
        # NSE trading hours: 9 AM to 3 PM (6 hours)
        trading_hours = 6
        intervals_per_hour = 4  # 15-minute intervals
        total_intervals = trading_hours * intervals_per_hour
        
        regime_params = self.regimes[regime]
        
        # Intraday volatility pattern (higher at open/close)
        volatility_pattern = np.array([
            1.5, 1.3, 1.1, 1.0,  # 9-10 AM (higher at open)
            0.8, 0.7, 0.6, 0.7,  # 10-11 AM
            0.6, 0.5, 0.5, 0.6,  # 11-12 PM
            0.7, 0.8, 0.9, 1.0,  # 12-1 PM
            1.1, 1.2, 1.3, 1.4,  # 1-2 PM
            1.5, 1.6, 1.7, 1.8   # 2-3 PM (higher at close)
        ])
        
        # Generate price movements
        base_volatility = regime_params.annual_volatility / np.sqrt(252 * total_intervals)
        volatilities = base_volatility * volatility_pattern
        
        returns = np.random.normal(0, volatilities, total_intervals)
        log_prices = np.log(start_price) + np.cumsum(returns)
        prices = np.exp(log_prices)
        
        # Generate timestamps
        start_time = trading_date.replace(hour=9, minute=0, second=0)
        timestamps = [start_time + timedelta(minutes=15*i) for i in range(total_intervals)]
        
        # Generate volumes (higher at open/close)
        base_volume = NSE_FUTURES[contract].get('average_volume', 1000000) // total_intervals
        volume_pattern = volatility_pattern * 0.8 + 0.2  # Volume follows volatility
        volumes = np.random.poisson(base_volume * volume_pattern)
        
        # Create DataFrame
        data = pd.DataFrame({
            'datetime': timestamps,
            'price': prices,
            'volume': volumes,
            'contract': contract,
            'regime': regime
        })
        
        return data
    
    def add_corporate_actions(
        self,
        data: pd.DataFrame,
        contract: str,
        action_probability: float = 0.02
    ) -> pd.DataFrame:
        """
        Add corporate actions to price data.
        
        Args:
            data: Price data DataFrame
            contract: Contract symbol
            action_probability: Probability of corporate action per day
            
        Returns:
            DataFrame with corporate actions applied
        """
        data = data.copy()
        
        for i, row in data.iterrows():
            if np.random.random() < action_probability:
                action_type = np.random.choice(['dividend', 'split', 'rights'], p=[0.7, 0.2, 0.1])
                
                if action_type == 'dividend':
                    # Dividend payment (price drops by dividend amount)
                    dividend_yield = np.random.uniform(0.01, 0.05)
                    dividend_amount = row['price'] * dividend_yield
                    data.loc[i:, 'price'] -= dividend_amount
                    logger.info(f"Dividend payment on {row['date']}: {dividend_amount:.2f}")
                
                elif action_type == 'split':
                    # Stock split (price halved, but not relevant for futures)
                    split_ratio = np.random.choice([2, 3])
                    data.loc[i:, 'price'] /= split_ratio
                    logger.info(f"Stock split on {row['date']}: 1:{split_ratio}")
                
                elif action_type == 'rights':
                    # Rights issue (temporary price drop)
                    rights_discount = np.random.uniform(0.05, 0.15)
                    data.loc[i, 'price'] *= (1 - rights_discount)
                    logger.info(f"Rights issue on {row['date']}: {rights_discount:.1%} discount")
        
        return data
    
    def generate_stress_scenario(
        self,
        contract: str,
        scenario_type: str,
        days: int = 30,
        random_seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate specific stress testing scenarios.
        
        Args:
            contract: Contract symbol
            scenario_type: Type of stress scenario
            days: Number of days
            random_seed: Random seed
            
        Returns:
            DataFrame with stress scenario data
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        stress_scenarios = {
            'market_crash': {
                'regime': 'crisis',
                'initial_shock': -0.15,
                'recovery_days': 10
            },
            'liquidity_crisis': {
                'regime': 'volatile',
                'volume_reduction': 0.3,
                'volatility_spike': 2.0
            },
            'currency_crisis': {
                'regime': 'bear',
                'correlation_with_usd': 0.8,
                'volatility_increase': 1.5
            }
        }
        
        if scenario_type not in stress_scenarios:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
        
        scenario = stress_scenarios[scenario_type]
        contract_params = NSE_FUTURES[contract]
        start_price = contract_params.get('last_price', 100.0)
        
        # Apply initial shock if specified
        if 'initial_shock' in scenario:
            start_price *= (1 + scenario['initial_shock'])
        
        # Generate base data
        data = self.generate_price_data(
            contract, start_price, days, scenario['regime']
        )
        
        # Apply scenario-specific modifications
        if scenario_type == 'liquidity_crisis':
            # Reduce volume
            data['volume'] *= scenario['volume_reduction']
            
            # Increase volatility
            data['returns'] *= scenario['volatility_spike']
            data['price'] = data['price'].iloc[0] * np.exp(data['returns'].cumsum())
        
        return data


# Convenience functions
def generate_sample_nse_data(
    contract: str = 'SCOM',
    days: int = 252,
    regime: str = 'normal'
) -> pd.DataFrame:
    """
    Generate sample NSE data for quick testing.
    
    Args:
        contract: NSE contract symbol
        days: Number of days
        regime: Market regime
        
    Returns:
        DataFrame with simulated data
    """
    simulator = NSEMarketSimulator()
    start_price = NSE_FUTURES[contract].get('last_price', 100.0)
    
    return simulator.generate_price_data(contract, start_price, days, regime)


def generate_multi_contract_data(
    contracts: List[str] = None,
    days: int = 252
) -> Dict[str, pd.DataFrame]:
    """
    Generate data for multiple NSE contracts.
    
    Args:
        contracts: List of contract symbols
        days: Number of days
        
    Returns:
        Dictionary mapping contract to DataFrame
    """
    if contracts is None:
        contracts = ['SCOM', 'KCB', 'EQTY']
    
    simulator = NSEMarketSimulator()
    return simulator.generate_multi_asset_data(contracts, days)