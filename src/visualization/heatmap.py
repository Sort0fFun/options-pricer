"""
Heatmap visualization utilities for options analysis.
"""

import numpy as np
import plotly.graph_objects as go
from .styles import get_plotly_layout

def create_sensitivity_heatmap(
    x_values, 
    y_values, 
    z_values, 
    x_label, 
    y_label, 
    title,
    colorscale='RdBu'
):
    """
    Create a heatmap showing sensitivity analysis of option parameters.
    
    Parameters:
    -----------
    x_values : array-like
        Values for x-axis
    y_values : array-like
        Values for y-axis
    z_values : 2D array
        Matrix of values for the heatmap
    x_label : str
        Label for x-axis
    y_label : str
        Label for y-axis
    title : str
        Title of the heatmap
    colorscale : str, optional
        Plotly colorscale to use (default: 'RdBu')
    
    Returns:
    --------
    plotly.graph_objects.Figure
        The heatmap figure
    """
    fig = go.Figure(data=go.Heatmap(
        x=x_values,
        y=y_values,
        z=z_values,
        colorscale=colorscale,
        colorbar=dict(
            title=dict(
                text="Value",
                side="right"
            )
        )
    ))
    
    # Apply consistent styling
    layout = get_plotly_layout(title, x_label, y_label)
    layout.update(dict(
        xaxis=dict(
            title=x_label,
            gridcolor='#EAEAEA',
            showgrid=False,
            side='bottom'
        ),
        yaxis=dict(
            title=y_label,
            gridcolor='#EAEAEA',
            showgrid=False
        )
    ))
    
    fig.update_layout(layout)
    return fig