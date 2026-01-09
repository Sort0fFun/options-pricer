"""
API Blueprint initialization with Flask-RESTX.
"""
from flask import Blueprint
from flask_restx import Api

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Initialize Flask-RESTX API with Swagger documentation
api = Api(
    api_bp,
    version='1.0',
    title='NSE Options Pricer API',
    description='RESTful API for NSE Options Pricing, PnL Analysis, and AI Chatbot',
    doc='/doc'
)

# Import and add namespaces
from backend.api import pricing, market, chatbot, pnl, auth

# Add namespaces to API
api.add_namespace(pricing.ns, path='/pricing')
api.add_namespace(market.ns, path='/market')
api.add_namespace(chatbot.ns, path='/chat')
api.add_namespace(pnl.ns, path='/pnl')
api.add_namespace(auth.ns, path='/auth')
