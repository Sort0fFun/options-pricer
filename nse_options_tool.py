#!/usr/bin/env python3
"""
NSE Options on Futures Analysis Tool
Black-76 Pricing Model for Kenyan Equity Futures

A simple, locally relevant tool for analyzing European-style options
on Nairobi Securities Exchange (NSE) equity futures.
"""

import os
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.pricing.contracts import NSE_FUTURES
from src.core.pricing.black76 import Black76Pricer

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class NSEOptionsAnalyzer:
    """
    Simple options analysis tool for NSE futures using Black-76 model.
    
    Features:
    - Price European call/put options on NSE equity futures
    - Visualize option pricing across different spot prices
    - Analyze Greeks (Delta, Gamma, Vega, Theta)
    - Volatility impact analysis
    - Time decay visualization
    - Profit/Loss scenarios
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.pricer = Black76Pricer()
        self.contracts = NSE_FUTURES
        
        # NSE-specific parameters
        self.risk_free_rate = 0.12  # Kenya Central Bank Rate / T-Bill rate (~12%)
        self.typical_volatility = 0.25  # Typical NSE equity volatility (25%)
    
    def list_available_contracts(self) -> pd.DataFrame:
        """
        List all available NSE futures contracts.
        
        Returns:
            DataFrame with contract specifications
        """
        data = []
        for symbol, details in self.contracts.items():
            data.append({
                'Symbol': symbol,
                'Name': details['name'],
                'Sector': details['sector'],
                'Contract Size': details['contract_size'],
                'Tick Size': details['min_tick'],
                'Current Price': details.get('mtm_price', 'N/A'),
            })
        
        df = pd.DataFrame(data)
        return df
    
    def analyze_option(
        self,
        symbol: str,
        strike_price: float,
        days_to_expiry: int,
        volatility: Optional[float] = None,
        option_type: str = 'Call',
        risk_free_rate: Optional[float] = None,
        display: bool = True
    ) -> Dict:
        """
        Analyze a single option on NSE futures.
        
        Args:
            symbol: NSE futures symbol (e.g., 'SCOM', 'EQTY', 'KCBG')
            strike_price: Option strike price in KES
            days_to_expiry: Days until option expiry
            volatility: Annualized volatility (if None, uses typical 25%)
            option_type: 'Call' or 'Put'
            risk_free_rate: Risk-free rate (if None, uses Kenya CBR ~12%)
            display: Whether to print results
        
        Returns:
            Dictionary with pricing results and Greeks
        """
        # Get contract details
        if symbol not in self.contracts:
            raise ValueError(f"Unknown symbol: {symbol}. Use list_available_contracts()")
        
        contract = self.contracts[symbol]
        futures_price = contract.get('mtm_price', strike_price)
        
        # Use defaults if not provided
        if volatility is None:
            volatility = self.typical_volatility
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Convert days to years
        time_to_expiry = days_to_expiry / 365
        
        # Price the option
        if option_type.lower() == 'call':
            price = self.pricer.price_call(
                futures_price, strike_price, time_to_expiry,
                volatility, risk_free_rate
            )
            intrinsic = max(futures_price - strike_price, 0)
        else:
            price = self.pricer.price_put(
                futures_price, strike_price, time_to_expiry,
                volatility, risk_free_rate
            )
            intrinsic = max(strike_price - futures_price, 0)
        
        # Calculate Greeks
        delta = self.pricer.delta(
            futures_price, strike_price, time_to_expiry,
            volatility, risk_free_rate, option_type.lower()
        )
        
        gamma = self.pricer.gamma(
            futures_price, strike_price, time_to_expiry,
            volatility, risk_free_rate
        )
        
        vega = self.pricer.vega(
            futures_price, strike_price, time_to_expiry,
            volatility, risk_free_rate
        )
        
        theta = self.pricer.theta(
            futures_price, strike_price, time_to_expiry,
            volatility, risk_free_rate, option_type.lower()
        )
        
        rho = self.pricer.rho(
            futures_price, strike_price, time_to_expiry,
            volatility, risk_free_rate, option_type.lower()
        )
        
        # Calculate contract value
        contract_size = contract['contract_size']
        contract_value = price * contract_size
        
        # Moneyness
        moneyness_pct = (futures_price - strike_price) / strike_price * 100
        if option_type.lower() == 'call':
            moneyness = 'ITM' if futures_price > strike_price else 'OTM'
        else:
            moneyness = 'ITM' if strike_price > futures_price else 'OTM'
        
        results = {
            'symbol': symbol,
            'name': contract['name'],
            'option_type': option_type,
            'futures_price': futures_price,
            'strike_price': strike_price,
            'days_to_expiry': days_to_expiry,
            'time_to_expiry': time_to_expiry,
            'volatility': volatility,
            'risk_free_rate': risk_free_rate,
            'option_price': price,
            'intrinsic_value': intrinsic,
            'time_value': price - intrinsic,
            'contract_size': contract_size,
            'contract_value': contract_value,
            'moneyness': moneyness,
            'moneyness_pct': moneyness_pct,
            'greeks': {
                'delta': delta,
                'gamma': gamma,
                'vega': vega,
                'theta': theta,
                'rho': rho,
            }
        }
        
        if display:
            self._display_option_analysis(results)
        
        return results
    
    def _display_option_analysis(self, results: Dict):
        """Display formatted option analysis."""
        print(f"\n{'='*80}")
        print(f"  NSE OPTION ANALYSIS: {results['name']} ({results['symbol']})")
        print(f"{'='*80}")
        
        print(f"\n📋 CONTRACT DETAILS:")
        print(f"   Option Type:        {results['option_type']}")
        print(f"   Futures Price:      KES {results['futures_price']:.2f}")
        print(f"   Strike Price:       KES {results['strike_price']:.2f}")
        print(f"   Days to Expiry:     {results['days_to_expiry']}")
        print(f"   Moneyness:          {results['moneyness']} ({results['moneyness_pct']:+.1f}%)")
        
        print(f"\n💰 PRICING (Black-76 Model):")
        print(f"   Option Price:       KES {results['option_price']:.4f} per share")
        print(f"   Contract Value:     KES {results['contract_value']:.2f} (×{results['contract_size']})")
        print(f"   Intrinsic Value:    KES {results['intrinsic_value']:.4f}")
        print(f"   Time Value:         KES {results['time_value']:.4f}")
        
        print(f"\n📊 MARKET PARAMETERS:")
        print(f"   Volatility:         {results['volatility']:.1%}")
        print(f"   Risk-free Rate:     {results['risk_free_rate']:.1%} (Kenya CBR)")
        
        print(f"\n📈 GREEKS (Risk Measures):")
        print(f"   Delta (Δ):          {results['greeks']['delta']:7.4f}  "
              f"(Price change per KES 1 move in futures)")
        print(f"   Gamma (Γ):          {results['greeks']['gamma']:7.4f}  "
              f"(Delta change per KES 1 move)")
        print(f"   Vega (ν):           {results['greeks']['vega']:7.4f}  "
              f"(Price change per 1% volatility change)")
        print(f"   Theta (Θ):          {results['greeks']['theta']:7.4f}  "
              f"(Price decay per day)")
        print(f"   Rho (ρ):            {results['greeks']['rho']:7.4f}  "
              f"(Price change per 1% rate change)")
        
        print(f"\n{'='*80}\n")
    
    def visualize_price_surface(
        self,
        symbol: str,
        strike_price: float,
        days_to_expiry: int,
        option_type: str = 'Call',
        spot_range_pct: float = 0.3,
        save_plot: bool = False
    ):
        """
        Visualize option price across different futures prices.
        
        Args:
            symbol: NSE futures symbol
            strike_price: Option strike price
            days_to_expiry: Days to expiry
            option_type: 'Call' or 'Put'
            spot_range_pct: Price range as % of strike (default ±30%)
            save_plot: Whether to save the plot
        """
        contract = self.contracts[symbol]
        
        # Create price range
        spot_min = strike_price * (1 - spot_range_pct)
        spot_max = strike_price * (1 + spot_range_pct)
        spot_prices = np.linspace(spot_min, spot_max, 100)
        
        time_to_expiry = days_to_expiry / 365
        
        # Calculate option prices
        option_prices = []
        intrinsic_values = []
        
        for spot in spot_prices:
            if option_type.lower() == 'call':
                price = self.pricer.price_call(
                    spot, strike_price, time_to_expiry,
                    self.typical_volatility, self.risk_free_rate
                )
                intrinsic = max(spot - strike_price, 0)
            else:
                price = self.pricer.price_put(
                    spot, strike_price, time_to_expiry,
                    self.typical_volatility, self.risk_free_rate
                )
                intrinsic = max(strike_price - spot, 0)
            
            option_prices.append(price)
            intrinsic_values.append(intrinsic)
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 7))
        
        ax.plot(spot_prices, option_prices, 'b-', linewidth=2.5, 
                label=f'{option_type} Option Price')
        ax.plot(spot_prices, intrinsic_values, 'r--', linewidth=2, 
                label='Intrinsic Value')
        ax.fill_between(spot_prices, intrinsic_values, option_prices, 
                        alpha=0.3, label='Time Value')
        
        ax.axvline(strike_price, color='gray', linestyle=':', linewidth=1.5, 
                   label=f'Strike = KES {strike_price}')
        ax.axvline(contract['mtm_price'], color='green', linestyle=':', linewidth=1.5,
                   label=f'Current Futures = KES {contract["mtm_price"]}')
        
        ax.set_xlabel('Futures Price (KES)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Option Value (KES)', fontsize=12, fontweight='bold')
        ax.set_title(
            f'NSE {option_type} Option Price: {contract["name"]} ({symbol})\n'
            f'Strike: KES {strike_price} | Days to Expiry: {days_to_expiry} | Vol: {self.typical_volatility:.0%}',
            fontsize=14, fontweight='bold', pad=20
        )
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            filename = f'nse_{symbol}_{option_type}_price_surface.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved: {filename}")
        
        plt.show()
    
    def visualize_greeks(
        self,
        symbol: str,
        strike_price: float,
        days_to_expiry: int,
        option_type: str = 'Call',
        spot_range_pct: float = 0.3,
        save_plot: bool = False
    ):
        """
        Visualize Greeks across different futures prices.
        
        Args:
            symbol: NSE futures symbol
            strike_price: Strike price
            days_to_expiry: Days to expiry
            option_type: 'Call' or 'Put'
            spot_range_pct: Price range as % of strike
            save_plot: Whether to save plot
        """
        contract = self.contracts[symbol]
        
        spot_min = strike_price * (1 - spot_range_pct)
        spot_max = strike_price * (1 + spot_range_pct)
        spot_prices = np.linspace(spot_min, spot_max, 100)
        
        time_to_expiry = days_to_expiry / 365
        
        # Calculate Greeks
        deltas, gammas, vegas, thetas = [], [], [], []
        
        for spot in spot_prices:
            delta = self.pricer.delta(
                spot, strike_price, time_to_expiry,
                self.typical_volatility, self.risk_free_rate, option_type.lower()
            )
            gamma = self.pricer.gamma(
                spot, strike_price, time_to_expiry,
                self.typical_volatility, self.risk_free_rate
            )
            vega = self.pricer.vega(
                spot, strike_price, time_to_expiry,
                self.typical_volatility, self.risk_free_rate
            )
            theta = self.pricer.theta(
                spot, strike_price, time_to_expiry,
                self.typical_volatility, self.risk_free_rate, option_type.lower()
            )
            
            deltas.append(delta)
            gammas.append(gamma)
            vegas.append(vega)
            thetas.append(theta)
        
        # Plot
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Delta
        axes[0, 0].plot(spot_prices, deltas, 'b-', linewidth=2.5)
        axes[0, 0].axvline(strike_price, color='gray', linestyle=':', alpha=0.7)
        axes[0, 0].axhline(0, color='black', linestyle='-', linewidth=0.5)
        axes[0, 0].set_title('Delta (Δ) - Price Sensitivity', fontweight='bold')
        axes[0, 0].set_xlabel('Futures Price (KES)')
        axes[0, 0].set_ylabel('Delta')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Gamma
        axes[0, 1].plot(spot_prices, gammas, 'r-', linewidth=2.5)
        axes[0, 1].axvline(strike_price, color='gray', linestyle=':', alpha=0.7)
        axes[0, 1].set_title('Gamma (Γ) - Delta Sensitivity', fontweight='bold')
        axes[0, 1].set_xlabel('Futures Price (KES)')
        axes[0, 1].set_ylabel('Gamma')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Vega
        axes[1, 0].plot(spot_prices, vegas, 'g-', linewidth=2.5)
        axes[1, 0].axvline(strike_price, color='gray', linestyle=':', alpha=0.7)
        axes[1, 0].set_title('Vega (ν) - Volatility Sensitivity', fontweight='bold')
        axes[1, 0].set_xlabel('Futures Price (KES)')
        axes[1, 0].set_ylabel('Vega')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Theta
        axes[1, 1].plot(spot_prices, thetas, 'm-', linewidth=2.5)
        axes[1, 1].axvline(strike_price, color='gray', linestyle=':', alpha=0.7)
        axes[1, 1].axhline(0, color='black', linestyle='-', linewidth=0.5)
        axes[1, 1].set_title('Theta (Θ) - Time Decay', fontweight='bold')
        axes[1, 1].set_xlabel('Futures Price (KES)')
        axes[1, 1].set_ylabel('Theta (per day)')
        axes[1, 1].grid(True, alpha=0.3)
        
        fig.suptitle(
            f'Greeks Analysis: {contract["name"]} ({symbol}) {option_type}\n'
            f'Strike: KES {strike_price} | Days: {days_to_expiry}',
            fontsize=14, fontweight='bold', y=1.00
        )
        
        plt.tight_layout()
        
        if save_plot:
            filename = f'nse_{symbol}_{option_type}_greeks.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved: {filename}")
        
        plt.show()
    
    def visualize_volatility_impact(
        self,
        symbol: str,
        strike_price: float,
        days_to_expiry: int,
        option_type: str = 'Call',
        vol_range: Tuple[float, float] = (0.10, 0.50),
        save_plot: bool = False
    ):
        """
        Visualize how volatility affects option price.
        
        Args:
            symbol: NSE futures symbol
            strike_price: Strike price
            days_to_expiry: Days to expiry
            option_type: 'Call' or 'Put'
            vol_range: Volatility range (min, max)
            save_plot: Whether to save plot
        """
        contract = self.contracts[symbol]
        futures_price = contract['mtm_price']
        time_to_expiry = days_to_expiry / 365
        
        # Volatility range
        vols = np.linspace(vol_range[0], vol_range[1], 50)
        prices = []
        
        for vol in vols:
            if option_type.lower() == 'call':
                price = self.pricer.price_call(
                    futures_price, strike_price, time_to_expiry,
                    vol, self.risk_free_rate
                )
            else:
                price = self.pricer.price_put(
                    futures_price, strike_price, time_to_expiry,
                    vol, self.risk_free_rate
                )
            prices.append(price)
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 7))
        
        ax.plot(vols * 100, prices, 'b-', linewidth=2.5)
        ax.axvline(self.typical_volatility * 100, color='red', linestyle='--',
                   linewidth=2, label=f'Typical NSE Vol = {self.typical_volatility:.0%}')
        
        ax.set_xlabel('Volatility (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Option Price (KES)', fontsize=12, fontweight='bold')
        ax.set_title(
            f'Volatility Impact: {contract["name"]} ({symbol}) {option_type}\n'
            f'Futures: KES {futures_price} | Strike: KES {strike_price} | Days: {days_to_expiry}',
            fontsize=14, fontweight='bold', pad=20
        )
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            filename = f'nse_{symbol}_{option_type}_volatility_impact.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved: {filename}")
        
        plt.show()
    
    def visualize_time_decay(
        self,
        symbol: str,
        strike_price: float,
        max_days: int = 90,
        option_type: str = 'Call',
        save_plot: bool = False
    ):
        """
        Visualize time decay (Theta) effect.
        
        Args:
            symbol: NSE futures symbol
            strike_price: Strike price
            max_days: Maximum days to expiry
            option_type: 'Call' or 'Put'
            save_plot: Whether to save plot
        """
        contract = self.contracts[symbol]
        futures_price = contract['mtm_price']
        
        days = np.arange(1, max_days + 1)
        prices = []
        
        for day in days:
            time_to_expiry = day / 365
            if option_type.lower() == 'call':
                price = self.pricer.price_call(
                    futures_price, strike_price, time_to_expiry,
                    self.typical_volatility, self.risk_free_rate
                )
            else:
                price = self.pricer.price_put(
                    futures_price, strike_price, time_to_expiry,
                    self.typical_volatility, self.risk_free_rate
                )
            prices.append(price)
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 7))
        
        ax.plot(days, prices, 'b-', linewidth=2.5)
        
        ax.set_xlabel('Days to Expiry', fontsize=12, fontweight='bold')
        ax.set_ylabel('Option Price (KES)', fontsize=12, fontweight='bold')
        ax.set_title(
            f'Time Decay: {contract["name"]} ({symbol}) {option_type}\n'
            f'Futures: KES {futures_price} | Strike: KES {strike_price} | Vol: {self.typical_volatility:.0%}',
            fontsize=14, fontweight='bold', pad=20
        )
        ax.grid(True, alpha=0.3)
        
        # Add annotation for theta
        mid_point = len(days) // 2
        ax.annotate(
            'Time value decays\nfaster near expiry',
            xy=(days[mid_point], prices[mid_point]),
            xytext=(days[mid_point] + 10, prices[mid_point] + 0.5),
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
            fontsize=10, color='red'
        )
        
        plt.tight_layout()
        
        if save_plot:
            filename = f'nse_{symbol}_{option_type}_time_decay.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved: {filename}")
        
        plt.show()
    
    def compare_strikes(
        self,
        symbol: str,
        strikes: List[float],
        days_to_expiry: int,
        option_type: str = 'Call',
        display: bool = True
    ) -> pd.DataFrame:
        """
        Compare multiple strike prices.
        
        Args:
            symbol: NSE futures symbol
            strikes: List of strike prices
            days_to_expiry: Days to expiry
            option_type: 'Call' or 'Put'
            display: Whether to print results
        
        Returns:
            DataFrame with comparison
        """
        contract = self.contracts[symbol]
        futures_price = contract['mtm_price']
        
        results = []
        for strike in strikes:
            analysis = self.analyze_option(
                symbol, strike, days_to_expiry,
                option_type=option_type, display=False
            )
            
            results.append({
                'Strike': strike,
                'Moneyness': analysis['moneyness'],
                'Option Price': analysis['option_price'],
                'Intrinsic': analysis['intrinsic_value'],
                'Time Value': analysis['time_value'],
                'Delta': analysis['greeks']['delta'],
                'Gamma': analysis['greeks']['gamma'],
                'Vega': analysis['greeks']['vega'],
                'Theta': analysis['greeks']['theta'],
            })
        
        df = pd.DataFrame(results)
        
        if display:
            print(f"\n{'='*80}")
            print(f"STRIKE COMPARISON: {contract['name']} ({symbol}) {option_type}")
            print(f"Futures Price: KES {futures_price} | Days to Expiry: {days_to_expiry}")
            print(f"{'='*80}\n")
            print(df.to_string(index=False))
            print(f"\n{'='*80}\n")
        
        return df


# =============================================================================
# DEMONSTRATION & EXAMPLES
# =============================================================================

def main():
    """Run demonstration of NSE Options Analysis Tool."""
    
    print("\n" + "="*80)
    print(" " * 20 + "NSE OPTIONS ON FUTURES ANALYSIS TOOL")
    print(" " * 25 + "Black-76 Pricing Model")
    print("="*80)
    
    # Initialize analyzer
    analyzer = NSEOptionsAnalyzer()
    
    # Example 1: List available contracts
    print("\n" + "="*80)
    print("EXAMPLE 1: Available NSE Futures Contracts")
    print("="*80 + "\n")
    
    contracts_df = analyzer.list_available_contracts()
    print(contracts_df.to_string(index=False))
    
    # Example 2: Analyze a single option
    print("\n" + "="*80)
    print("EXAMPLE 2: Analyze Safaricom (SCOM) Call Option")
    print("="*80)
    
    scom_call = analyzer.analyze_option(
        symbol='SCOM',
        strike_price=30.0,
        days_to_expiry=30,
        option_type='Call',
        volatility=0.28
    )
    
    # Example 3: Compare multiple strikes
    print("\n" + "="*80)
    print("EXAMPLE 3: Compare Different Strike Prices")
    print("="*80)
    
    strikes = [25.0, 27.5, 30.0, 32.5, 35.0]
    comparison = analyzer.compare_strikes(
        symbol='SCOM',
        strikes=strikes,
        days_to_expiry=30,
        option_type='Call'
    )
    
    # Example 4: Visualizations
    print("\n" + "="*80)
    print("EXAMPLE 4: Generating Visualizations...")
    print("="*80)
    
    try:
        # Price surface
        print("\n📊 1. Option Price Surface")
        analyzer.visualize_price_surface(
            symbol='SCOM',
            strike_price=30.0,
            days_to_expiry=30,
            option_type='Call',
            save_plot=True
        )
        
        # Greeks
        print("\n📊 2. Greeks Analysis")
        analyzer.visualize_greeks(
            symbol='SCOM',
            strike_price=30.0,
            days_to_expiry=30,
            option_type='Call',
            save_plot=True
        )
        
        # Volatility impact
        print("\n📊 3. Volatility Impact")
        analyzer.visualize_volatility_impact(
            symbol='SCOM',
            strike_price=30.0,
            days_to_expiry=30,
            option_type='Call',
            save_plot=True
        )
        
        # Time decay
        print("\n📊 4. Time Decay")
        analyzer.visualize_time_decay(
            symbol='SCOM',
            strike_price=30.0,
            max_days=90,
            option_type='Call',
            save_plot=True
        )
        
        print("\n✓ All visualizations generated successfully!")
        
    except Exception as e:
        print(f"\nNote: Visualization requires matplotlib. Error: {e}")
    
    # Example 5: Put option analysis
    print("\n" + "="*80)
    print("EXAMPLE 5: Equity Group (EQTY) Put Option")
    print("="*80)
    
    eqty_put = analyzer.analyze_option(
        symbol='EQTY',
        strike_price=60.0,
        days_to_expiry=45,
        option_type='Put',
        volatility=0.30
    )
    
    print("\n" + "="*80)
    print("  ANALYSIS COMPLETE - Tool Ready for Use!")
    print("="*80)
    print("\nKey Features:")
    print("  ✓ Black-76 pricing for NSE equity futures options")
    print("  ✓ European-style call and put options")
    print("  ✓ Complete Greeks analysis (Delta, Gamma, Vega, Theta, Rho)")
    print("  ✓ Volatility impact assessment")
    print("  ✓ Time decay visualization")
    print("  ✓ Strike price comparison")
    print("  ✓ Locally relevant (Kenya-specific risk-free rate, NSE contracts)")
    print("\nUsage:")
    print("  from nse_options_tool import NSEOptionsAnalyzer")
    print("  analyzer = NSEOptionsAnalyzer()")
    print("  analyzer.analyze_option('SCOM', strike_price=30, days_to_expiry=30)")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
