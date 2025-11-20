#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to verify core functionality works
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_basic_pricing():
    """Test basic pricing functionality"""
    try:
        from src.core.pricing.black76 import Black76Pricer
        print("SUCCESS: Black76Pricer imported successfully")
        
        # Create pricer
        pricer = Black76Pricer()
        print("SUCCESS: Black76Pricer initialized")
        
        # Test basic call pricing
        call_price = pricer.price_call(
            futures_price=100.0,
            strike_price=105.0,
            time_to_expiry=0.25,
            volatility=0.20,
            risk_free_rate=0.10
        )
        print("SUCCESS: Call option price: KES {:.4f}".format(call_price))
        
        # Test basic put pricing
        put_price = pricer.price_put(
            futures_price=100.0,
            strike_price=105.0,
            time_to_expiry=0.25,
            volatility=0.20,
            risk_free_rate=0.10
        )
        print("SUCCESS: Put option price: KES {:.4f}".format(put_price))
        
        return True
        
    except Exception as e:
        print("ERROR in pricing test: {}".format(e))
        return False

def test_streamlit_imports():
    """Test if Streamlit app can import dependencies"""
    try:
        import streamlit as st
        print("SUCCESS: Streamlit imported")
        
        import pandas as pd
        print("SUCCESS: Pandas imported")
        
        import numpy as np
        print("SUCCESS: NumPy imported")
        
        import plotly.graph_objects as go
        print("SUCCESS: Plotly imported")
        
        return True
        
    except Exception as e:
        print("ERROR in Streamlit imports: {}".format(e))
        return False

if __name__ == "__main__":
    print("Running basic functionality tests...")
    print("")
    
    success = True
    
    print("Testing Pricing Engine...")
    if not test_basic_pricing():
        success = False
    
    print("")
    print("Testing Streamlit Dependencies...")
    if not test_streamlit_imports():
        success = False
    
    print("")
    print("=" * 50)
    if success:
        print("SUCCESS: All tests passed! Application should work correctly.")
        print("")
        print("To run the app:")
        print("   streamlit run app.py")
    else:
        print("WARNING: Some tests failed. Please check the errors above.")
    print("=" * 50)