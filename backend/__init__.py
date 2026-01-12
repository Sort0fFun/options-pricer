"""
Flask application factory.
"""
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from config import config
from datetime import datetime

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()


class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that handles datetime serialization."""
    
    def default(self, obj):
        """Convert datetime objects to ISO format strings."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )

    # Load configuration
    app.config.from_object(config[config_name])
    
    # Set custom JSON provider for datetime serialization
    app.json = CustomJSONProvider(app)

    # Initialize extensions
    CORS(app)
    mongo.init_app(app)
    jwt.init_app(app)

    # Initialize auth service with MongoDB
    from backend.services.auth_service import AuthService, bcrypt
    bcrypt.init_app(app)
    AuthService.init_app(mongo)

    # Initialize wallet and M-Pesa services
    from backend.services.wallet_service import WalletService
    from backend.services.mpesa_service import MpesaService
    WalletService.init_app(mongo)
    MpesaService.init_app(app)

    # Initialize volatility forecasting service
    from backend.services.volatility_service import VolatilityForecasterService
    VolatilityForecasterService.init_app(app)

    # Register blueprints
    from backend.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register page routes
    from backend import routes
    routes.init_app(app)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'success': False,
            'message': 'Token has expired'
        }, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'success': False,
            'message': 'Invalid token'
        }, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'success': False,
            'message': 'Authorization token required'
        }, 401

    return app
