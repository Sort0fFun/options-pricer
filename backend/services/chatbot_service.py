"""
Chatbot service - Flavia AI for Flask (without Streamlit dependencies).
"""
import os
from openai import OpenAI
from datetime import datetime
import pytz
from typing import List, Optional, Dict, Any
from bson import ObjectId
import uuid


class ChatbotService:
    """Service for Flavia AI chatbot interactions."""
    
    _mongo = None
    _initialized = False

    def __init__(self, user_id: Optional[str] = None, session_id: Optional[str] = None):
        """Initialize chatbot with OpenAI API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.user_id = user_id
        self.session_id = session_id
        self.conversation_history = []
        
        # Load existing session if provided
        if user_id and session_id:
            self._load_session()

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

    @classmethod
    def init_app(cls, mongo):
        """Initialize with MongoDB instance."""
        cls._mongo = mongo
        cls._initialized = False
    
    @classmethod
    def _ensure_indexes(cls):
        """Ensure necessary indexes exist."""
        if cls._mongo is not None and not cls._initialized:
            try:
                cls._mongo.db.chat_sessions.create_index('user_id')
                cls._mongo.db.chat_sessions.create_index('created_at')
                cls._mongo.db.chat_sessions.create_index([('user_id', 1), ('is_active', 1)])
                cls._initialized = True
            except Exception as e:
                print(f"Warning: Could not create chat indexes: {e}")
    
    @classmethod
    def _get_sessions_collection(cls):
        """Get chat sessions collection."""
        if cls._mongo is None:
            raise RuntimeError("ChatbotService not initialized. Call init_app first.")
        cls._ensure_indexes()
        return cls._mongo.db.chat_sessions
    
    def _load_session(self):
        """Load existing chat session from database."""
        if not self.user_id or not self.session_id:
            return
        
        sessions = self._get_sessions_collection()
        session = sessions.find_one({
            '_id': self.session_id,
            'user_id': self.user_id
        })
        
        if session:
            # Load message history
            self.conversation_history = [
                {"role": msg['role'], "content": msg['content']}
                for msg in session.get('messages', [])
                if msg['role'] in ['user', 'assistant']
            ]
    
    def _save_session(self, user_message: str, assistant_message: str, tokens_used: int):
        """Save chat session to database."""
        if not self.user_id:
            return
        
        sessions = self._get_sessions_collection()
        now = datetime.utcnow()
        
        # Create session ID if not exists
        if not self.session_id:
            self.session_id = f"chat_{uuid.uuid4().hex}"
        
        # Prepare messages
        messages = [
            {
                'role': 'user',
                'content': user_message,
                'timestamp': now,
                'tokens_used': None
            },
            {
                'role': 'assistant',
                'content': assistant_message,
                'timestamp': now,
                'tokens_used': tokens_used
            }
        ]
        
        # Check if session exists
        existing = sessions.find_one({'_id': self.session_id})
        
        if existing:
            # Update existing session
            sessions.update_one(
                {'_id': self.session_id},
                {
                    '$push': {'messages': {'$each': messages}},
                    '$inc': {'total_tokens': tokens_used},
                    '$set': {'updated_at': now, 'is_active': True}
                }
            )
        else:
            # Create new session with title from first message
            title = user_message[:50] + '...' if len(user_message) > 50 else user_message
            sessions.insert_one({
                '_id': self.session_id,
                'user_id': self.user_id,
                'title': title,
                'messages': messages,
                'total_tokens': tokens_used,
                'created_at': now,
                'updated_at': now,
                'is_active': True
            })
    
    @classmethod
    def get_user_sessions(cls, user_id: str, page: int = 1, per_page: int = 20, active_only: bool = False) -> Dict[str, Any]:
        """Get user's chat sessions."""
        sessions = cls._get_sessions_collection()
        
        # Build query
        query = {'user_id': user_id}
        if active_only:
            query['is_active'] = True
        
        # Get total count
        total = sessions.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * per_page
        cursor = sessions.find(query).sort('updated_at', -1).skip(skip).limit(per_page)
        
        session_list = []
        for session in cursor:
            session_list.append({
                'id': session['_id'],
                'user_id': session['user_id'],
                'title': session.get('title'),
                'messages': session.get('messages', []),
                'total_tokens': session.get('total_tokens', 0),
                'created_at': session['created_at'].isoformat() if session.get('created_at') else None,
                'updated_at': session['updated_at'].isoformat() if session.get('updated_at') else None,
                'is_active': session.get('is_active', True)
            })
        
        return {
            'sessions': session_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    @classmethod
    def get_session(cls, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chat session."""
        sessions = cls._get_sessions_collection()
        
        session = sessions.find_one({
            '_id': session_id,
            'user_id': user_id
        })
        
        if not session:
            return None
        
        return {
            'id': session['_id'],
            'user_id': session['user_id'],
            'title': session.get('title'),
            'messages': session.get('messages', []),
            'total_tokens': session.get('total_tokens', 0),
            'created_at': session['created_at'].isoformat() if session.get('created_at') else None,
            'updated_at': session['updated_at'].isoformat() if session.get('updated_at') else None,
            'is_active': session.get('is_active', True)
        }

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
            
            # Save to database
            tokens_used = response.usage.total_tokens
            if self.user_id:
                self._save_session(message, assistant_message, tokens_used)

            return {
                'response': assistant_message,
                'timestamp': self._get_timestamp(),
                'model': 'gpt-4o-mini',
                'tokens_used': tokens_used,
                'session_id': self.session_id
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
