"""Flask application factory."""

import logging
from flask import Flask
from app.config import config
from app.clients.rate_limiter import RateLimiter
from app.clients.riot_client import RiotAPIClient
from app.services.cache_service import CacheService
from app.services.review_engine import ReviewEngine

# Global service instances
cache_service = None
review_engine = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_app(config_name='development'):
    """
    Application factory pattern.

    Args:
        config_name: Configuration name ('development', 'production', 'default')

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Validate API key
    if not app.config.get('RIOT_API_KEY'):
        raise ValueError(
            "RIOT_API_KEY not found. Please create a .env file with your API key. "
            "See .env.example for the template."
        )

    # Initialize services
    global cache_service, review_engine
    cache_service = CacheService()

    rate_limiter = RateLimiter(
        rate_per_second=app.config['RATE_LIMIT_PER_SECOND'],
        rate_per_two_minutes=app.config['RATE_LIMIT_PER_TWO_MINUTES']
    )

    riot_client = RiotAPIClient(
        api_key=app.config['RIOT_API_KEY'],
        rate_limiter=rate_limiter
    )

    review_engine = ReviewEngine(
        riot_client=riot_client,
        cache_service=cache_service
    )

    # Register blueprints
    from app.routes.main import main
    app.register_blueprint(main)

    # Log startup
    logging.info(f"Application started in {config_name} mode")

    return app
