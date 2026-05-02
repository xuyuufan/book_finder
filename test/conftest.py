"""
Pytest configuration and fixtures for the Book Finder application.

This module provides shared test fixtures that are automatically
discovered and used by pytest across all test modules.
"""

import pytest
from app import create_app

@pytest.fixture
def app():
    """
    Create and configure a test Flask application instance.

    This fixture sets up a Flask app with testing configuration enabled,
    which disables error catching during request handling to allow
    exceptions to propagate for easier debugging.

    Yields:
        Flask: Configured test application instance
    """
    # Create the Flask application
    app = create_app()

    # Enable testing mode
    app.config.update({
        "TESTING": True,
    })
    # Yield the app for use in tests
    yield app
    # Cleanup happens automatically after yield

@pytest.fixture
def client(app):
    """
    Create a test client for making requests to the application.

    This fixture depends on the 'app' fixture and provides a test client
    that can be used to simulate HTTP requests without running a server.

    Args:
        app (Flask): The test application instance from the app fixture

    Returns:
        FlaskClient: Test client for making HTTP requests
    """
    return app.test_client()