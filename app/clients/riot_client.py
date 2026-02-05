"""Riot API client wrapper."""

import requests
import time
import logging
from app.utils.exceptions import (
    RiotAPIError,
    PlayerNotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    AuthenticationError
)

logger = logging.getLogger(__name__)


# Region routing mapping: platform -> regional routing value
REGION_ROUTING = {
    'na1': 'americas',
    'br1': 'americas',
    'la1': 'americas',
    'la2': 'americas',
    'euw1': 'europe',
    'eun1': 'europe',
    'tr1': 'europe',
    'ru': 'europe',
    'kr': 'asia',
    'jp1': 'asia',
    'oc1': 'sea',
    'ph2': 'sea',
    'sg2': 'sea',
    'th2': 'sea',
    'tw2': 'sea',
    'vn2': 'sea'
}


class RiotAPIClient:
    """
    Wrapper for Riot API calls with rate limiting and error handling.
    """

    def __init__(self, api_key, rate_limiter):
        """
        Initialize Riot API client.

        Args:
            api_key: Riot API key
            rate_limiter: RateLimiter instance
        """
        self.api_key = api_key
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
        self.session.headers.update({
            'X-Riot-Token': self.api_key
        })

    def get_puuid_by_riot_id(self, game_name, tag_line, region):
        """
        Get PUUID by Riot ID (GameName#TAG).

        Args:
            game_name: Summoner name (e.g., "Doublelift")
            tag_line: Tag line (e.g., "NA1")
            region: Platform region (e.g., "na1")

        Returns:
            PUUID string

        Raises:
            PlayerNotFoundError: If player doesn't exist
            RiotAPIError: For other API errors
        """
        routing = self._get_region_routing(region)

        # example: https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/alzzz02/2002?api_key=RGAPI-c44369a6-0925-4799-9425-9bc89cdf3e74
        url = f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

        logger.info(f"Fetching PUUID for {game_name}#{tag_line} in region {region}")
        response_data = self._make_request(url)

        return response_data.get('puuid')

    def get_match_ids_by_puuid(self, puuid, region, count=20):
        """
        Get match IDs for a player by PUUID.

        Args:
            puuid: Player UUID
            region: Platform region (e.g., "na1")
            count: Number of matches to retrieve (default: 20)

        Returns:
            List of match ID strings

        Raises:
            RiotAPIError: For API errors
        """
        routing = self._get_region_routing(region)
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {
            'start': 0,
            'count': count
        }

        logger.info(f"Fetching {count} match IDs for PUUID {puuid[:8]}...")
        response_data = self._make_request(url, params=params)

        return response_data

    def get_match_details(self, match_id, region):
        """
        Get detailed match data by match ID.

        Args:
            match_id: Match ID (e.g., "NA1_1234567890")
            region: Platform region (e.g., "na1")

        Returns:
            Dictionary containing full match data

        Raises:
            RiotAPIError: For API errors
        """
        routing = self._get_region_routing(region)
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"

        logger.debug(f"Fetching match details for {match_id}")
        response_data = self._make_request(url)

        return response_data

    def _make_request(self, url, params=None, max_retries=3):
        """
        Make HTTP request to Riot API with rate limiting and error handling.

        Args:
            url: API endpoint URL
            params: Query parameters (optional)
            max_retries: Maximum retry attempts for transient errors

        Returns:
            JSON response data

        Raises:
            AuthenticationError: Invalid API key (401/403)
            PlayerNotFoundError: Resource not found (404)
            RateLimitError: Rate limit exceeded (429)
            ServiceUnavailableError: Service unavailable (503)
            RiotAPIError: Other API errors
        """
        for attempt in range(max_retries):
            try:
                # Apply rate limiting before request
                self.rate_limiter.wait_if_needed()

                # Make the request
                response = self.session.get(url, params=params, timeout=10)

                # Handle different status codes
                if response.status_code == 200:
                    return response.json()

                elif response.status_code in [401, 403]:
                    logger.error(f"Authentication failed: {response.status_code}")
                    raise AuthenticationError(
                        "Invalid API key. Please check your RIOT_API_KEY in .env file."
                    )

                elif response.status_code == 404:
                    logger.warning(f"Resource not found: {url}")
                    raise PlayerNotFoundError("Player not found or no match data available.")

                elif response.status_code == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get('Retry-After', 1))
                    logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")

                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded. Please try again later.")

                elif response.status_code == 503:
                    # Service unavailable
                    logger.warning(f"Service unavailable (attempt {attempt + 1}/{max_retries})")

                    if attempt < max_retries - 1:
                        # Exponential backoff
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ServiceUnavailableError("Riot API service is currently unavailable.")

                else:
                    # Other errors
                    logger.error(f"API error {response.status_code}: {response.text}")
                    raise RiotAPIError(f"API request failed with status {response.status_code}")

            except requests.Timeout:
                logger.error(f"Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise ServiceUnavailableError("Request timed out.")

            except requests.ConnectionError:
                logger.error(f"Connection error (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise ServiceUnavailableError("Connection error. Please check your internet connection.")

    def _get_region_routing(self, platform):
        """
        Map platform code to regional routing value.

        Args:
            platform: Platform code (e.g., "na1", "euw1")

        Returns:
            Regional routing value (e.g., "americas", "europe")

        Raises:
            RiotAPIError: If platform is not recognized
        """
        routing = REGION_ROUTING.get(platform.lower())
        if not routing:
            raise RiotAPIError(f"Unknown platform: {platform}")
        return routing
