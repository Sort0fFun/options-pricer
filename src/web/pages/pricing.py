def show_pricing_page():
    """Display the main options pricing page."""
    st.title("Options Pricing")
    
    if not MODULES_AVAILABLE:
        st.error("Pricing modules not available. Please check installation.")
        return
    
    # Get inputs from session state
    inputs = st.session_state.pricing_inputs
    if not inputs:
        st.warning("Please select a contract and enter parameters in the sidebar.")
        return
    
    # Create columns for the layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Option Pricing Section
        st.subheader("Option Price Calculator")
        
        # Calculate option price
        price = Black76Pricer.price_option(
            futures_price=inputs['futures_price'],
            strike_price=inputs['strike_price'],
            time_to_expiry=inputs['time_to_expiry'] / 365.25,
            volatility=inputs['volatility'],
            risk_free_rate=0.10,  # Kenya 10Y Bond rate (approximate)
            option_type=inputs['option_type'].lower()
        )
        
        # Display option details
        st.metric(
            "Option Premium",
            format_currency(price),
            delta=f"Per {inputs['contract_specs']['contract_size']} shares"
        )
        
        # Display contract specifications
        st.markdown("### Contract Details")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Contract", f"{inputs['contract']}")
            st.metric("Option Type", inputs['option_type'])
            st.metric("Strike Price", format_currency(inputs['strike_price']))
        with col_b:
            st.metric("Futures Price", format_currency(inputs['futures_price']))
            st.metric("Days to Expiry", f"{inputs['time_to_expiry']} days")
            st.metric("Volatility", f"{inputs['volatility']*100:.1f}%")
        
        # Total cost
        total_cost = price * inputs['contract_specs']['contract_size']
        st.metric(
            "Total Position Cost",
            format_currency(total_cost),
            delta="Including contract size"
        )
    
    with col2:
        # PnL Chart Section
        from src.core.pricing.visualization import create_pnl_chart
        
        fig = create_pnl_chart(
            futures_price=inputs['futures_price'],
            strike_price=inputs['strike_price'],
            option_type=inputs['option_type'].lower(),
            premium=price,
            volatility=inputs['volatility'],
            time_to_expiry=inputs['time_to_expiry'] / 365.25
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Quick Actions
        st.markdown("### Quick Actions")
        col_x, col_y = st.columns(2)
        
        with col_x:
            if st.button("Analyze Greeks", use_container_width=True):
                st.session_state.page = "Greeks Analysis"
                
        with col_y:
            if st.button("View Strategies", use_container_width=True):
                st.session_state.page = "Strategy Builder"