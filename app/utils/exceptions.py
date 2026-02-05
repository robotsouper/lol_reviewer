"""Custom exceptions for the League of Legends Reviewer application."""


class RiotAPIError(Exception):
    """Base exception for Riot API errors."""
    pass


class PlayerNotFoundError(RiotAPIError):
    """Raised when a player is not found (404 from API)."""
    pass


class RateLimitError(RiotAPIError):
    """Raised when rate limit is exceeded (429 from API)."""
    pass


class ServiceUnavailableError(RiotAPIError):
    """Raised when Riot API service is unavailable (503 from API)."""
    pass


class AuthenticationError(RiotAPIError):
    """Raised when authentication fails (401/403 from API)."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass
