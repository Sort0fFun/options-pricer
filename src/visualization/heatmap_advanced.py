"""
Options Heatmap Visualization
Interactive heatmaps for options Greeks and pricing analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math

from src.core.pricing.black76 import Black76Calculator
from src.core.greeks.calculator import GreeksCalculator


class OptionsHeatmapGenerator:
    """Generate interactive heatmaps for options analysis"""
    
    def __init__(self):
        self.pricing_calculator = Black76Calculator()
        self.greeks_calculator = GreeksCalculator()
    
    def generate_strike_expiry_grid(
        self,
        current_price: float,
        risk_free_rate: float,
        volatility: float,
        strike_range: Tuple[float, float] = None,
        expiry_range: Tuple[int, int] = (1, 90),
        grid_size: Tuple[int, int] = (20, 15)
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate grid of strike prices, expiry dates, and time to expiry
        
        Args:
            current_price: Current underlying price
            risk_free_rate: Risk-free interest rate
            volatility: Implied volatility
            strike_range: (min_strike, max_strike) or None for auto
            expiry_range: (min_days, max_days) to expiry
            grid_size: (strikes, expiries) grid dimensions
            
        Returns:
            Tuple of (strikes_grid, expiries_grid, times_grid)
        """
        # Auto-generate strike range if not provided
        if strike_range is None:
            price_range = 0.3  # ±30% of current price
            min_strike = current_price * (1 - price_range)
            max_strike = current_price * (1 + price_range)
        else:
            min_strike, max_strike = strike_range
        
        # Generate strike prices and expiry days
        strikes = np.linspace(min_strike, max_strike, grid_size[0])
        expiry_days = np.linspace(expiry_range[0], expiry_range[1], grid_size[1])
        
        # Convert days to years for time parameter
        times = expiry_days / 365.0
        
        # Create meshgrids
        strikes_grid, times_grid = np.meshgrid(strikes, times)
        expiries_grid, _ = np.meshgrid(expiry_days, strikes)
        
        return strikes_grid, expiries_grid.T, times_grid
    
    def calculate_greeks_heatmap(
        self,
        current_price: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str = "call",
        **grid_params
    ) -> Dict[str, np.ndarray]:
        """
        Calculate Greeks heatmap data
        
        Returns:
            Dictionary with Greek values as 2D arrays
        """
        strikes_grid, expiries_grid, times_grid = self.generate_strike_expiry_grid(
            current_price, risk_free_rate, volatility, **grid_params
        )
        
        # Initialize result arrays
        shape = strikes_grid.shape
        greeks_data = {
            'delta': np.zeros(shape),
            'gamma': np.zeros(shape),
            'theta': np.zeros(shape),
            'vega': np.zeros(shape),
            'rho': np.zeros(shape),
            'prices': np.zeros(shape)
        }
        
        # Calculate Greeks for each point in the grid
        for i in range(shape[0]):
            for j in range(shape[1]):
                strike = strikes_grid[i, j]
                time_to_expiry = times_grid[i, j]
                
                try:
                    # Calculate option price
                    price = self.pricing_calculator.calculate_option_price(
                        S=current_price,
                        K=strike,
                        T=time_to_expiry,
                        r=risk_free_rate,
                        sigma=volatility,
                        option_type=option_type
                    )
                    
                    # Calculate Greeks
                    greeks = self.greeks_calculator.calculate_all_greeks(
                        S=current_price,
                        K=strike,
                        T=time_to_expiry,
                        r=risk_free_rate,
                        sigma=volatility,
                        option_type=option_type
                    )
                    
                    greeks_data['prices'][i, j] = price
                    greeks_data['delta'][i, j] = greeks['delta']
                    greeks_data['gamma'][i, j] = greeks['gamma']
                    greeks_data['theta'][i, j] = greeks['theta']
                    greeks_data['vega'][i, j] = greeks['vega']
                    greeks_data['rho'][i, j] = greeks['rho']
                    
                except Exception as e:
                    # Handle edge cases (e.g., very low time to expiry)
                    for key in greeks_data:
                        greeks_data[key][i, j] = np.nan
        
        # Add grid data for plotting
        greeks_data['strikes'] = strikes_grid
        greeks_data['expiries'] = expiries_grid
        greeks_data['times'] = times_grid
        
        return greeks_data
    
    def create_greeks_heatmap(
        self,
        greeks_data: Dict[str, np.ndarray],
        greek_name: str = 'delta'
    ) -> go.Figure:
        """Create interactive heatmap for a specific Greek"""
        
        # Get data for the specified Greek
        z_data = greeks_data[greek_name]
        strikes = greeks_data['strikes']
        expiries = greeks_data['expiries']
        
        # Create custom hover text
        hover_text = []
        for i in range(z_data.shape[0]):
            hover_row = []
            for j in range(z_data.shape[1]):
                hover_row.append(
                    f'Strike: KES {strikes[i,j]:.2f}<br>'
                    f'Days to Expiry: {expiries[i,j]:.0f}<br>'
                    f'{greek_name.title()}: {z_data[i,j]:.4f}<br>'
                    f'Option Price: KES {greeks_data["prices"][i,j]:.2f}'
                )
            hover_text.append(hover_row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=expiries[0, :],  # Expiry days (x-axis)
            y=strikes[:, 0],   # Strike prices (y-axis)
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            colorscale='RdYlBu_r',
            colorbar=dict(
                title=f'{greek_name.title()}',
                titleside="right"
            )
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{greek_name.title()} Heatmap',
            xaxis_title='Days to Expiry',
            yaxis_title='Strike Price (KES)',
            width=800,
            height=600,
            font=dict(size=12)
        )
        
        return fig
    
    def create_combined_greeks_heatmap(
        self,
        greeks_data: Dict[str, np.ndarray]
    ) -> go.Figure:
        """Create combined view of all Greeks"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Delta', 'Gamma', 'Theta', 'Vega'],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        greeks_to_plot = ['delta', 'gamma', 'theta', 'vega']
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        expiries = greeks_data['expiries']
        strikes = greeks_data['strikes']
        
        for greek, (row, col) in zip(greeks_to_plot, positions):
            fig.add_trace(
                go.Heatmap(
                    z=greeks_data[greek],
                    x=expiries[0, :],
                    y=strikes[:, 0],
                    colorscale='RdYlBu_r',
                    showscale=False,
                    hovertemplate=f'{greek.title()}: %{{z:.4f}}<extra></extra>'
                ),
                row=row, col=col
            )
        
        # Update layout
        fig.update_layout(
            title='Options Greeks Heatmap Overview',
            width=1000,
            height=800,
            font=dict(size=10)
        )
        
        # Update axes
        for i in range(1, 3):
            for j in range(1, 3):
                fig.update_xaxes(title_text='Days to Expiry', row=i, col=j)
                fig.update_yaxes(title_text='Strike (KES)', row=i, col=j)
        
        return fig
    
    def create_volatility_surface(
        self,
        current_price: float,
        risk_free_rate: float,
        base_volatility: float,
        option_type: str = "call"
    ) -> go.Figure:
        """Create 3D volatility surface"""
        
        # Generate volatility scenarios
        vol_range = np.linspace(0.1, 1.0, 15)  # 10% to 100% volatility
        
        # Use smaller grid for 3D surface
        strikes_grid, expiries_grid, times_grid = self.generate_strike_expiry_grid(
            current_price, risk_free_rate, base_volatility,
            grid_size=(15, 10)
        )
        
        # Calculate option prices for different volatilities
        prices_surface = np.zeros((len(vol_range), *strikes_grid.shape))
        
        for k, vol in enumerate(vol_range):
            for i in range(strikes_grid.shape[0]):
                for j in range(strikes_grid.shape[1]):
                    try:
                        price = self.pricing_calculator.calculate_option_price(
                            S=current_price,
                            K=strikes_grid[i, j],
                            T=times_grid[i, j],
                            r=risk_free_rate,
                            sigma=vol,
                            option_type=option_type
                        )
                        prices_surface[k, i, j] = price
                    except:
                        prices_surface[k, i, j] = np.nan
        
        # Create 3D surface plot
        fig = go.Figure()
        
        # Add surface for base volatility
        base_vol_idx = np.argmin(np.abs(vol_range - base_volatility))
        
        fig.add_trace(go.Surface(
            z=prices_surface[base_vol_idx],
            x=expiries_grid[0, :],
            y=strikes_grid[:, 0],
            colorscale='Viridis',
            name=f'Vol: {base_volatility:.1%}',
            hovertemplate=(
                'Strike: KES %{y:.2f}<br>'
                'Days to Expiry: %{x:.0f}<br>'
                'Option Price: KES %{z:.2f}<extra></extra>'
            )
        ))
        
        # Update layout
        fig.update_layout(
            title='Options Pricing Surface',
            scene=dict(
                xaxis_title='Days to Expiry',
                yaxis_title='Strike Price (KES)',
                zaxis_title='Option Price (KES)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            width=900,
            height=700
        )
        
        return fig


def render_heatmap_analysis():
    """Render the heatmap analysis interface"""
    st.title("🔥 Options Heatmap Analysis")
    st.markdown("*Interactive visualization of options Greeks and pricing surfaces*")
    
    # Initialize heatmap generator
    heatmap_gen = OptionsHeatmapGenerator()
    
    # Sidebar parameters
    with st.sidebar:
        st.subheader("📊 Heatmap Parameters")
        
        # Market parameters
        current_price = st.number_input(
            "Current Price (KES)",
            min_value=1.0,
            max_value=10000.0,
            value=100.0,
            step=1.0
        )
        
        risk_free_rate = st.number_input(
            "Risk-free Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.1
        ) / 100
        
        volatility = st.number_input(
            "Volatility (%)",
            min_value=1.0,
            max_value=100.0,
            value=25.0,
            step=1.0
        ) / 100
        
        option_type = st.selectbox(
            "Option Type",
            ["call", "put"],
            index=0
        )
        
        # Grid parameters
        st.subheader("🎯 Grid Settings")
        
        strike_range_pct = st.slider(
            "Strike Range (% of current price)",
            min_value=10,
            max_value=100,
            value=30,
            step=5
        ) / 100
        
        max_expiry_days = st.slider(
            "Maximum Days to Expiry",
            min_value=30,
            max_value=365,
            value=90,
            step=15
        )
        
        grid_resolution = st.select_slider(
            "Grid Resolution",
            options=['Low (15x10)', 'Medium (20x15)', 'High (25x20)'],
            value='Medium (20x15)'
        )
        
        # Parse grid resolution
        grid_sizes = {
            'Low (15x10)': (15, 10),
            'Medium (20x15)': (20, 15),
            'High (25x20)': (25, 20)
        }
        grid_size = grid_sizes[grid_resolution]
    
    # Calculate strike range
    min_strike = current_price * (1 - strike_range_pct)
    max_strike = current_price * (1 + strike_range_pct)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Individual Greeks",
        "📊 Combined View",
        "🌊 3D Surface",
        "📈 Analysis Tools"
    ])
    
    with tab1:
        st.subheader("Individual Greeks Heatmaps")
        
        # Greek selection
        selected_greek = st.selectbox(
            "Select Greek to visualize",
            ['delta', 'gamma', 'theta', 'vega', 'rho', 'prices'],
            index=0,
            format_func=lambda x: x.title() if x != 'prices' else 'Option Prices'
        )
        
        # Calculate heatmap data
        with st.spinner("Calculating Greeks heatmap..."):
            greeks_data = heatmap_gen.calculate_greeks_heatmap(
                current_price=current_price,
                risk_free_rate=risk_free_rate,
                volatility=volatility,
                option_type=option_type,
                strike_range=(min_strike, max_strike),
                expiry_range=(1, max_expiry_days),
                grid_size=grid_size
            )
        
        # Create and display heatmap
        fig = heatmap_gen.create_greeks_heatmap(greeks_data, selected_greek)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display summary statistics
        with st.expander("📊 Summary Statistics"):
            greek_values = greeks_data[selected_greek]
            valid_values = greek_values[~np.isnan(greek_values)]
            
            if len(valid_values) > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Minimum", f"{valid_values.min():.4f}")
                
                with col2:
                    st.metric("Maximum", f"{valid_values.max():.4f}")
                
                with col3:
                    st.metric("Mean", f"{valid_values.mean():.4f}")
                
                with col4:
                    st.metric("Std Dev", f"{valid_values.std():.4f}")
    
    with tab2:
        st.subheader("Combined Greeks Overview")
        
        # Use the same greeks_data if already calculated, otherwise calculate
        if 'greeks_data' not in locals():
            with st.spinner("Calculating combined Greeks heatmap..."):
                greeks_data = heatmap_gen.calculate_greeks_heatmap(
                    current_price=current_price,
                    risk_free_rate=risk_free_rate,
                    volatility=volatility,
                    option_type=option_type,
                    strike_range=(min_strike, max_strike),
                    expiry_range=(1, max_expiry_days),
                    grid_size=grid_size
                )
        
        # Create combined heatmap
        combined_fig = heatmap_gen.create_combined_greeks_heatmap(greeks_data)
        st.plotly_chart(combined_fig, use_container_width=True)
    
    with tab3:
        st.subheader("3D Volatility Surface")
        
        # Create 3D surface
        with st.spinner("Generating 3D volatility surface..."):
            surface_fig = heatmap_gen.create_volatility_surface(
                current_price=current_price,
                risk_free_rate=risk_free_rate,
                base_volatility=volatility,
                option_type=option_type
            )
        
        st.plotly_chart(surface_fig, use_container_width=True)
        
        st.info("💡 **Tip:** Click and drag to rotate the 3D surface. Use mouse wheel to zoom.")
    
    with tab4:
        st.subheader("Analysis Tools")
        
        # Scenario analysis
        st.markdown("### 📈 Scenario Analysis")
        
        if 'greeks_data' in locals():
            # Create scenario comparison
            scenarios = {
                "Current": (current_price, volatility),
                "Price +10%": (current_price * 1.1, volatility),
                "Price -10%": (current_price * 0.9, volatility),
                "Vol +5%": (current_price, volatility + 0.05),
                "Vol -5%": (current_price, volatility - 0.05)
            }
            
            scenario_results = []
            
            for scenario_name, (price, vol) in scenarios.items():
                # Calculate option price for ATM option with 30 days to expiry
                try:
                    option_price = heatmap_gen.pricing_calculator.calculate_option_price(
                        S=price,
                        K=current_price,  # ATM strike
                        T=30/365,  # 30 days
                        r=risk_free_rate,
                        sigma=vol,
                        option_type=option_type
                    )
                    
                    scenario_results.append({
                        'Scenario': scenario_name,
                        'Underlying Price': f"KES {price:.2f}",
                        'Volatility': f"{vol:.1%}",
                        'Option Price': f"KES {option_price:.2f}"
                    })
                except:
                    pass
            
            if scenario_results:
                scenario_df = pd.DataFrame(scenario_results)
                st.dataframe(scenario_df, use_container_width=True)
        
        # Risk metrics
        st.markdown("### ⚠️ Risk Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Delta Risk**: Sensitivity to underlying price changes
            - High delta = High directional risk
            - Delta hedging may be required
            """)
        
        with col2:
            st.info("""
            **Gamma Risk**: Delta stability risk
            - High gamma = Unstable delta
            - Frequent rehedging needed
            """)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.info("""
            **Theta Risk**: Time decay exposure
            - Negative theta = Losing value over time
            - Consider time to expiry carefully
            """)
        
        with col4:
            st.info("""
            **Vega Risk**: Volatility sensitivity
            - High vega = High vol risk
            - Monitor implied volatility changes
            """)


if __name__ == "__main__":
    render_heatmap_analysis()