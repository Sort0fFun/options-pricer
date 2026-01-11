"""
Page routes for rendering templates.
"""
from flask import render_template


def init_app(app):
    """Initialize page routes."""

    @app.route('/')
    def index():
        """Option calculator page."""
        return render_template('index.html')

    @app.route('/pnl')
    def pnl():
        """PnL predictor page."""
        return render_template('pnl.html')

    @app.route('/chatbot')
    def chatbot():
        """Flavia AI chatbot page."""
        return render_template('chatbot.html')

    @app.route('/settings')
    def settings():
        """Settings page."""
        return render_template('settings.html')

    @app.route('/login')
    def login():
        """Login page."""
        return render_template('login.html')

    @app.route('/register')
    def register():
        """Registration page."""
        return render_template('register.html')

    @app.route('/profile')
    def profile():
        """User profile page."""
        return render_template('profile.html')

    @app.route('/wallet')
    def wallet():
        """User wallet page."""
        return render_template('wallet.html')
