"""Main application routes."""

import logging
from flask import Blueprint, render_template, request, flash, jsonify
from app import review_engine
from app.utils.validators import validate_riot_id, validate_region, validate_num_matches
from app.utils.exceptions import (
    ValidationError,
    PlayerNotFoundError,
    AuthenticationError,
    ServiceUnavailableError
)

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """
    Home page with input form.

    Returns:
        Rendered index template
    """
    return render_template('index.html')


@main.route('/review', methods=['POST'])
def review():
    """
    Process match review request.

    Accepts form data:
        - riot_id: Riot ID in format "GameName#TAG"
        - region: Platform region (e.g., "na1")
        - num_matches: Number of matches to analyze (optional, default 20)

    Returns:
        Rendered review template with results or error page
    """
    try:
        # Get form data
        riot_id = request.form.get('riot_id', '').strip()
        region = request.form.get('region', '').strip().lower()
        num_matches_str = request.form.get('num_matches', '20')

        # Validate inputs
        validate_riot_id(riot_id)
        validate_region(region)
        num_matches = validate_num_matches(num_matches_str)

        # Parse Riot ID
        game_name, tag_line = riot_id.split('#')

        # Analyze player
        logger.info(f"Processing review request for {riot_id} in {region}")
        results = review_engine.analyze_player(
            game_name=game_name,
            tag_line=tag_line,
            region=region,
            num_matches=num_matches
        )

        # Check if any matches were found
        if not results['matches']:
            flash('No match data found for this player. The account may be new or have no recent matches.', 'warning')
            return render_template('index.html'), 404

        return render_template('review.html', results=results)

    except ValidationError as e:
        flash(str(e), 'error')
        logger.warning(f"Validation error: {e}")
        return render_template('index.html'), 400

    except PlayerNotFoundError as e:
        flash('Player not found. Please check the Riot ID and region.', 'error')
        logger.warning(f"Player not found: {riot_id}")
        return render_template('index.html'), 404

    except AuthenticationError as e:
        flash('API authentication failed. Please contact the administrator.', 'error')
        logger.error(f"Authentication error: {e}")
        return render_template('index.html'), 500

    except ServiceUnavailableError as e:
        flash('Riot API is currently unavailable. Please try again later.', 'error')
        logger.error(f"Service unavailable: {e}")
        return render_template('index.html'), 503

    except Exception as e:
        flash('An unexpected error occurred. Please try again later.', 'error')
        logger.error(f"Unexpected error in review route: {e}", exc_info=True)
        return render_template('index.html'), 500


@main.route('/api/review', methods=['POST'])
def api_review():
    """
    JSON API endpoint for match review.

    Accepts JSON data:
        - riot_id: Riot ID in format "GameName#TAG"
        - region: Platform region (e.g., "na1")
        - num_matches: Number of matches to analyze (optional, default 20)

    Returns:
        JSON response with match data or error
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JSON data'
            }), 400

        riot_id = data.get('riot_id', '').strip()
        region = data.get('region', '').strip().lower()
        num_matches_str = str(data.get('num_matches', 20))

        # Validate inputs
        validate_riot_id(riot_id)
        validate_region(region)
        num_matches = validate_num_matches(num_matches_str)

        # Parse Riot ID
        game_name, tag_line = riot_id.split('#')

        # Analyze player
        logger.info(f"Processing API review request for {riot_id} in {region}")
        results = review_engine.analyze_player(
            game_name=game_name,
            tag_line=tag_line,
            region=region,
            num_matches=num_matches
        )

        return jsonify({
            'status': 'success',
            'data': results
        }), 200

    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'code': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400

    except PlayerNotFoundError:
        return jsonify({
            'status': 'error',
            'code': 'PLAYER_NOT_FOUND',
            'message': 'Player not found. Check Riot ID and region.'
        }), 404

    except AuthenticationError:
        return jsonify({
            'status': 'error',
            'code': 'AUTHENTICATION_ERROR',
            'message': 'API authentication failed.'
        }), 500

    except ServiceUnavailableError:
        return jsonify({
            'status': 'error',
            'code': 'SERVICE_UNAVAILABLE',
            'message': 'Riot API is currently unavailable.'
        }), 503

    except Exception as e:
        logger.error(f"Unexpected error in API review route: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'code': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred.'
        }), 500
