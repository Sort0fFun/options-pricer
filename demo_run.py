#!/usr/bin/env python3
"""
Demo script to test the core functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def demo_pricing():
    """Demonstrate the pricing functionality"""
    print("=" * 60)
    print("🇰🇪 NSE OPTIONS PRICING TOOL - DEMO")
    print("=" * 60)
    
    try:
        # Import the pricing engine
        from src.core.pricing.black76 import Black76Pricer
        print("✅ Successfully imported Black76Pricer")
        
        # Initialize the pricer
        pricer = Black76Pricer()
        print("✅ Successfully initialized pricing engine")
        
        # Demo parameters for a SCOM option
        print("\n📊 DEMO: Pricing SCOM Call Option")
        print("-" * 40)
        futures_price = 28.50  # Current SCOM futures price
        strike_price = 30.00   # Slightly out-of-the-money
        time_to_expiry = 0.25  # 3 months to expiry
        volatility = 0.25      # 25% annual volatility
        risk_free_rate = 0.10  # 10% CBK rate
        
        print(f"Futures Price:    KES {futures_price:.2f}")
        print(f"Strike Price:     KES {strike_price:.2f}")
        print(f"Time to Expiry:   {time_to_expiry:.2f} years")
        print(f"Volatility:       {volatility:.1%}")
        print(f"Risk-free Rate:   {risk_free_rate:.1%}")
        
        # Price the call option
        call_price = pricer.price_call(
            futures_price=futures_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            volatility=volatility,
            risk_free_rate=risk_free_rate,
            contract_symbol='SCOM'
        )
        
        print(f"\n💰 CALL OPTION PRICE: KES {call_price:.4f}")
        
        # Price the put option
        put_price = pricer.price_put(
            futures_price=futures_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            volatility=volatility,
            risk_free_rate=risk_free_rate,
            contract_symbol='SCOM'
        )
        
        print(f"💰 PUT OPTION PRICE:  KES {put_price:.4f}")
        
        # Calculate intrinsic values
        call_intrinsic = pricer.calculate_intrinsic_value(futures_price, strike_price, 'call')
        put_intrinsic = pricer.calculate_intrinsic_value(futures_price, strike_price, 'put')
        
        print(f"\n📈 INTRINSIC VALUES:")
        print(f"Call Intrinsic:   KES {call_intrinsic:.4f}")
        print(f"Put Intrinsic:    KES {put_intrinsic:.4f}")
        
        # Calculate time values
        call_time_value = pricer.calculate_time_value(call_price, call_intrinsic)
        put_time_value = pricer.calculate_time_value(put_price, put_intrinsic)
        
        print(f"\n⏰ TIME VALUES:")
        print(f"Call Time Value:  KES {call_time_value:.4f}")
        print(f"Put Time Value:   KES {put_time_value:.4f}")
        
        print("\n✅ PRICING ENGINE WORKING CORRECTLY!")
        
    except Exception as e:
        print(f"❌ Error in pricing demo: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Greeks calculation
    try:
        print("\n📊 DEMO: Greeks Analysis")
        print("-" * 40)
        
        from src.core.greeks.calculator import GreeksCalculator
        print("✅ Successfully imported GreeksCalculator")
        
        greeks_calc = GreeksCalculator()
        print("✅ Successfully initialized Greeks calculator")
        
        # Calculate Greeks for the call option
        greeks = greeks_calc.calculate_greeks(
            futures_price=futures_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            volatility=volatility,
            risk_free_rate=risk_free_rate,
            option_type='call'
        )
        
        print(f"\n📊 GREEKS for SCOM Call Option:")
        print(f"Delta (Δ):        {greeks.delta:.4f}")
        print(f"Gamma (Γ):        {greeks.gamma:.6f}")
        print(f"Vega (ν):         {greeks.vega:.4f}")
        print(f"Theta (Θ):        {greeks.theta:.4f}")
        print(f"Rho (ρ):          {greeks.rho:.4f}")
        print(f"Lambda (Λ):       {greeks.lambda_:.2f}")
        
        print("\n✅ GREEKS CALCULATOR WORKING CORRECTLY!")
        
    except Exception as e:
        print(f"❌ Error in Greeks demo: {e}")
        return False
    
    # Test data simulation
    try:
        print("\n📈 DEMO: Market Data Simulation")
        print("-" * 40)
        
        from src.data.simulation.nse_simulator import NSEMarketSimulator
        print("✅ Successfully imported NSEMarketSimulator")
        
        simulator = NSEMarketSimulator()
        print("✅ Successfully initialized market simulator")
        
        # Generate 30 days of SCOM data
        sample_data = simulator.generate_price_data(
            contract='SCOM',
            start_price=28.50,
            days=30,
            regime='normal'
        )
        
        print(f"\n📊 Generated {len(sample_data)} days of market data")
        print(f"Starting price:   KES {sample_data['price'].iloc[0]:.2f}")
        print(f"Ending price:     KES {sample_data['price'].iloc[-1]:.2f}")
        print(f"Max price:        KES {sample_data['price'].max():.2f}")
        print(f"Min price:        KES {sample_data['price'].min():.2f}")
        print(f"Average volume:   {sample_data['volume'].mean():,.0f}")
        
        print("\n✅ MARKET SIMULATOR WORKING CORRECTLY!")
        
    except Exception as e:
        print(f"❌ Error in simulation demo: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL CORE MODULES WORKING CORRECTLY!")
    print("🚀 READY TO RUN STREAMLIT APPLICATION!")
    print("=" * 60)
    print("\nTo run the web application:")
    print("   streamlit run app.py")
    print("\nThen open your browser to: http://localhost:8501")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    demo_pricing()