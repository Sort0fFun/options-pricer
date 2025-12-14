"""
Educational chatbot for Kenyan options market
"""

from datetime import datetime
import streamlit as st

def initialize_chat_history():
    """Initialize the chat history and Flavia's welcome message."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm Flavia, your derivatives market specialist. "
                    "I'm here to help you understand options, futures, and derivatives trading in the NSE market. "
                    "I can explain everything from basic concepts to advanced trading strategies. "
                    "What would you like to learn about today?"
                )
            }
        ]

def show_education_page():
    """Display the options education page with AI chatbot."""
    st.title("Options Education Hub with Flavia")
    
    initialize_chat_history()
    
    # Sidebar with topic selection and Flavia's introduction
    st.sidebar.markdown("### Meet Flavia")
    st.sidebar.markdown("""
    Hi! I'm Flavia, your derivatives market specialist. I specialize in:
    - Options & Futures Trading
    - NSE Derivatives Markets
    - Complex Trading Strategies
    - Risk Management & Analysis
    - Market Mechanics & Structure
    
    Feel free to ask me anything about derivatives trading!
    """)
    
    # Topic selection below Jeff's introduction
    st.sidebar.markdown("### Topics")
    topic = st.sidebar.selectbox(
        "Select a Topic",
        [
            "Options Basics",
            "NSE Options Market",
            "Options Strategies",
            "Greeks Explained",
            "Risk Management",
            "Market Mechanics"
        ]
    )
    
    # Main chat interface with improved styling
    st.markdown(f"### {topic}")
    st.markdown("""
    <div style='background-color: #1E1E1E; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='color: #00FF00; margin: 0;'>How can I help you today?</h4>
        <p style='color: #CCCCCC; margin-top: 10px;'>
            Ask me anything about options trading, NSE markets, or specific strategies.
            I'm here to help you understand the complexities of derivatives trading!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat interface with improved styling
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar=None):
            st.markdown(message["content"])
    
    # Chat input with enhanced response generation
    if prompt := st.chat_input("Ask Flavia about derivatives trading..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Basic response generation based on keywords
        response = generate_flavia_response(prompt, topic)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Rerun to show new messages
        st.rerun()
    
    # Clear chat button with improved styling
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

def generate_flavia_response(prompt: str, topic: str) -> str:
    """Generate contextual responses based on the prompt and selected topic."""
    prompt_lower = prompt.lower()
    
    # Get current market status and news
    now = datetime.now()
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=0, second=0, microsecond=0)
    is_market_open = market_open <= now <= market_close and now.weekday() < 5
    
    # Enhanced response templates covering derivatives
    responses = {
        "Market Status": {
            "status": f"The NSE Derivatives Market is currently {'OPEN' if is_market_open else 'CLOSED'}. "
                     f"Regular trading hours are 9:30 AM to 3:00 PM EAT, Monday through Friday.",
            "news": "Latest Market Updates:\n"
                   "- NSE NEXT derivatives market shows increased activity in index futures\n"
                   "- Recent policy changes by CBK impact currency derivatives\n"
                   "- Global markets watching Fed decisions on interest rates",
        },
        "Kenyan Market": {
            "nse": "The Nairobi Securities Exchange (NSE) is East Africa's leading securities exchange. "
                  "The derivatives market (NEXT) launched in July 2019, offering futures contracts on:\n"
                  "- Individual stocks (Safaricom, KCB, Equity, EABL)\n"
                  "- NSE 25 Share Index\n"
                  "- Currency futures (USD/KES)",
            "regulations": "The NSE derivatives market is regulated by:\n"
                         "- Capital Markets Authority (CMA)\n"
                         "- NSE Clear as the central counterparty\n"
                         "Trading requires approved broker membership and proper margins.",
        },
        "Options Strategies": {
            "call": "A call option gives you the right (but not obligation) to buy an asset at a specific price (strike price). "
                   "In the NSE context, this is particularly useful for taking bullish positions on stocks like Safaricom or Equity Bank. "
                   "The potential profit is unlimited while risk is limited to the premium paid.",
            "put": "A put option gives you the right to sell an asset at a specific price. "
                  "This is commonly used as a hedging tool in the NSE market, especially for protecting equity portfolios against downside risk. "
                  "Put options are essential for risk management strategies.",
            "premium": "The option premium is what you pay to buy an option. In the NSE market, "
                      "premiums are affected by factors like volatility, time to expiry, and the underlying asset's price. "
                      "The Black-76 model is commonly used to calculate fair option premiums.",
            "strike": "The strike price is the price at which the option can be exercised. "
                     "For NSE equity options, strikes are typically set at regular intervals around the current market price. "
                     "The relationship between strike and market price determines if an option is in-the-money or out-of-the-money.",
        },
        "NSE Options Market": {
            "contract": "NSE options contracts are standardized. For stocks like Safaricom (SCOM), "
                       "each contract typically represents 100 shares. Contract specifications ensure liquidity and ease of trading.",
            "expiry": "NSE options usually expire on the last Thursday of the expiry month. "
                     "The main expiry months are March, June, September, and December. This quarterly cycle helps in strategic planning.",
            "trading": "Options trading on the NSE occurs during regular market hours (9:30 AM - 3:00 PM EAT). "
                      "All trades are cleared through the NSE derivatives clearing house for security and risk management.",
            "margin": "Trading options on NSE requires maintaining margin requirements. Initial margins are based on SPAN calculations, "
                     "while maintenance margins ensure positions can be held safely through market movements.",
        },
        "Options Strategies": {
            "covered call": "Strategy: Covered Call\n\n"
                          "Setup:\n"
                          "- Hold long position in underlying asset\n"
                          "- Sell call options against the position\n\n"
                          "Ideal Market View:\n"
                          "- Neutral to slightly bullish\n\n"
                          "Risk Profile:\n"
                          "- Limited upside potential\n"
                          "- Partial downside protection\n"
                          "- Income generation from premium\n\n"
                          "Example: Hold 100 Safaricom shares and sell 1 call option",
            
            "protective put": "Strategy: Protective Put\n\n"
                            "Setup:\n"
                            "- Hold long position in underlying asset\n"
                            "- Buy put options for protection\n\n"
                            "Ideal Market View:\n"
                            "- Bullish but want insurance\n\n"
                            "Risk Profile:\n"
                            "- Known maximum loss\n"
                            "- Unlimited upside potential\n"
                            "- Cost of protection (premium)\n\n"
                            "Example: Hold KCB shares and buy puts to protect against market decline",
            
            "spread": "Types of Option Spreads:\n\n"
                     "1. Vertical Spread:\n"
                     "   - Buy and sell options of same type, different strikes\n"
                     "   - Limited risk and reward\n"
                     "   - Examples: Bull Call Spread, Bear Put Spread\n\n"
                     "2. Calendar Spread:\n"
                     "   - Same strike, different expiration dates\n"
                     "   - Profit from time decay\n"
                     "   - Lower capital requirement\n\n"
                     "3. Diagonal Spread:\n"
                     "   - Different strikes and expiration dates\n"
                     "   - Complex risk/reward profile",
            
            "straddle": "Strategy: Long Straddle\n\n"
                       "Setup:\n"
                       "- Buy call and put at same strike\n"
                       "- Same expiration date\n\n"
                       "Ideal Market View:\n"
                       "- Expecting large move, direction unknown\n\n"
                       "Risk Profile:\n"
                       "- Limited risk (premium paid)\n"
                       "- Unlimited profit potential\n"
                       "- Needs significant move to profit\n\n"
                       "Common on NSE before major announcements",
            
            "iron condor": "Strategy: Iron Condor\n\n"
                          "Setup:\n"
                          "- Sell OTM Put Spread\n"
                          "- Sell OTM Call Spread\n\n"
                          "Ideal Market View:\n"
                          "- Neutral, expecting low volatility\n\n"
                          "Risk Profile:\n"
                          "- Limited risk and reward\n"
                          "- Profit from time decay\n"
                          "- Maximum profit if price stays between short strikes\n\n"
                          "Popular in range-bound NSE stocks",
        },
        "Futures Trading": {
            "futures": "Futures are standardized contracts to buy/sell an asset at a future date. Unlike options, futures create "
                      "an obligation rather than a right. NSE futures are cash-settled at expiry.",
            "margin": "Futures trading requires initial and maintenance margins. These are typically lower than buying the "
                     "underlying asset outright, providing leverage opportunities.",
            "rollover": "Futures positions can be rolled over to the next expiry by closing the current contract and opening "
                       "a new one. This helps maintain long-term positions.",
            "basis": "The basis is the difference between spot and futures prices. Understanding basis trends is crucial for "
                    "arbitrage opportunities and hedging strategies.",
        },
        "Risk Management": {
            "hedging": "Hedging using derivatives helps protect portfolios against adverse price movements. Common techniques include:"
                      "\n- Protective Puts for equity portfolios"
                      "\n- Covered Calls for enhanced income"
                      "\n- Delta Hedging for market neutrality",
            
            "greeks": "The Option Greeks:\n\n"
                     "1. Delta (Δ):\n"
                     "   - Measures directional risk\n"
                     "   - Range: -1.0 to +1.0\n"
                     "   - Calls: 0 to +1\n"
                     "   - Puts: -1 to 0\n"
                     "   - Used for hedge ratios\n\n"
                     "2. Gamma (Γ):\n"
                     "   - Rate of delta change\n"
                     "   - Highest near strike price\n"
                     "   - Important for dynamic hedging\n"
                     "   - Always positive for long options\n\n"
                     "3. Theta (Θ):\n"
                     "   - Time decay rate\n"
                     "   - Usually negative for buyers\n"
                     "   - Highest for at-the-money options\n"
                     "   - Accelerates near expiration\n\n"
                     "4. Vega (v):\n"
                     "   - Volatility sensitivity\n"
                     "   - Important for NSE's volatile stocks\n"
                     "   - Higher for longer-dated options\n"
                     "   - Key for volatility strategies\n\n"
                     "5. Rho (ρ):\n"
                     "   - Interest rate sensitivity\n"
                     "   - Important for longer-dated options\n"
                     "   - Affected by CBK rate decisions",
            "volatility": "Volatility is a key factor in options pricing. Historical volatility measures past price movements, "
                         "while implied volatility reflects market expectations of future movements.",
        }
    }
    
    # Default response if no specific match is found
    default_response = (
        "I understand you're asking about " + topic.lower() + ". "
        "Could you please be more specific about what aspect you'd like to learn? "
        "For example, you can ask about:\n\n"
        "- Basic concepts and definitions\n"
        "- Practical trading strategies\n"
        "- Risk management techniques\n"
        "- NSE-specific rules and guidelines"
    )
    
    # Check for topic-specific responses
    topic_responses = responses.get(topic, {})
    for keyword, response in topic_responses.items():
        if keyword in prompt_lower:
            return response
    
    # Return default response if no specific match
    return default_response