"""Input validation utilities."""

import re
from app.utils.exceptions import ValidationError


ALLOWED_REGIONS = [
    'na1', 'br1', 'la1', 'la2',  # Americas
    'euw1', 'eun1', 'tr1', 'ru',  # Europe
    'kr', 'jp1',  # Asia
    'oc1', 'ph2', 'sg2', 'th2', 'tw2', 'vn2'  # SEA
]


def validate_riot_id(riot_id):
    """
    Validate Riot ID format: GameName#TAG

    Args:
        riot_id: String in format "GameName#TAG"

    Raises:
        ValidationError: If format is invalid
    """
    if not riot_id or not isinstance(riot_id, str):
        raise ValidationError("Riot ID is required")

    if '#' not in riot_id:
        raise ValidationError("Riot ID must be in format: GameName#TAG")

    parts = riot_id.split('#')
    if len(parts) != 2:
        raise ValidationError("Riot ID must contain exactly one # separator")

    game_name, tag_line = parts

    # Validate game name (3-16 characters, alphanumeric + spaces allowed)
    if not game_name or len(game_name) < 3 or len(game_name) > 16:
        raise ValidationError("Game name must be 3-16 characters")

    # Validate tag line (3-5 characters, alphanumeric)
    if not tag_line or len(tag_line) < 3 or len(tag_line) > 5:
        raise ValidationError("Tag line must be 3-5 characters")

    if not re.match(r'^[a-zA-Z0-9]+$', tag_line):
        raise ValidationError("Tag line must contain only letters and numbers")


def validate_region(region):
    """
    Validate region code.

    Args:
        region: Region code string (e.g., 'na1', 'euw1')

    Raises:
        ValidationError: If region is invalid
    """
    if not region or not isinstance(region, str):
        raise ValidationError("Region is required")

    region_lower = region.lower()
    if region_lower not in ALLOWED_REGIONS:
        raise ValidationError(
            f"Invalid region '{region}'. Allowed regions: {', '.join(ALLOWED_REGIONS)}"
        )


def validate_num_matches(num_matches):
    """
    Validate number of matches requested.

    Args:
        num_matches: Number of matches (integer or string)

    Raises:
        ValidationError: If number is invalid
    """
    try:
        num = int(num_matches)
    except (ValueError, TypeError):
        raise ValidationError("Number of matches must be a valid integer")

    if num < 1 or num > 20:
        raise ValidationError("Number of matches must be between 1 and 20")

    return num
