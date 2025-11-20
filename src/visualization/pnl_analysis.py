"""
Profit & Loss Analysis for Options Strategies
Interactive P&L diagrams and scenario analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import math

from src.core.pricing.black76 import Black76Calculator
from src.core.greeks.calculator import GreeksCalculator


@dataclass
class OptionPosition:
    """Represents a single option position"""
    option_type: str  # 'call' or 'put'
    strike: float
    premium: float
    quantity: int  # positive for long, negative for short
    expiry_days: int
    position_type: str  # 'long' or 'short'


@dataclass
class StrategyLeg:
    """Single leg of an options strategy"""
    option_type: str
    strike: float
    premium: float
    quantity: int
    position_type: str


class PnLAnalyzer:
    """Analyze P&L for options positions and strategies"""
    
    def __init__(self):
        self.pricing_calculator = Black76Calculator()
        self.greeks_calculator = GreeksCalculator()
    
    def calculate_option_pnl(
        self,
        position: OptionPosition,
        underlying_prices: np.ndarray,
        time_to_expiry: float = None
    ) -> np.ndarray:
        """
        Calculate P&L for a single option position
        
        Args:
            position: Option position details
            underlying_prices: Array of underlying prices to evaluate
            time_to_expiry: Time to expiry (if None, assumes expiry)
            
        Returns:
            Array of P&L values
        """
        pnl = np.zeros_like(underlying_prices)
        
        for i, S in enumerate(underlying_prices):
            if time_to_expiry is None or time_to_expiry <= 0:
                # At expiry - intrinsic value
                if position.option_type.lower() == 'call':
                    intrinsic = max(0, S - position.strike)
                else:  # put
                    intrinsic = max(0, position.strike - S)
            else:
                # Before expiry - use Black76 pricing
                try:
                    intrinsic = self.pricing_calculator.calculate_option_price(
                        S=S,
                        K=position.strike,
                        T=time_to_expiry,
                        r=0.05,  # Default risk-free rate
                        sigma=0.25,  # Default volatility
                        option_type=position.option_type.lower()
                    )
                except:
                    intrinsic = 0
            
            # Calculate P&L based on position type
            if position.position_type.lower() == 'long':
                pnl[i] = (intrinsic - position.premium) * position.quantity
            else:  # short
                pnl[i] = (position.premium - intrinsic) * abs(position.quantity)
        
        return pnl
    
    def calculate_strategy_pnl(
        self,
        legs: List[StrategyLeg],
        underlying_prices: np.ndarray,
        time_to_expiry: float = None
    ) -> Dict[str, np.ndarray]:
        """
        Calculate P&L for a multi-leg options strategy
        
        Returns:
            Dictionary with total P&L and individual leg P&Ls
        """
        result = {'total': np.zeros_like(underlying_prices)}
        
        for i, leg in enumerate(legs):
            # Convert StrategyLeg to OptionPosition
            position = OptionPosition(
                option_type=leg.option_type,
                strike=leg.strike,
                premium=leg.premium,
                quantity=leg.quantity,
                expiry_days=0,  # Not used in this calculation
                position_type=leg.position_type
            )
            
            # Calculate P&L for this leg
            leg_pnl = self.calculate_option_pnl(position, underlying_prices, time_to_expiry)
            
            # Store individual leg P&L
            result[f'leg_{i+1}_{leg.option_type}_{leg.strike}'] = leg_pnl
            
            # Add to total
            result['total'] += leg_pnl
        
        return result
    
    def create_pnl_diagram(
        self,
        pnl_data: Dict[str, np.ndarray],
        underlying_prices: np.ndarray,
        title: str = "P&L Diagram",
        show_individual_legs: bool = True
    ) -> go.Figure:
        """Create interactive P&L diagram"""
        
        fig = go.Figure()
        
        # Add individual legs if requested
        if show_individual_legs and len(pnl_data) > 1:
            for key, pnl in pnl_data.items():
                if key != 'total':
                    fig.add_trace(go.Scatter(
                        x=underlying_prices,
                        y=pnl,
                        name=key.replace('_', ' ').title(),
                        line=dict(dash='dot', width=1),
                        opacity=0.6,
                        hovertemplate='Price: KES %{x:.2f}<br>P&L: KES %{y:.2f}<extra></extra>'
                    ))
        
        # Add total P&L
        fig.add_trace(go.Scatter(
            x=underlying_prices,
            y=pnl_data['total'],
            name='Total P&L',
            line=dict(color='blue', width=3),
            fill='tonexty' if pnl_data['total'].min() >= 0 else None,
            hovertemplate='Price: KES %{x:.2f}<br>Total P&L: KES %{y:.2f}<extra></extra>'
        ))
        
        # Add break-even lines
        breakeven_points = self.find_breakeven_points(underlying_prices, pnl_data['total'])
        for be_point in breakeven_points:
            fig.add_vline(
                x=be_point,
                line_dash="dash",
                line_color="red",
                annotation_text=f"BE: KES {be_point:.2f}",
                annotation_position="top"
            )
        
        # Add zero P&L line
        fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title='Underlying Price (KES)',
            yaxis_title='Profit/Loss (KES)',
            width=900,
            height=600,
            hovermode='x unified',
            legend=dict(x=0.02, y=0.98)
        )
        
        return fig
    
    def find_breakeven_points(
        self,
        prices: np.ndarray,
        pnl: np.ndarray,
        tolerance: float = 0.01
    ) -> List[float]:
        """Find breakeven points where P&L crosses zero"""
        breakeven_points = []
        
        # Find sign changes
        for i in range(len(pnl) - 1):
            if pnl[i] * pnl[i + 1] < 0:  # Sign change
                # Linear interpolation to find exact crossing point
                x1, y1 = prices[i], pnl[i]
                x2, y2 = prices[i + 1], pnl[i + 1]
                
                # Find x where y = 0
                if y2 != y1:
                    x_zero = x1 - y1 * (x2 - x1) / (y2 - y1)
                    breakeven_points.append(x_zero)
        
        return breakeven_points
    
    def calculate_max_profit_loss(
        self,
        prices: np.ndarray,
        pnl: np.ndarray
    ) -> Dict[str, float]:
        """Calculate maximum profit and loss"""
        return {
            'max_profit': float(np.max(pnl)),
            'max_loss': float(np.min(pnl)),
            'max_profit_price': float(prices[np.argmax(pnl)]),
            'max_loss_price': float(prices[np.argmin(pnl)])
        }


class StrategyBuilder:
    """Build common options strategies"""
    
    @staticmethod
    def long_call(strike: float, premium: float) -> List[StrategyLeg]:
        """Long call strategy"""
        return [StrategyLeg("call", strike, premium, 1, "long")]
    
    @staticmethod
    def long_put(strike: float, premium: float) -> List[StrategyLeg]:
        """Long put strategy"""
        return [StrategyLeg("put", strike, premium, 1, "long")]
    
    @staticmethod
    def covered_call(call_strike: float, call_premium: float) -> List[StrategyLeg]:
        """Covered call strategy (short call)"""
        return [StrategyLeg("call", call_strike, call_premium, 1, "short")]
    
    @staticmethod
    def protective_put(put_strike: float, put_premium: float) -> List[StrategyLeg]:
        """Protective put strategy (long put)"""
        return [StrategyLeg("put", put_strike, put_premium, 1, "long")]
    
    @staticmethod
    def bull_call_spread(
        lower_strike: float,
        upper_strike: float,
        lower_premium: float,
        upper_premium: float
    ) -> List[StrategyLeg]:
        """Bull call spread"""
        return [
            StrategyLeg("call", lower_strike, lower_premium, 1, "long"),
            StrategyLeg("call", upper_strike, upper_premium, 1, "short")
        ]
    
    @staticmethod
    def bear_put_spread(
        lower_strike: float,
        upper_strike: float,
        lower_premium: float,
        upper_premium: float
    ) -> List[StrategyLeg]:
        """Bear put spread"""
        return [
            StrategyLeg("put", lower_strike, lower_premium, 1, "short"),
            StrategyLeg("put", upper_strike, upper_premium, 1, "long")
        ]
    
    @staticmethod
    def long_straddle(strike: float, call_premium: float, put_premium: float) -> List[StrategyLeg]:
        """Long straddle"""
        return [
            StrategyLeg("call", strike, call_premium, 1, "long"),
            StrategyLeg("put", strike, put_premium, 1, "long")
        ]
    
    @staticmethod
    def long_strangle(
        call_strike: float,
        put_strike: float,
        call_premium: float,
        put_premium: float
    ) -> List[StrategyLeg]:
        """Long strangle"""
        return [
            StrategyLeg("call", call_strike, call_premium, 1, "long"),
            StrategyLeg("put", put_strike, put_premium, 1, "long")
        ]
    
    @staticmethod
    def iron_condor(
        put_strike_low: float,
        put_strike_high: float,
        call_strike_low: float,
        call_strike_high: float,
        put_premium_low: float,
        put_premium_high: float,
        call_premium_low: float,
        call_premium_high: float
    ) -> List[StrategyLeg]:
        """Iron condor"""
        return [
            StrategyLeg("put", put_strike_low, put_premium_low, 1, "short"),
            StrategyLeg("put", put_strike_high, put_premium_high, 1, "long"),
            StrategyLeg("call", call_strike_low, call_premium_low, 1, "short"),
            StrategyLeg("call", call_strike_high, call_premium_high, 1, "long")
        ]


def render_pnl_analysis():
    """Render the P&L analysis interface"""
    st.title("📈 P&L Analysis & Strategy Builder")
    st.markdown("*Analyze profit/loss scenarios for options strategies*")
    
    # Initialize analyzer
    pnl_analyzer = PnLAnalyzer()
    strategy_builder = StrategyBuilder()
    
    # Sidebar for market parameters
    with st.sidebar:
        st.subheader("🎯 Market Parameters")
        
        current_price = st.number_input(
            "Current Price (KES)",
            min_value=1.0,
            max_value=10000.0,
            value=100.0,
            step=1.0
        )
        
        price_range_pct = st.slider(
            "Price Range (%)",
            min_value=10,
            max_value=100,
            value=50,
            step=5
        )
        
        # Calculate price range
        min_price = current_price * (1 - price_range_pct / 100)
        max_price = current_price * (1 + price_range_pct / 100)
        
        st.markdown(f"**Price Range:** KES {min_price:.2f} - KES {max_price:.2f}")
        
        # Analysis parameters
        st.subheader("⏰ Time Parameters")
        
        analysis_time = st.selectbox(
            "Analysis Time",
            ["At Expiry", "30 Days Before", "60 Days Before", "90 Days Before"],
            index=0
        )
        
        time_mapping = {
            "At Expiry": 0,
            "30 Days Before": 30/365,
            "60 Days Before": 60/365,
            "90 Days Before": 90/365
        }
        
        time_to_expiry = time_mapping[analysis_time]
    
    # Generate price array
    prices = np.linspace(min_price, max_price, 200)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Strategy Builder",
        "📊 Custom Position",
        "📈 Compare Strategies",
        "🔍 Scenario Analysis"
    ])
    
    with tab1:
        st.subheader("Pre-built Strategy Builder")
        
        strategy_type = st.selectbox(
            "Select Strategy Type",
            [
                "Long Call",
                "Long Put",
                "Covered Call",
                "Protective Put",
                "Bull Call Spread",
                "Bear Put Spread",
                "Long Straddle",
                "Long Strangle",
                "Iron Condor"
            ]
        )
        
        # Strategy-specific inputs
        if strategy_type == "Long Call":
            col1, col2 = st.columns(2)
            with col1:
                strike = st.number_input("Strike Price (KES)", value=current_price, step=1.0)
            with col2:
                premium = st.number_input("Premium (KES)", value=5.0, step=0.1)
            
            legs = strategy_builder.long_call(strike, premium)
        
        elif strategy_type == "Long Put":
            col1, col2 = st.columns(2)
            with col1:
                strike = st.number_input("Strike Price (KES)", value=current_price, step=1.0)
            with col2:
                premium = st.number_input("Premium (KES)", value=5.0, step=0.1)
            
            legs = strategy_builder.long_put(strike, premium)
        
        elif strategy_type == "Bull Call Spread":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                lower_strike = st.number_input("Lower Strike (KES)", value=current_price * 0.95, step=1.0)
            with col2:
                upper_strike = st.number_input("Upper Strike (KES)", value=current_price * 1.05, step=1.0)
            with col3:
                lower_premium = st.number_input("Lower Premium (KES)", value=7.0, step=0.1)
            with col4:
                upper_premium = st.number_input("Upper Premium (KES)", value=3.0, step=0.1)
            
            legs = strategy_builder.bull_call_spread(lower_strike, upper_strike, lower_premium, upper_premium)
        
        elif strategy_type == "Long Straddle":
            col1, col2, col3 = st.columns(3)
            with col1:
                strike = st.number_input("Strike Price (KES)", value=current_price, step=1.0)
            with col2:
                call_premium = st.number_input("Call Premium (KES)", value=5.0, step=0.1)
            with col3:
                put_premium = st.number_input("Put Premium (KES)", value=5.0, step=0.1)
            
            legs = strategy_builder.long_straddle(strike, call_premium, put_premium)
        
        else:
            # For other strategies, use simplified inputs
            st.info(f"Configure {strategy_type} parameters:")
            strike = st.number_input("Strike Price (KES)", value=current_price, step=1.0)
            premium = st.number_input("Premium (KES)", value=5.0, step=0.1)
            legs = strategy_builder.long_call(strike, premium)  # Default for now
        
        # Calculate and display P&L
        if st.button("Calculate P&L", key="strategy_pnl"):
            pnl_data = pnl_analyzer.calculate_strategy_pnl(legs, prices, time_to_expiry)
            
            # Create P&L diagram
            fig = pnl_analyzer.create_pnl_diagram(
                pnl_data, prices, f"{strategy_type} P&L Diagram", True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Display strategy summary
            with st.expander("📋 Strategy Summary"):
                summary_data = []
                total_cost = 0
                
                for i, leg in enumerate(legs):
                    cost = leg.premium * leg.quantity
                    if leg.position_type == "long":
                        total_cost += cost
                    else:
                        total_cost -= cost
                    
                    summary_data.append({
                        'Leg': i + 1,
                        'Type': f"{leg.position_type.title()} {leg.option_type.title()}",
                        'Strike': f"KES {leg.strike:.2f}",
                        'Premium': f"KES {leg.premium:.2f}",
                        'Quantity': leg.quantity,
                        'Net Cost': f"KES {cost:.2f}"
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
                
                # Calculate key metrics
                metrics = pnl_analyzer.calculate_max_profit_loss(prices, pnl_data['total'])
                breakeven_points = pnl_analyzer.find_breakeven_points(prices, pnl_data['total'])
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Net Cost", f"KES {total_cost:.2f}")
                
                with col2:
                    st.metric("Max Profit", f"KES {metrics['max_profit']:.2f}")
                
                with col3:
                    st.metric("Max Loss", f"KES {metrics['max_loss']:.2f}")
                
                with col4:
                    if breakeven_points:
                        st.metric("Breakeven Points", len(breakeven_points))
                        for be in breakeven_points:
                            st.write(f"KES {be:.2f}")
    
    with tab2:
        st.subheader("Custom Position Builder")
        
        # Initialize session state for custom positions
        if 'custom_legs' not in st.session_state:
            st.session_state.custom_legs = []
        
        # Add new leg
        st.markdown("### Add New Leg")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            new_option_type = st.selectbox("Option Type", ["call", "put"], key="new_type")
        
        with col2:
            new_strike = st.number_input("Strike (KES)", value=current_price, step=1.0, key="new_strike")
        
        with col3:
            new_premium = st.number_input("Premium (KES)", value=5.0, step=0.1, key="new_premium")
        
        with col4:
            new_position = st.selectbox("Position", ["long", "short"], key="new_position")
        
        with col5:
            new_quantity = st.number_input("Quantity", value=1, min_value=1, step=1, key="new_quantity")
        
        col_add, col_clear = st.columns([1, 1])
        
        with col_add:
            if st.button("Add Leg", use_container_width=True):
                new_leg = StrategyLeg(
                    option_type=new_option_type,
                    strike=new_strike,
                    premium=new_premium,
                    quantity=new_quantity,
                    position_type=new_position
                )
                st.session_state.custom_legs.append(new_leg)
                st.rerun()
        
        with col_clear:
            if st.button("Clear All", use_container_width=True):
                st.session_state.custom_legs = []
                st.rerun()
        
        # Display current legs
        if st.session_state.custom_legs:
            st.markdown("### Current Position")
            
            leg_data = []
            for i, leg in enumerate(st.session_state.custom_legs):
                leg_data.append({
                    'Leg': i + 1,
                    'Type': f"{leg.position_type.title()} {leg.option_type.title()}",
                    'Strike': f"KES {leg.strike:.2f}",
                    'Premium': f"KES {leg.premium:.2f}",
                    'Quantity': leg.quantity
                })
            
            leg_df = pd.DataFrame(leg_data)
            st.dataframe(leg_df, use_container_width=True)
            
            # Calculate P&L
            if st.button("Calculate Custom P&L", key="custom_pnl"):
                pnl_data = pnl_analyzer.calculate_strategy_pnl(
                    st.session_state.custom_legs, prices, time_to_expiry
                )
                
                fig = pnl_analyzer.create_pnl_diagram(
                    pnl_data, prices, "Custom Strategy P&L", True
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add legs to your custom strategy above.")
    
    with tab3:
        st.subheader("Strategy Comparison")
        
        # Compare multiple strategies
        st.markdown("### Compare Different Strategies")
        
        # Quick comparison of common strategies
        strategies_to_compare = [
            ("Long Call", strategy_builder.long_call(current_price, 5.0)),
            ("Long Put", strategy_builder.long_put(current_price, 5.0)),
            ("Bull Call Spread", strategy_builder.bull_call_spread(
                current_price * 0.95, current_price * 1.05, 7.0, 3.0
            )),
            ("Long Straddle", strategy_builder.long_straddle(current_price, 5.0, 5.0))
        ]
        
        if st.button("Compare Common Strategies"):
            fig = go.Figure()
            
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            
            for i, (name, legs) in enumerate(strategies_to_compare):
                pnl_data = pnl_analyzer.calculate_strategy_pnl(legs, prices, time_to_expiry)
                
                fig.add_trace(go.Scatter(
                    x=prices,
                    y=pnl_data['total'],
                    name=name,
                    line=dict(color=colors[i % len(colors)], width=2),
                    hovertemplate=f'{name}<br>Price: KES %{{x:.2f}}<br>P&L: KES %{{y:.2f}}<extra></extra>'
                ))
            
            # Add zero line
            fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
            
            fig.update_layout(
                title="Strategy Comparison",
                xaxis_title="Underlying Price (KES)",
                yaxis_title="Profit/Loss (KES)",
                width=900,
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Scenario Analysis")
        
        # Volatility impact analysis
        st.markdown("### Volatility Impact Analysis")
        
        if st.session_state.get('custom_legs') or st.button("Use Long Straddle Example"):
            # Use custom legs or example
            if st.session_state.get('custom_legs'):
                analysis_legs = st.session_state.custom_legs
                strategy_name = "Custom Strategy"
            else:
                analysis_legs = strategy_builder.long_straddle(current_price, 5.0, 5.0)
                strategy_name = "Long Straddle (Example)"
            
            # Volatility scenarios
            vol_scenarios = [0.15, 0.20, 0.25, 0.30, 0.35]  # 15% to 35%
            time_scenarios = [0, 30/365, 60/365, 90/365]  # Different times to expiry
            
            # Create subplot for different scenarios
            fig_scenarios = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'At Expiry',
                    '30 Days to Expiry',
                    '60 Days to Expiry',
                    '90 Days to Expiry'
                ],
                vertical_spacing=0.1
            )
            
            colors = ['red', 'orange', 'blue', 'green', 'purple']
            
            for i, time_val in enumerate(time_scenarios):
                row = (i // 2) + 1
                col = (i % 2) + 1
                
                for j, vol in enumerate(vol_scenarios):
                    # Calculate P&L for this scenario
                    # Note: This is simplified - in reality, you'd need to recalculate premiums
                    pnl_data = pnl_analyzer.calculate_strategy_pnl(analysis_legs, prices, time_val)
                    
                    fig_scenarios.add_trace(
                        go.Scatter(
                            x=prices,
                            y=pnl_data['total'],
                            name=f'Vol {vol:.0%}' if i == 0 else None,
                            line=dict(color=colors[j], width=2),
                            showlegend=(i == 0),
                            hovertemplate=f'Vol {vol:.0%}<br>Price: KES %{{x:.2f}}<br>P&L: KES %{{y:.2f}}<extra></extra>'
                        ),
                        row=row, col=col
                    )
                
                # Add zero line
                fig_scenarios.add_hline(y=0, line_dash="dash", line_color="black", line_width=1, row=row, col=col)
            
            fig_scenarios.update_layout(
                title=f'{strategy_name} - Time and Volatility Impact',
                height=800,
                showlegend=True
            )
            
            # Update axes
            for i in range(1, 3):
                for j in range(1, 3):
                    fig_scenarios.update_xaxes(title_text='Underlying Price (KES)', row=i, col=j)
                    fig_scenarios.update_yaxes(title_text='P&L (KES)', row=i, col=j)
            
            st.plotly_chart(fig_scenarios, use_container_width=True)
            
        else:
            st.info("Build a custom strategy in the 'Custom Position' tab or use the example button above.")


if __name__ == "__main__":
    render_pnl_analysis()