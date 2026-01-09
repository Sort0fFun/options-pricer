"""
Chatbot service - Flavia AI for Flask (without Streamlit dependencies).
"""
import os
from openai import OpenAI
from datetime import datetime
import pytz
from typing import List


class ChatbotService:
    """Service for Flavia AI chatbot interactions."""

    def __init__(self):
        """Initialize chatbot with OpenAI API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.conversation_history = []

        # Flavia's system prompt
        self.system_prompt = """
You are Flavia, an expert AI assistant specializing in:
- Nairobi Securities Exchange (NSE) options and futures trading
- Options pricing models (Black-76, Black-Scholes)
- Risk management and hedging strategies
- Kenyan securities market regulations and practices
- Technical analysis and market trends

You provide clear, accurate, and professional advice on options trading,
helping users understand complex financial concepts in simple terms.

Current market hours: NSE trading hours are 9:00 AM to 3:00 PM EAT (East Africa Time), Monday to Friday.
"""

    def send_message(self, message: str, context: dict = None) -> dict:
        """
        Send message to Flavia AI and get response.

        Args:
            message: User message
            context: Optional context (pricing data, market status, etc.)

        Returns:
            dict: Response from Flavia AI
        """
        try:
            # Build messages
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add conversation history
            messages.extend(self.conversation_history)

            # Add context if provided
            if context:
                context_message = self._format_context(context)
                messages.append({"role": "system", "content": f"Current context: {context_message}"})

            # Add user message
            messages.append({"role": "user", "content": message})

            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            assistant_message = response.choices[0].message.content

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            # Keep only last 10 exchanges (20 messages)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return {
                'response': assistant_message,
                'timestamp': self._get_timestamp(),
                'model': 'gpt-4o-mini',
                'tokens_used': response.usage.total_tokens
            }

        except Exception as e:
            return {
                'response': f"I apologize, but I encountered an error: {str(e)}",
                'timestamp': self._get_timestamp(),
                'model': 'gpt-4o-mini',
                'error': True
            }

    def get_suggestions(self) -> List[str]:
        """
        Get suggested questions.

        Returns:
            list: List of suggested questions
        """
        return [
            "What are the current NSE trading hours?",
            "How does volatility affect option prices?",
            "Explain the Black-76 pricing model",
            "What's the difference between call and put options?",
            "How do I calculate option Greeks?",
            "What is implied volatility?",
            "Explain bull call spread strategy",
            "What factors affect option premiums?",
            "How does time decay work in options?",
            "What is the risk-free rate in Kenya?"
        ]

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []

    @staticmethod
    def _format_context(context: dict) -> str:
        """Format context dictionary into readable string."""
        parts = []
        if 'futures_price' in context:
            parts.append(f"Futures Price: KES {context['futures_price']}")
        if 'strike_price' in context:
            parts.append(f"Strike: KES {context['strike_price']}")
        if 'option_type' in context:
            parts.append(f"Option Type: {context['option_type']}")
        return ", ".join(parts) if parts else "No additional context"

    @staticmethod
    def _get_timestamp():
        """Get current timestamp in ISO format."""
        tz = pytz.timezone('Africa/Nairobi')
        return datetime.now(tz).isoformat()
