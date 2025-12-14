"""
UI Components for the NSE Options Pricing Tool

This module provides reusable UI components with consistent styling.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List


def create_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None,
    card_type: str = "default"
) -> None:
    """
    Create a styled metric card.
    
    Args:
        title: Card title
        value: Main value to display
        delta: Optional delta value
        delta_color: Color of delta (normal, inverse)
        help_text: Optional help text
        card_type: Type of card (default, call, put, success, warning, error)
    """
    card_classes = {
        "call": "call-option",
        "put": "put-option",
        "success": "success-card",
        "warning": "warning-card",
        "error": "error-card"
    }
    
    card_class = card_classes.get(card_type, "")
    
    if card_class:
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )
    
    if card_class:
        st.markdown('</div>', unsafe_allow_html=True)


def create_chart_container(chart, title: Optional[str] = None) -> None:
    """
    Create a styled container for charts.
    
    Args:
        chart: Plotly chart object
        title: Optional chart title
    """
    if title:
        st.markdown(f"#### {title}")
    
    st.plotly_chart(chart, use_container_width=True)


def create_sidebar_section(title: str, content_func, expanded: bool = True) -> None:
    """
    Create a collapsible sidebar section.
    
    Args:
        title: Section title
        content_func: Function that renders the section content
        expanded: Whether section starts expanded
    """
    with st.expander(title, expanded=expanded):
        content_func()


def create_info_box(
    message: str,
    box_type: str = "info",
    title: Optional[str] = None
) -> None:
    """
    Create an information box.
    
    Args:
        message: Message to display
        box_type: Type of box (info, success, warning, error)
        title: Optional title
    """
    icons = {
        "info": "[i]",
        "success": "[ok]",
        "warning": "[!]",
        "error": "[x]"
    }
    
    colors = {
        "info": "#17a2b8",
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545"
    }
    
    icon = icons.get(box_type, "[i]")
    color = colors.get(box_type, "#17a2b8")
    
    title_html = f"<strong>{title}</strong><br>" if title else ""
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}20, {color}10);
        border: 1px solid {color};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    ">
        {icon} {title_html}{message}
    </div>
    """, unsafe_allow_html=True)


def create_status_indicator(
    status: str,
    label: str,
    description: Optional[str] = None
) -> None:
    """
    Create a status indicator.
    
    Args:
        status: Status value (OPEN, CLOSED, etc.)
        label: Status label
        description: Optional description
    """
    colors = {
        "OPEN": "#28a745",
        "CLOSED": "#dc3545",
        "PENDING": "#ffc107"
    }
    
    color = colors.get(status, "#6c757d")
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}20, {color}10);
        border: 1px solid {color};
        border-radius: 6px;
        padding: 0.75rem;
        text-align: center;
        margin-bottom: 1rem;
    ">
        <div style="color: {color}; font-weight: 600; font-size: 1.1rem;">
            {label}: {status}
        </div>
        {f'<div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.25rem;">{description}</div>' if description else ''}
    </div>
    """, unsafe_allow_html=True)


def create_feature_card(
    icon: str,
    title: str,
    description: str,
    metric_value: Optional[str] = None
) -> None:
    """
    Create a feature showcase card.
    
    Args:
        icon: Emoji or icon
        title: Feature title
        description: Feature description
        metric_value: Optional metric value
    """
    metric_html = f'<h2 style="margin: 0.5rem 0; color: var(--primary-color);">{metric_value}</h2>' if metric_value else ''
    
    st.markdown(f"""
    <div style="
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <h4 style="margin: 0; color: var(--primary-color);">{title}</h4>
        {metric_html}
        <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">{description}</p>
    </div>
    """, unsafe_allow_html=True)


def create_quick_action_button(
    label: str,
    icon: str,
    description: str,
    key: str
) -> bool:
    """
    Create a quick action button.
    
    Args:
        label: Button label
        icon: Button icon
        description: Button description
        key: Unique key for the button
        
    Returns:
        True if button was clicked
    """
    return st.button(
        f"{icon} {label}",
        key=key,
        help=description,
        use_container_width=True
    )


def create_data_table(
    data: Dict[str, List],
    title: Optional[str] = None,
    highlight_columns: Optional[List[str]] = None
) -> None:
    """
    Create a styled data table.
    
    Args:
        data: Dictionary of data
        title: Optional table title
        highlight_columns: Columns to highlight
    """
    import pandas as pd
    
    if title:
        st.markdown(f"#### {title}")
    
    df = pd.DataFrame(data)
    
    # Style the dataframe if highlight columns are specified
    if highlight_columns:
        def highlight_cols(s):
            return ['background-color: var(--primary-color); color: white' 
                   if s.name in highlight_columns else '' for _ in s]
        
        styled_df = df.style.apply(highlight_cols, axis=0)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)


def create_loading_spinner(message: str = "Loading...") -> None:
    """
    Create a loading spinner with message.
    
    Args:
        message: Loading message
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="
            border: 3px solid var(--border-color);
            border-radius: 50%;
            border-top: 3px solid var(--primary-color);
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem auto;
        "></div>
        <p style="color: var(--text-secondary);">{message}</p>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)