"""
Flask application entry point.

This is the new Flask-based version of the NSE Options Pricer,
replacing the Streamlit implementation.

Run with: python flask_app.py
Or in production: gunicorn -w 4 -b 0.0.0.0:8000 flask_app:app
"""
import os
from dotenv import load_dotenv
from backend import create_app

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.config['DEBUG']
    )
