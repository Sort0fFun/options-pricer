"""
API Blueprint initialization with Flask-RESTX.
"""
from flask import Blueprint
from flask_restx import Api, Resource

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

# Health check endpoint
@api_bp.route('/health')
def health_check():
    """Health check endpoint for Docker/Kubernetes."""
    return {'status': 'healthy', 'service': 'options-pricer-api'}, 200

# Import and add namespaces
from backend.api import pricing, market, chatbot, pnl, auth, wallet, volatility, nse, reports

# Add namespaces to API
api.add_namespace(pricing.ns, path='/pricing')
api.add_namespace(market.ns, path='/market')
api.add_namespace(chatbot.ns, path='/chat')
api.add_namespace(pnl.ns, path='/pnl')
api.add_namespace(auth.ns, path='/auth')
api.add_namespace(wallet.wallet_ns, path='/wallet')
api.add_namespace(reports.reports_ns, path='/reports')

# Register volatility blueprint (uses plain Flask Blueprint, not Flask-RESTX)
api_bp.register_blueprint(volatility.volatility_bp, url_prefix='/volatility')

# Register NSE derivatives blueprint
api_bp.register_blueprint(nse.nse_bp, url_prefix='/nse')

