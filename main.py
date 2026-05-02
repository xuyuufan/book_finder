"""
Application entry point.

This module creates and runs the Flask development server.
Execute this file directly to start the application.
"""

from app import create_app
# Create the Flask application instance using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the development server
    # debug=True enables:
    #   - Auto-reloading when code changes
    #   - Detailed error pages with interactive debugger
    #   - Better error messages in the console
    # port=5000 makes the app accessible at http://localhost:5000
    app.run(debug=True,port=5001)