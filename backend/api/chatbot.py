"""
Chatbot API endpoints.
"""
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.chatbot_service import ChatbotService
from backend.services.wallet_service import WalletService
from backend.models.chatbot_models import ChatMessageRequest
from pydantic import ValidationError
from datetime import datetime, timedelta

# Create namespace
ns = Namespace('chat', description='Flavia AI chatbot operations')

# API Models for Swagger documentation
chat_message_model = ns.model('ChatMessage', {
    'message': fields.String(required=True, description='User message', example='How does volatility affect option prices?'),
    'context': fields.Raw(description='Optional context object')
})

# Daily free tokens configuration
DAILY_FREE_TOKENS = 4

# Initialize chatbot service (singleton)
try:
    chatbot_service = ChatbotService()
except Exception as e:
    print(f"Warning: ChatbotService initialization failed: {e}")
    chatbot_service = None


def check_and_grant_daily_tokens(user_id: str) -> dict:
    """Check if user is eligible for daily free tokens and grant them."""
    from bson import ObjectId
    
    users = WalletService._get_users_collection()
    user = users.find_one({'_id': ObjectId(user_id)})
    
    if not user:
        return {'granted': False, 'tokens_granted': 0}
    
    wallet = user.get('wallet', {})
    last_daily_grant = wallet.get('last_daily_token_grant')
    
    # Check if user already received daily tokens today
    today = datetime.utcnow().date()
    
    if last_daily_grant:
        if isinstance(last_daily_grant, datetime):
            last_grant_date = last_daily_grant.date()
        else:
            last_grant_date = datetime.fromisoformat(str(last_daily_grant)).date()
        
        if last_grant_date >= today:
            return {'granted': False, 'tokens_granted': 0, 'already_granted_today': True}
    
    # Grant daily tokens
    users.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$inc': {'wallet.chat_tokens': DAILY_FREE_TOKENS},
            '$set': {
                'wallet.last_daily_token_grant': datetime.utcnow(),
                'wallet.last_updated': datetime.utcnow()
            }
        },
        upsert=False
    )
    
    # Ensure wallet exists first
    WalletService.ensure_wallet_exists(user_id)
    
    return {'granted': True, 'tokens_granted': DAILY_FREE_TOKENS}


@ns.route('/message')
class ChatMessage(Resource):
    """Send message to Flavia AI."""

    @ns.doc('send_chat_message')
    @ns.expect(chat_message_model)
    @jwt_required()
    def post(self):
        """Send message and get AI response. Requires authentication and tokens."""
        if chatbot_service is None:
            return {
                'success': False,
                'message': 'Chatbot service is not available. Please check OPENAI_API_KEY.'
            }, 503

        user_id = get_jwt_identity()
        
        try:
            # Check and grant daily tokens if eligible
            daily_result = check_and_grant_daily_tokens(user_id)
            
            # Get current wallet
            wallet = WalletService.get_wallet(user_id)
            current_tokens = wallet.get('chat_tokens', 0)
            
            # Check if user has tokens
            if current_tokens < 1:
                return {
                    'success': False,
                    'error': 'insufficient_tokens',
                    'message': 'You have no tokens remaining. Please purchase more tokens to continue chatting.',
                    'tokens_remaining': 0
                }, 402
            
            # Validate request
            data = ChatMessageRequest(**request.json)

            # Use one token
            WalletService.use_token(user_id, 1)

            # Get response
            result = chatbot_service.send_message(
                message=data.message,
                context=data.context
            )
            
            # Get updated wallet
            updated_wallet = WalletService.get_wallet(user_id)

            return {
                'success': True,
                'data': result,
                'tokens_remaining': updated_wallet.get('chat_tokens', 0),
                'daily_tokens_granted': daily_result.get('tokens_granted', 0)
            }, 200

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Validation error',
                'errors': e.errors()
            }, 400
        except Exception as e:
            current_app.logger.error(f"Chat error: {e}")
            return {
                'success': False,
                'message': str(e)
            }, 500


@ns.route('/suggestions')
class ChatSuggestions(Resource):
    """Get suggested questions."""

    @ns.doc('get_suggestions')
    def get(self):
        """Get list of suggested questions."""
        if chatbot_service is None:
            return {
                'success': False,
                'message': 'Chatbot service is not available.'
            }, 503

        try:
            suggestions = chatbot_service.get_suggestions()
            return {
                'success': True,
                'data': {'suggestions': suggestions}
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500


@ns.route('/token-status')
class ChatTokenStatus(Resource):
    """Get chat token status including daily tokens."""

    @ns.doc('get_token_status')
    @jwt_required()
    def get(self):
        """Get token balance and check for daily free tokens."""
        user_id = get_jwt_identity()
        
        try:
            # Check and grant daily tokens if eligible
            daily_result = check_and_grant_daily_tokens(user_id)
            
            # Get current wallet
            wallet = WalletService.get_wallet(user_id)
            
            return {
                'success': True,
                'tokens': wallet.get('chat_tokens', 0),
                'tokens_used': wallet.get('tokens_used', 0),
                'daily_tokens_granted': daily_result.get('tokens_granted', 0),
                'daily_tokens_available': not daily_result.get('already_granted_today', False),
                'daily_free_tokens': DAILY_FREE_TOKENS
            }, 200
        except Exception as e:
            current_app.logger.error(f"Token status error: {e}")
            return {
                'success': False,
                'message': str(e)
            }, 500


@ns.route('/clear')
class ChatClear(Resource):
    """Clear conversation history."""

    @ns.doc('clear_conversation')
    def post(self):
        """Clear server-side conversation history."""
        if chatbot_service is None:
            return {
                'success': False,
                'message': 'Chatbot service is not available.'
            }, 503

        try:
            chatbot_service.clear_conversation()
            return {
                'success': True,
                'message': 'Conversation cleared'
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }, 500
