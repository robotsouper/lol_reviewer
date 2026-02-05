"""Application entry point."""

import os
from app import create_app

# Get environment from environment variable or default to development
config_name = os.getenv('FLASK_ENV', 'development')

# Create Flask application
app = create_app(config_name)

if __name__ == '__main__':
    # Run the application
    # Debug mode is controlled by the config
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config.get('DEBUG', True)
    )
