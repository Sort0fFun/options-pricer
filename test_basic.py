#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic test to verify core functionality works
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_basic_pricing():
    """Test basic pricing functionality"""
    try:
        from src.core.pricing.black76 import Black76Pricer
        print("✅ Black76Pricer imported successfully")
        
        # Create pricer
        pricer = Black76Pricer()
        print("✅ Black76Pricer initialized")
        
        # Test basic call pricing
        call_price = pricer.price_call(
            futures_price=100.0,
            strike_price=105.0,
            time_to_expiry=0.25,
            volatility=0.20,
            risk_free_rate=0.10
        )
        print("Call option price: KES {:.4f}".format(call_price))
        
        # Test basic put pricing
        put_price = pricer.price_put(
            futures_price=100.0,
            strike_price=105.0,
            time_to_expiry=0.25,
            volatility=0.20,
            risk_free_rate=0.10
        )
        print("Put option price: KES {:.4f}".format(put_price))
        
        return True
        
    except Exception as e:
        print("Error in pricing test: {}".format(e))
        return False

def test_streamlit_imports():
    """Test if Streamlit app can import dependencies"""
    try:
        import streamlit as st
        print("✅ Streamlit imported")
        
        import pandas as pd
        print("✅ Pandas imported")
        
        import numpy as np
        print("✅ NumPy imported")
        
        import plotly.graph_objects as go
        print("✅ Plotly imported")
        
        return True
        
    except Exception as e:
        print("Error in Streamlit imports: {}".format(e))
        return False

def test_app_structure():
    """Test if app.py can be imported"""
    try:
        # Check if app.py exists and is readable
        with open('app.py', 'r') as f:
            content = f.read()
            
        if 'st.set_page_config' in content:
            print("✅ App.py structure looks good")
            return True
        else:
            print("❌ App.py missing key components")
            return False
            
    except Exception as e:
        print("Error reading app.py: {}".format(e))
        return False

if __name__ == "__main__":
    print("🧪 Running basic functionality tests...\n")
    
    success = True
    
    print("📊 Testing Pricing Engine...")
    if not test_basic_pricing():
        success = False
    
    print("\n🌐 Testing Streamlit Dependencies...")
    if not test_streamlit_imports():
        success = False
    
    print("\n📱 Testing App Structure...")
    if not test_app_structure():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 All tests passed! Application should work correctly.")
        print("\n💡 To run the app:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    print("="*50)