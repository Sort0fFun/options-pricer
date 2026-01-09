"""
PnL service - P&L analysis for options strategies.
Note: This is a standalone implementation to avoid Streamlit dependencies from pnl_analysis.py
"""
import numpy as np
from typing import List, Dict, Optional


class PnLService:
    """Service for P&L analysis and strategy building."""

    @staticmethod
    def analyze_strategy(strategy: dict, market_params: dict) -> dict:
        """
        Analyze P&L for a custom strategy.

        Args:
            strategy: Strategy configuration with legs
            market_params: Market parameters (current_price, price_range_pct, time_to_expiry)

        Returns:
            dict: P&L analysis results with data and metrics
        """
        try:
            # Extract market parameters
            current_price = market_params.get('current_price', 100.0)
            price_range_pct = market_params.get('price_range_pct', 50)
            time_to_expiry = market_params.get('time_to_expiry', 0.0822)  # ~30 days

            # Calculate price range
            min_price = current_price * (1 - price_range_pct / 100)
            max_price = current_price * (1 + price_range_pct / 100)
            prices = np.linspace(min_price, max_price, 100)

            # Initialize analyzer
            analyzer = PnLAnalyzer()

            # Process each leg
            legs_data = {}
            total_pnl = np.zeros(len(prices))

            for i, leg in enumerate(strategy.get('legs', [])):
                option_type = leg.get('option_type', 'call')
                strike = leg.get('strike', current_price)
                premium = leg.get('premium', 0.0)
                quantity = leg.get('quantity', 1)
                position_type = leg.get('position_type', 'long')

                # Calculate P&L for this leg
                leg_pnl = []
                for price in prices:
                    intrinsic = max(0, price - strike) if option_type == 'call' else max(0, strike - price)
                    payoff = intrinsic - premium if position_type == 'long' else premium - intrinsic
                    leg_pnl.append(payoff * quantity)

                leg_pnl = np.array(leg_pnl)
                total_pnl += leg_pnl

                # Store leg data
                leg_name = f"leg_{i+1}_{option_type}_{int(strike)}"
                legs_data[leg_name] = leg_pnl.tolist()

            # Calculate metrics
            max_profit = float(np.max(total_pnl))
            max_loss = float(np.min(total_pnl))

            # Find breakeven points (where total_pnl crosses zero)
            breakeven_points = []
            for i in range(len(total_pnl) - 1):
                if (total_pnl[i] <= 0 and total_pnl[i + 1] > 0) or (total_pnl[i] >= 0 and total_pnl[i + 1] < 0):
                    # Linear interpolation for more accurate breakeven
                    breakeven = prices[i] + (prices[i + 1] - prices[i]) * (-total_pnl[i]) / (total_pnl[i + 1] - total_pnl[i])
                    breakeven_points.append(round(breakeven, 2))

            # Calculate net cost
            net_cost = sum(
                leg.get('premium', 0) * leg.get('quantity', 1) *
                (1 if leg.get('position_type') == 'long' else -1)
                for leg in strategy.get('legs', [])
            )

            return {
                'pnl_data': {
                    'prices': prices.tolist(),
                    'total_pnl': total_pnl.tolist(),
                    **legs_data
                },
                'metrics': {
                    'max_profit': round(max_profit, 2),
                    'max_loss': round(max_loss, 2),
                    'breakeven_points': breakeven_points,
                    'net_cost': round(net_cost, 2)
                }
            }

        except Exception as e:
            raise ValueError(f"Error analyzing strategy: {str(e)}")

    @staticmethod
    def build_strategy(strategy_name: str, parameters: dict) -> dict:
        """
        Build a pre-defined strategy.

        Args:
            strategy_name: Name of the strategy (e.g., 'long_call', 'bull_spread', etc.)
            parameters: Strategy parameters (spot_price, strikes, premiums, etc.)

        Returns:
            dict: P&L analysis results with description
        """
        try:
            # Extract common parameters
            spot_price = parameters.get('spot_price', 100.0)
            price_range_pct = parameters.get('price_range_pct', 50)

            # Calculate price range
            min_price = spot_price * (1 - price_range_pct / 100)
            max_price = spot_price * (1 + price_range_pct / 100)
            prices = np.linspace(min_price, max_price, 100)

            # Build strategy based on name
            builder = StrategyBuilder()
            strategy_map = {
                'long_call': builder.long_call,
                'long_put': builder.long_put,
                'bull_call_spread': builder.bull_call_spread,
                'bear_put_spread': builder.bear_put_spread,
                'long_straddle': builder.long_straddle,
                'long_strangle': builder.long_strangle,
                'iron_condor': builder.iron_condor,
                'butterfly_spread': builder.butterfly_spread,
                'covered_call': builder.covered_call
            }

            if strategy_name not in strategy_map:
                raise ValueError(f"Unknown strategy: {strategy_name}")

            # Get strategy function
            strategy_func = strategy_map[strategy_name]

            # Build strategy with parameters
            if strategy_name == 'long_call':
                strike = parameters.get('strike', spot_price)
                premium = parameters.get('premium', spot_price * 0.05)
                pnl = [max(0, p - strike) - premium for p in prices]
                description = f"Long Call: Buy call at strike {strike} for premium {premium}"

            elif strategy_name == 'long_put':
                strike = parameters.get('strike', spot_price)
                premium = parameters.get('premium', spot_price * 0.05)
                pnl = [max(0, strike - p) - premium for p in prices]
                description = f"Long Put: Buy put at strike {strike} for premium {premium}"

            elif strategy_name == 'bull_call_spread':
                lower_strike = parameters.get('lower_strike', spot_price * 0.95)
                upper_strike = parameters.get('upper_strike', spot_price * 1.05)
                lower_premium = parameters.get('lower_premium', spot_price * 0.07)
                upper_premium = parameters.get('upper_premium', spot_price * 0.03)
                pnl = [min(max(0, p - lower_strike) - lower_premium - (max(0, p - upper_strike) - upper_premium), upper_strike - lower_strike - (lower_premium - upper_premium)) for p in prices]
                description = f"Bull Call Spread: Buy call at {lower_strike}, sell call at {upper_strike}"

            elif strategy_name == 'bear_put_spread':
                lower_strike = parameters.get('lower_strike', spot_price * 0.95)
                upper_strike = parameters.get('upper_strike', spot_price * 1.05)
                lower_premium = parameters.get('lower_premium', spot_price * 0.03)
                upper_premium = parameters.get('upper_premium', spot_price * 0.07)
                pnl = [min(max(0, upper_strike - p) - upper_premium - (max(0, lower_strike - p) - lower_premium), upper_strike - lower_strike - (upper_premium - lower_premium)) for p in prices]
                description = f"Bear Put Spread: Buy put at {upper_strike}, sell put at {lower_strike}"

            elif strategy_name == 'long_straddle':
                strike = parameters.get('strike', spot_price)
                call_premium = parameters.get('call_premium', spot_price * 0.05)
                put_premium = parameters.get('put_premium', spot_price * 0.05)
                pnl = [max(0, p - strike) + max(0, strike - p) - call_premium - put_premium for p in prices]
                description = f"Long Straddle: Buy call and put at strike {strike}"

            elif strategy_name == 'long_strangle':
                call_strike = parameters.get('call_strike', spot_price * 1.05)
                put_strike = parameters.get('put_strike', spot_price * 0.95)
                call_premium = parameters.get('call_premium', spot_price * 0.03)
                put_premium = parameters.get('put_premium', spot_price * 0.03)
                pnl = [max(0, p - call_strike) + max(0, put_strike - p) - call_premium - put_premium for p in prices]
                description = f"Long Strangle: Buy call at {call_strike}, put at {put_strike}"

            elif strategy_name == 'iron_condor':
                put_lower = parameters.get('put_lower_strike', spot_price * 0.90)
                put_upper = parameters.get('put_upper_strike', spot_price * 0.95)
                call_lower = parameters.get('call_lower_strike', spot_price * 1.05)
                call_upper = parameters.get('call_upper_strike', spot_price * 1.10)
                total_credit = parameters.get('total_credit', spot_price * 0.04)
                pnl = [total_credit - max(0, max(0, put_upper - p) - max(0, put_lower - p)) - max(0, max(0, p - call_lower) - max(0, p - call_upper)) for p in prices]
                description = f"Iron Condor: Sell {put_upper}/{call_lower}, buy {put_lower}/{call_upper}"

            elif strategy_name == 'butterfly_spread':
                lower_strike = parameters.get('lower_strike', spot_price * 0.95)
                middle_strike = parameters.get('middle_strike', spot_price)
                upper_strike = parameters.get('upper_strike', spot_price * 1.05)
                net_cost = parameters.get('net_cost', spot_price * 0.02)
                pnl = [max(0, p - lower_strike) - 2 * max(0, p - middle_strike) + max(0, p - upper_strike) - net_cost for p in prices]
                description = f"Butterfly Spread: Buy {lower_strike}/{upper_strike}, sell 2x{middle_strike}"

            elif strategy_name == 'covered_call':
                stock_cost = parameters.get('stock_cost', spot_price)
                call_strike = parameters.get('call_strike', spot_price * 1.05)
                call_premium = parameters.get('call_premium', spot_price * 0.03)
                pnl = [p - stock_cost + call_premium - max(0, p - call_strike) for p in prices]
                description = f"Covered Call: Own stock at {stock_cost}, sell call at {call_strike}"

            else:
                pnl = [0] * len(prices)
                description = "Unknown strategy"

            # Calculate metrics
            pnl_array = np.array(pnl)
            max_profit = float(np.max(pnl_array))
            max_loss = float(np.min(pnl_array))

            # Find breakeven points
            breakeven_points = []
            for i in range(len(pnl_array) - 1):
                if (pnl_array[i] <= 0 and pnl_array[i + 1] > 0) or (pnl_array[i] >= 0 and pnl_array[i + 1] < 0):
                    breakeven = prices[i] + (prices[i + 1] - prices[i]) * (-pnl_array[i]) / (pnl_array[i + 1] - pnl_array[i])
                    breakeven_points.append(round(breakeven, 2))

            return {
                'pnl_data': {
                    'prices': prices.tolist(),
                    'total_pnl': pnl
                },
                'metrics': {
                    'max_profit': round(max_profit, 2),
                    'max_loss': round(max_loss, 2),
                    'breakeven_points': breakeven_points
                },
                'strategy_description': description
            }

        except Exception as e:
            raise ValueError(f"Error building strategy: {str(e)}")

    @staticmethod
    def get_available_strategies() -> dict:
        """
        Get list of available pre-built strategies.

        Returns:
            dict: List of strategies with descriptions
        """
        strategies = [
            {'name': 'long_call', 'label': 'Long Call', 'description': 'Buy a call option'},
            {'name': 'long_put', 'label': 'Long Put', 'description': 'Buy a put option'},
            {'name': 'bull_call_spread', 'label': 'Bull Call Spread', 'description': 'Buy lower strike call, sell higher strike call'},
            {'name': 'bear_put_spread', 'label': 'Bear Put Spread', 'description': 'Buy higher strike put, sell lower strike put'},
            {'name': 'long_straddle', 'label': 'Long Straddle', 'description': 'Buy call and put at same strike'},
            {'name': 'long_strangle', 'label': 'Long Strangle', 'description': 'Buy call and put at different strikes'},
            {'name': 'iron_condor', 'label': 'Iron Condor', 'description': 'Sell OTM put spread and call spread'},
            {'name': 'butterfly_spread', 'label': 'Butterfly Spread', 'description': 'Buy 1 low, sell 2 mid, buy 1 high strike'},
            {'name': 'covered_call', 'label': 'Covered Call', 'description': 'Own stock and sell call option'}
        ]

        return {'strategies': strategies, 'total': len(strategies)}
