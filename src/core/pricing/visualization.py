"""
Components for options pricing and PnL visualization
"""

import numpy as np
import plotly.graph_objects as go
from src.visualization.styles import get_plotly_layout

def create_pnl_chart(
    futures_price: float,
    strike_price: float,
    option_type: str,
    premium: float,
    volatility: float,
    time_to_expiry: float
):
    """
    Create an interactive PnL chart for the option position.
    
    Parameters:
    -----------
    futures_price : float
        Current futures price
    strike_price : float
        Option strike price
    option_type : str
        'call' or 'put'
    premium : float
        Option premium paid/received
    volatility : float
        Implied volatility (as decimal)
    time_to_expiry : float
        Time to expiration in years
        
    Returns:
    --------
    plotly.graph_objects.Figure
        The PnL chart
    """
    # Generate price range for x-axis
    price_range = np.linspace(futures_price * 0.7, futures_price * 1.3, 100)
    
    # Calculate payoff at expiration
    if option_type.lower() == 'call':
        payoff = np.maximum(price_range - strike_price, 0) - premium
    else:
        payoff = np.maximum(strike_price - price_range, 0) - premium
    
    # Create figure
    fig = go.Figure()
    
    # Add payoff line
    fig.add_trace(go.Scatter(
        x=price_range,
        y=payoff,
        name='Payoff at Expiration',
        line=dict(color='#2C3333', width=2)
    ))
    
    # Add breakeven line
    fig.add_hline(y=0, line=dict(color='#EAEAEA', width=1, dash='dash'))
    fig.add_vline(x=futures_price, line=dict(color='#2C3333', width=1, dash='dash'))
    
    # Calculate breakeven points
    if option_type.lower() == 'call':
        breakeven = strike_price + premium
    else:
        breakeven = strike_price - premium
    
    # Update layout
    layout = get_plotly_layout(
        title="Position P&L Profile",
        xlabel="Futures Price",
        ylabel="Profit/Loss"
    )
    
    # Add annotations for key points
    annotations = [
        dict(
            x=futures_price,
            y=min(payoff) * 0.8,
            text="Current Price",
            showarrow=False,
            yanchor="top"
        ),
        dict(
            x=breakeven,
            y=0,
            text="Breakeven",
            showarrow=True,
            arrowhead=1
        )
    ]
    
    layout.update(
        showlegend=True,
        annotations=annotations,
        yaxis_zeroline=True,
        yaxis_zerolinewidth=1,
        yaxis_zerolinecolor='#EAEAEA'
    )
    
    fig.update_layout(layout)
    return fig