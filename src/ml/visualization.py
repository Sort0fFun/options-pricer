"""
ML Visualization Components

This module provides interactive visualizations for ML predictions
and market analysis using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

def create_volatility_surface(
    strikes: np.ndarray,
    expiries: np.ndarray,
    volatilities: np.ndarray,
    title: str = "Implied Volatility Surface"
) -> go.Figure:
    """Create a 3D volatility surface plot."""
    
    fig = go.Figure(data=[go.Surface(
        x=strikes,
        y=expiries,
        z=volatilities,
        colorscale='viridis'
    )])
    
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Strike Price",
            yaxis_title="Days to Expiry",
            zaxis_title="Implied Volatility"
        ),
        width=800,
        height=600
    )
    
    return fig

def create_regime_timeline(
    regimes: pd.DataFrame,
    title: str = "Market Regime Timeline"
) -> go.Figure:
    """Create a timeline visualization of market regimes."""
    
    fig = go.Figure()
    
    # Add regime blocks
    for regime in regimes.itertuples():
        fig.add_trace(go.Scatter(
            x=[regime.start_date, regime.end_date],
            y=[regime.probability, regime.probability],
            fill='tonexty',
            name=regime.regime,
            mode='lines',
            line=dict(width=0),
            fillcolor=get_regime_color(regime.regime, 0.3)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Regime Probability",
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_prediction_comparison(
    actual: pd.Series,
    predicted: pd.Series,
    confidence: pd.DataFrame,
    title: str = "ML Prediction vs Actual"
) -> go.Figure:
    """Create a comparison plot of predicted vs actual values."""
    
    fig = go.Figure()
    
    # Add actual values
    fig.add_trace(go.Scatter(
        x=actual.index,
        y=actual.values,
        name="Actual",
        line=dict(color="black", width=2)
    ))
    
    # Add predicted values with confidence interval
    fig.add_trace(go.Scatter(
        x=predicted.index,
        y=predicted.values,
        name="Predicted",
        line=dict(color="rgb(46, 139, 87)", width=2)
    ))
    
    # Add confidence interval
    fig.add_trace(go.Scatter(
        x=confidence.index.tolist() + confidence.index.tolist()[::-1],
        y=confidence['upper'].tolist() + confidence['lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(46, 139, 87, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name="95% Confidence Interval"
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Value",
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def get_regime_color(regime: str, alpha: float = 1.0) -> str:
    """Get color for market regime visualization."""
    
    colors = {
        "Low Volatility": f"rgba(46, 139, 87, {alpha})",  # seagreen
        "Normal Trading": f"rgba(30, 144, 255, {alpha})",  # dodgerblue
        "High Volatility": f"rgba(178, 34, 34, {alpha})"   # firebrick
    }
    
    return colors.get(regime, f"rgba(128, 128, 128, {alpha})")  # default gray