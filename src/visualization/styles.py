"""
Styling utilities for plots and visualizations
"""

def get_plotly_layout(title, xlabel, ylabel, height=None, width=None, **kwargs):
    """
    Get consistent Plotly layout styling.
    
    Args:
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        height: Optional plot height in pixels
        width: Optional plot width in pixels
        **kwargs: Additional layout parameters
    """
    layout = dict(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=16)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title=xlabel,
            gridcolor='#EAEAEA',
            zerolinecolor='#EAEAEA',
            showline=True,
            linewidth=1,
            linecolor='#EAEAEA',
            tickformat=",.2f"
        ),
        yaxis=dict(
            title=ylabel,
            gridcolor='#EAEAEA',
            zerolinecolor='#EAEAEA',
            showline=True,
            linewidth=1,
            linecolor='#EAEAEA',
            tickformat=".1f"
        ),
        showlegend=True,
        legend=dict(
            yanchor="bottom",
            y=0.01,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        margin=dict(t=60, b=40, l=60, r=60),
        font=dict(
            family="Inter, sans-serif",
            color="#2C3333",
            size=12
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter, sans-serif"
        )
    )
    
    if height:
        layout['height'] = height
    if width:
        layout['width'] = width
        
    # Update with any additional kwargs
    layout.update(kwargs)
    
    return layout