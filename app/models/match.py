"""Match data model."""

from datetime import datetime


class MatchStats:
    """Data class for single match statistics."""

    def __init__(self, match_id, champion, kills, deaths, assists,
                 cs, damage, duration, win, timestamp, game_mode=None):
        """
        Initialize match statistics.

        Args:
            match_id: Match identifier
            champion: Champion name
            kills: Number of kills
            deaths: Number of deaths
            assists: Number of assists
            cs: Creep score (total minions killed)
            damage: Total damage dealt
            duration: Game duration in seconds
            win: Boolean indicating if the player won
            timestamp: Match end timestamp (milliseconds)
            game_mode: Game mode (optional)
        """
        self.match_id = match_id
        self.champion = champion
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.cs = cs
        self.damage = damage
        self.duration = duration
        self.win = win
        self.timestamp = timestamp
        self.game_mode = game_mode

        # Calculated fields
        self.kda = self._calculate_kda()
        self.cs_per_min = self._calculate_cs_per_min()

    def _calculate_kda(self):
        """
        Calculate KDA ratio.

        Returns:
            KDA ratio as float, or "Perfect" if no deaths
        """
        if self.deaths == 0:
            return "Perfect"
        return round((self.kills + self.assists) / self.deaths, 1)

    def _calculate_cs_per_min(self):
        """
        Calculate CS per minute.

        Returns:
            CS per minute as float
        """
        if self.duration == 0:
            return 0
        minutes = self.duration / 60.0
        return round(self.cs / minutes, 1)

    def get_formatted_timestamp(self):
        """
        Get human-readable timestamp.

        Returns:
            Formatted date string
        """
        dt = datetime.fromtimestamp(self.timestamp / 1000)
        return dt.strftime('%Y-%m-%d %H:%M')

    def get_formatted_duration(self):
        """
        Get human-readable game duration.

        Returns:
            Duration in MM:SS format
        """
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    def to_dict(self):
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            'match_id': self.match_id,
            'champion': self.champion,
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'kda': self.kda,
            'cs': self.cs,
            'cs_per_min': self.cs_per_min,
            'damage': self.damage,
            'duration': self.duration,
            'formatted_duration': self.get_formatted_duration(),
            'win': self.win,
            'timestamp': self.timestamp,
            'formatted_timestamp': self.get_formatted_timestamp(),
            'game_mode': self.game_mode
        }
