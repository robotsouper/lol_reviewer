"""Rate limiter implementation using token bucket algorithm."""

import time
from collections import deque
from threading import Lock


class RateLimiter:
    """
    Token bucket rate limiter to enforce Riot API rate limits.

    Tracks requests within two time windows:
    - 20 requests per second
    - 100 requests per 2 minutes
    """

    def __init__(self, rate_per_second=20, rate_per_two_minutes=100):
        """
        Initialize rate limiter.

        Args:
            rate_per_second: Maximum requests allowed per second
            rate_per_two_minutes: Maximum requests allowed per 2 minutes (120 seconds)
        """
        self.rate_per_second = rate_per_second
        self.rate_per_two_minutes = rate_per_two_minutes

        # Track request timestamps
        self.requests_last_second = deque()
        self.requests_last_two_minutes = deque()

        # Thread lock for thread safety
        self.lock = Lock()

    def wait_if_needed(self):
        """
        Check if rate limits would be exceeded and wait if necessary.

        This method:
        1. Removes expired timestamps from tracking queues
        2. Calculates if we're at the limit for either time window
        3. Sleeps if necessary to avoid exceeding limits
        4. Records the current request timestamp
        """
        with self.lock:
            current_time = time.time()

            # Clean old requests outside time windows
            self._clean_old_requests(self.requests_last_second, 1.0)
            self._clean_old_requests(self.requests_last_two_minutes, 120.0)

            # Calculate wait time if limits would be exceeded
            wait_time = self._calculate_wait_time()

            if wait_time > 0:
                print(f"[RateLimit] Waiting {wait_time:.2f}s to respect Riot API limits")
                time.sleep(wait_time + 0.1)
                # Clean again after waiting
                self._clean_old_requests(self.requests_last_second, 1.0)
                self._clean_old_requests(self.requests_last_two_minutes, 120.0)

            # Record this request
            current_time = time.time()
            self.requests_last_second.append(current_time)
            self.requests_last_two_minutes.append(current_time)

    def _clean_old_requests(self, queue, time_window):
        """
        Remove timestamps older than the time window.

        Args:
            queue: Deque containing request timestamps
            time_window: Time window in seconds
        """
        current_time = time.time()
        while queue and (current_time - queue[0]) > time_window:
            queue.popleft()

    def _calculate_wait_time(self):
        """
        Calculate how long to wait before the next request can be made.

        Returns:
            Wait time in seconds (0 if no wait needed)
        """
        current_time = time.time()
        wait_times = []

        # Check per-second limit
        if len(self.requests_last_second) >= self.rate_per_second:
            # Wait until the oldest request in the 1-second window expires
            oldest_request = self.requests_last_second[0]
            wait_time_second = 1.0 - (current_time - oldest_request)
            if wait_time_second > 0:
                wait_times.append(wait_time_second)

        # Check per-2-minute limit
        if len(self.requests_last_two_minutes) >= self.rate_per_two_minutes:
            # Wait until the oldest request in the 2-minute window expires
            oldest_request = self.requests_last_two_minutes[0]
            wait_time_two_minutes = 120.0 - (current_time - oldest_request)
            if wait_time_two_minutes > 0:
                wait_times.append(wait_time_two_minutes)

        # Return the maximum wait time needed
        return max(wait_times) if wait_times else 0

    def reset(self):
        """Reset all tracking (useful for testing)."""
        with self.lock:
            self.requests_last_second.clear()
            self.requests_last_two_minutes.clear()
