"""
Pricing service - wraps Black76Pricer for option pricing calculations.
"""
import numpy as np
from src.core.pricing.black76 import Black76Pricer
from src.core.pricing.contracts import NSE_FUTURES


class PricingService:
    """Service for option pricing calculations using Black-76 model."""

    # NSE market fees (as percentages)
    NSE_FEES = {
        'nse_clear': 0.0125,
        'clearing_member': 0.0125,
        'trading_member': 0.05,
        'ipf_levy': 0.005,
        'cma_fee': 0.005,
        'total': 0.085
    }

    @staticmethod
    def calculate_option_price(
        futures_price: float,
        strike_price: float,
        days_to_expiry: int,
        volatility: float,
        risk_free_rate: float,
        option_type: str = 'call',
        include_fees: bool = False
    ) -> dict:
        """
        Calculate option price using Black-76 model.

        Args:
            futures_price: Current futures price
            strike_price: Strike price
            days_to_expiry: Days until expiration
            volatility: Implied volatility (0-1)
            risk_free_rate: Risk-free rate (0-1)
            option_type: 'call' or 'put'
            include_fees: Whether to include NSE fees

        Returns:
            dict: Pricing results with call/put prices and fees
        """
        # Convert days to years
        time_to_maturity = days_to_expiry / 365.0

        # Initialize pricer
        pricer = Black76Pricer()

        # Calculate prices
        call_price = pricer.price_call(
            futures_price=futures_price,
            strike_price=strike_price,
            time_to_expiry=time_to_maturity,
            volatility=volatility,
            risk_free_rate=risk_free_rate
        )
        put_price = pricer.price_put(
            futures_price=futures_price,
            strike_price=strike_price,
            time_to_expiry=time_to_maturity,
            volatility=volatility,
            risk_free_rate=risk_free_rate
        )

        # Calculate prices with fees if requested
        call_price_with_fees = call_price
        put_price_with_fees = put_price

        if include_fees:
            fee_multiplier = 1 + (PricingService.NSE_FEES['total'] / 100)
            call_price_with_fees = call_price * fee_multiplier
            put_price_with_fees = put_price * fee_multiplier

        return {
            'call_price': round(call_price, 4),
            'put_price': round(put_price, 4),
            'call_price_with_fees': round(call_price_with_fees, 4),
            'put_price_with_fees': round(put_price_with_fees, 4),
            'fees': PricingService.NSE_FEES,
            'pricing_summary': {
                'current_asset_price': futures_price,
                'strike_price': strike_price,
                'time_to_maturity': round(time_to_maturity, 4),
                'volatility': volatility,
                'risk_free_rate': risk_free_rate
            }
        }

    @staticmethod
    def generate_heatmap(
        futures_price: float,
        strike_price: float,
        days_to_expiry: int,
        volatility: float,
        risk_free_rate: float,
        price_range_pct: float = 20.0,
        vol_range_pct: float = 50.0,
        grid_size: int = 12
    ) -> dict:
        """
        Generate heatmap data for option pricing visualization.

        Args:
            futures_price: Current futures price
            strike_price: Strike price
            days_to_expiry: Days until expiration
            volatility: Base volatility (0-1)
            risk_free_rate: Risk-free rate (0-1)
            price_range_pct: Price range as percentage of futures price
            vol_range_pct: Volatility range as percentage of base volatility
            grid_size: Number of grid points (default 12)

        Returns:
            dict: Heatmap data with call/put prices matrices
        """
        time_to_maturity = days_to_expiry / 365.0

        # Calculate price range
        price_delta = futures_price * (price_range_pct / 100)
        min_spot = futures_price - price_delta
        max_spot = futures_price + price_delta
        spot_range = np.linspace(min_spot, max_spot, grid_size)

        # Calculate volatility range
        vol_delta = volatility * (vol_range_pct / 100)
        min_vol = max(0.01, volatility - vol_delta)
        max_vol = volatility + vol_delta
        vol_range = np.linspace(min_vol, max_vol, grid_size)

        # Initialize matrices
        call_prices = np.zeros((grid_size, grid_size))
        put_prices = np.zeros((grid_size, grid_size))

        # Initialize pricer
        pricer = Black76Pricer()

        # Calculate prices for each combination
        for i, spot in enumerate(spot_range):
            for j, vol in enumerate(vol_range):
                call_prices[j][i] = pricer.price_call(
                    futures_price=spot,
                    strike_price=strike_price,
                    time_to_expiry=time_to_maturity,
                    volatility=vol,
                    risk_free_rate=risk_free_rate
                )
                put_prices[j][i] = pricer.price_put(
                    futures_price=spot,
                    strike_price=strike_price,
                    time_to_expiry=time_to_maturity,
                    volatility=vol,
                    risk_free_rate=risk_free_rate
                )

        return {
            'call_prices': call_prices.tolist(),
            'put_prices': put_prices.tolist(),
            'spot_range': spot_range.tolist(),
            'vol_range': vol_range.tolist(),
            'current_spot': futures_price,
            'current_vol': volatility
        }

    @staticmethod
    def get_contracts() -> dict:
        """
        Get available NSE futures contracts.

        Returns:
            dict: Contract information
        """
        contracts = []
        for symbol, info in NSE_FUTURES.items():
            contracts.append({
                'symbol': symbol,
                'name': info['name'],
                'sector': info.get('sector', 'Unknown'),
                'contract_size': info.get('contract_size', 100),
                'min_tick': info.get('min_tick', 0.05),
                'mtm_price': info.get('mtm_price', 0.0)
            })

        return {'contracts': contracts, 'total': len(contracts)}
