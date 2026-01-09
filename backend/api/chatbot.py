"""
Chatbot API endpoints.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from backend.services.chatbot_service import ChatbotService
from backend.models.chatbot_models import ChatMessageRequest
from pydantic import ValidationError

# Create namespace
ns = Namespace('chat', description='Flavia AI chatbot operations')

# API Models for Swagger documentation
chat_message_model = ns.model('ChatMessage', {
    'message': fields.String(required=True, description='User message', example='How does volatility affect option prices?'),
    'context': fields.Raw(description='Optional context object')
})

# Initialize chatbot service (singleton)
try:
    chatbot_service = ChatbotService()
except Exception as e:
    print(f"Warning: ChatbotService initialization failed: {e}")
    chatbot_service = None


@ns.route('/message')
class ChatMessage(Resource):
    """Send message to Flavia AI."""

    @ns.doc('send_chat_message')
    @ns.expect(chat_message_model)
    def post(self):
        """Send message and get AI response."""
        if chatbot_service is None:
            return {
                'success': False,
                'message': 'Chatbot service is not available. Please check OPENAI_API_KEY.'
            }, 503

        try:
            # Validate request
            data = ChatMessageRequest(**request.json)

            # Get response
            result = chatbot_service.send_message(
                message=data.message,
                context=data.context
            )

            return {
                'success': True,
                'data': result
            }, 200

        except ValidationError as e:
            return {
                'success': False,
                'message': 'Validation error',
                'errors': e.errors()
            }, 400
        except Exception as e:
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
