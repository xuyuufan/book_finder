"""
Flask application factory module.

This module provides the create_app factory function for initializing
and configuring the Flask application instance.
"""

from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_app():
    """
    Create and configure the Flask application.

    This factory function initializes a new Flask application instance,
    configures it with environment variables, and registers all blueprints.

    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize the Flask application
    app = Flask(__name__)

    # Set the secret key for session management and CSRF protection
    # Uses environment variable if available, falls back to 'dev_secret' for development
    app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

    # Import and register the main application blueprint
    # Blueprint registration enables modular route organization
    from .app import bp as main_bp
    app.register_blueprint(main_bp)

    return app