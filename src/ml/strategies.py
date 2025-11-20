"""
Strategy descriptions module

Contains detailed descriptions and educational content for various options strategies.
"""

def get_strategy_description(strategy_name: str) -> str:
    """Get detailed description for a given options trading strategy."""
    
    descriptions = {
        "Iron Condor": """
        **Iron Condor Strategy**
        
        The Iron Condor is a neutral options strategy designed to profit from low volatility.
        
        **Key Components:**
        - Sell 1 OTM put option
        - Buy 1 further OTM put option
        - Sell 1 OTM call option
        - Buy 1 further OTM call option
        
        **When to Use:**
        - Market expected to trade sideways
        - Implied volatility is high
        - You want to collect premium
        
        **Risk/Reward:**
        - Limited risk
        - Limited reward
        - Maximum profit achieved when price stays between short strikes
        """,
        
        "Covered Call": """
        **Covered Call Strategy**
        
        A covered call involves holding the underlying futures and selling a call option.
        
        **Key Components:**
        - Long futures position
        - Short call option
        
        **When to Use:**
        - Bullish to neutral market outlook
        - Want to generate income from existing positions
        - Willing to cap upside potential
        
        **Risk/Reward:**
        - Limited upside potential
        - Downside protection equal to premium received
        - Regular income generation
        """,
        
        "Long Straddle": """
        **Long Straddle Strategy**
        
        A long straddle involves buying both a call and put with the same strike and expiration.
        
        **Key Components:**
        - Buy ATM call option
        - Buy ATM put option
        
        **When to Use:**
        - Expecting significant price movement
        - Direction of movement uncertain
        - Before major market events
        
        **Risk/Reward:**
        - Unlimited profit potential
        - Limited risk to premium paid
        - Requires large price movement to profit
        """,
        
        "Calendar Spread": """
        **Calendar Spread Strategy**
        
        A calendar spread involves selling a near-term option and buying a longer-term option.
        
        **Key Components:**
        - Short near-term option
        - Long longer-term option
        
        **When to Use:**
        - Neutral market outlook
        - High near-term implied volatility
        - Expect volatility to decrease
        
        **Risk/Reward:**
        - Limited risk
        - Limited reward
        - Profits from time decay and volatility changes
        """,
    }
    
    return descriptions.get(strategy_name, "Strategy description not available.")