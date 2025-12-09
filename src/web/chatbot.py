"""
Flavia AI Chatbot - NSE Options Trading Assistant
Specialized ChatGPT-powered assistant for Kenyan securities market
"""

import streamlit as st
from openai import OpenAI
from typing import List, Dict, Optional
import json
from datetime import datetime
import pandas as pd

class FlaviaAIBot:
    """
    Flavia - AI-powered NSE Options Trading Assistant
    Specialized in Kenyan securities market, NSE options, and futures trading
    """

    # Hardcoded API key
    DEFAULT_API_KEY = "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"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Flavia with OpenAI API key"""
        self.api_key = api_key or self.DEFAULT_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
        # Flavia's personality and expertise
        self.system_prompt = """
        You are Flavia, an AI expert specializing in the Nairobi Securities Exchange (NSE) 
        and options trading on NSE futures. You are knowledgeable, professional, and helpful.
        
        Your expertise includes:
        - NSE futures contracts and options pricing
        - Black-76 model for commodity options
        - Kenyan securities market regulations and trading hours
        - Risk management and options strategies
        - Greek sensitivities (Delta, Gamma, Theta, Vega)
        - Volatility analysis and forecasting
        - Market timing and regime detection
        
        Your personality:
        - Professional yet approachable
        - Clear and educational in explanations
        - Focused on practical trading insights
        - Risk-aware and conservative in recommendations
        - Knowledgeable about NSE-specific nuances
        
        Always provide actionable insights while emphasizing proper risk management.
        Use Kenyan Shilling (KES) for pricing when relevant.
        Reference NSE trading hours (9:00 AM - 3:00 PM EAT) when discussing market timing.
        """
        
        # Initialize conversation history
        if 'flavia_history' not in st.session_state:
            st.session_state.flavia_history = []
    
    def get_market_context(self) -> str:
        """Get current market context for better responses"""
        current_time = datetime.now()
        
        # NSE trading hours: 9:00 AM - 3:00 PM EAT (UTC+3)
        nse_open = current_time.replace(hour=9, minute=0, second=0)
        nse_close = current_time.replace(hour=15, minute=0, second=0)
        
        market_status = "OPEN" if nse_open <= current_time <= nse_close else "CLOSED"
        
        context = f"""
        Current Market Context:
        - Date: {current_time.strftime('%Y-%m-%d')}
        - Time: {current_time.strftime('%H:%M EAT')}
        - NSE Status: {market_status}
        - Trading Hours: 9:00 AM - 3:00 PM EAT
        """
        
        return context
    
    def get_options_context(self) -> str:
        """Get current options pricing context from the app"""
        context_data = []
        
        # Try to get current pricing data from session state
        if 'current_option_data' in st.session_state:
            data = st.session_state.current_option_data
            context_data.append(f"Current Analysis: {data.get('underlying', 'N/A')}")
            context_data.append(f"Strike: KES {data.get('strike', 'N/A')}")
            context_data.append(f"Call Price: KES {data.get('call_price', 'N/A'):.2f}")
            context_data.append(f"Put Price: KES {data.get('put_price', 'N/A'):.2f}")
        
        return "\n".join(context_data) if context_data else "No current options data available."
    
    def chat_with_flavia(self, user_message: str) -> str:
        """Send message to Flavia and get response"""
        if not self.client:
            return "⚠️ OpenAI API key not configured. Please add your API key to use Flavia."

        try:
            # Prepare conversation context
            market_context = self.get_market_context()
            options_context = self.get_options_context()

            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"Market Context:\n{market_context}"},
                {"role": "system", "content": f"Options Context:\n{options_context}"}
            ]

            # Add conversation history (last 10 messages to manage token limits)
            recent_history = st.session_state.flavia_history[-10:] if st.session_state.flavia_history else []
            for msg in recent_history:
                messages.append(msg)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Get response from OpenAI (new API format)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                top_p=0.9
            )

            flavia_response = response.choices[0].message.content
            
            # Update conversation history
            st.session_state.flavia_history.append({"role": "user", "content": user_message})
            st.session_state.flavia_history.append({"role": "assistant", "content": flavia_response})
            
            return flavia_response
            
        except Exception as e:
            return f"⚠️ Error communicating with Flavia: {str(e)}"
    
    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions for users"""
        return [
            "What are the current NSE trading hours?",
            "Explain options Greeks in simple terms",
            "How does volatility affect options pricing?",
            "What's the difference between American and European options?",
            "Can you explain the Black-76 model for commodity options?",
            "What are some basic options trading strategies?",
            "How do I manage risk when trading options?",
            "What factors affect NSE futures pricing?",
            "When is the best time to trade options?",
            "How do interest rates affect options prices?"
        ]
    
    def clear_conversation(self):
        """Clear conversation history"""
        st.session_state.flavia_history = []
    
    def export_conversation(self) -> str:
        """Export conversation as JSON"""
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "conversation": st.session_state.flavia_history
        }
        return json.dumps(conversation_data, indent=2)


def render_flavia_chat():
    """Render the Flavia chatbot interface"""
    st.title("💬 Chat with Flavia")
    st.markdown("*Your AI assistant for NSE options trading and Kenyan securities market*")

    # Initialize Flavia with hardcoded API key
    flavia = FlaviaAIBot()
    
    # Chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Conversation")
        
        # Display conversation history
        chat_container = st.container()
        with chat_container:
            if st.session_state.flavia_history:
                for i, message in enumerate(st.session_state.flavia_history):
                    if message["role"] == "user":
                        st.markdown(f"**You:** {message['content']}")
                    else:
                        st.markdown(f"**Flavia:** {message['content']}")
                    
                    if i < len(st.session_state.flavia_history) - 1:
                        st.markdown("---")
            else:
                st.info("👋 Hi! I'm Flavia, your NSE options trading assistant. Ask me anything about options trading, market analysis, or Kenyan securities!")
        
        # Message input
        user_message = st.text_input(
            "Ask Flavia a question:",
            placeholder="e.g., How does volatility affect my call options?",
            key="flavia_input"
        )
        
        col_send, col_clear = st.columns([1, 1])

        with col_send:
            if st.button("Send 📤", use_container_width=True) and user_message:
                with st.spinner("Flavia is thinking..."):
                    flavia.chat_with_flavia(user_message)
                st.rerun()
        
        with col_clear:
            if st.button("Clear Chat 🗑️", use_container_width=True):
                flavia.clear_conversation()
                st.rerun()
    
    with col2:
        st.subheader("Quick Questions")
        
        suggested_questions = flavia.get_suggested_questions()
        
        for question in suggested_questions:
            if st.button(question, key=f"suggest_{hash(question)}", use_container_width=True):
                with st.spinner("Flavia is thinking..."):
                    flavia.chat_with_flavia(question)
                st.rerun()
        
        # Export conversation
        if st.session_state.flavia_history:
            st.markdown("---")
            st.subheader("Export")
            
            if st.button("💾 Export Chat", use_container_width=True):
                conversation_json = flavia.export_conversation()
                st.download_button(
                    "📄 Download JSON",
                    conversation_json,
                    file_name=f"flavia_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    use_container_width=True
                )


if __name__ == "__main__":
    render_flavia_chat()