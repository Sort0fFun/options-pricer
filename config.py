"""
Configuration classes for the Flask application.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # CORS settings
    CORS_HEADERS = 'Content-Type'

    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    # NSE Market hours (East Africa Time - UTC+3)
    MARKET_OPEN_HOUR = 9  # 9:00 AM
    MARKET_CLOSE_HOUR = 15  # 3:00 PM
    MARKET_TIMEZONE = 'Africa/Nairobi'

    # Data file paths
    NSE_DATA_FILE = os.environ.get('NSE_DATA_FILE', '/Users/mac/Downloads/Ahona_Amanda_Derivatives_Price_Lists_2025.csv')

    # Flask-RESTX settings
    RESTX_MASK_SWAGGER = False
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_VALIDATE = True
    ERROR_404_HELP = False

    # MongoDB configuration
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/options_pricer')

    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = False  # Enable in production


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    JWT_COOKIE_SECURE = True  # Require HTTPS in production
    JWT_COOKIE_CSRF_PROTECT = True  # Enable CSRF protection in production


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
