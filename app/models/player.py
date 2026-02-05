"""Player data model."""


class PlayerStats:
    """Data class for player statistics across multiple matches."""

    def __init__(self, puuid, game_name, tag_line, region):
        """
        Initialize player statistics.

        Args:
            puuid: Player unique identifier
            game_name: Summoner name
            tag_line: Tag line (e.g., "NA1")
            region: Platform region
        """
        self.puuid = puuid
        self.game_name = game_name
        self.tag_line = tag_line
        self.region = region
        self.matches = []
        self.aggregate_stats = {}

    def add_match(self, match_stats):
        """
        Add a match to the player's match history.

        Args:
            match_stats: MatchStats instance
        """
        self.matches.append(match_stats)

    def set_aggregate_stats(self, stats):
        """
        Set aggregated statistics.

        Args:
            stats: Dictionary of aggregate statistics
        """
        self.aggregate_stats = stats

    def get_riot_id(self):
        """
        Get full Riot ID.

        Returns:
            Riot ID in format "GameName#TAG"
        """
        return f"{self.game_name}#{self.tag_line}"

    def to_dict(self):
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            'puuid': self.puuid,
            'game_name': self.game_name,
            'tag_line': self.tag_line,
            'riot_id': self.get_riot_id(),
            'region': self.region,
            'matches': [match.to_dict() for match in self.matches],
            'aggregate_stats': self.aggregate_stats
        }
