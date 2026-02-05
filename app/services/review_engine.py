"""Review engine for analyzing player match statistics."""

import logging
from collections import Counter
from app.models.player import PlayerStats
from app.models.match import MatchStats
from app.utils.exceptions import RiotAPIError

logger = logging.getLogger(__name__)


class ReviewEngine:
    """
    Core business logic for match analysis.

    Orchestrates the entire flow from fetching player data
    to computing statistics and generating reviews.
    """

    def __init__(self, riot_client, cache_service):
        """
        Initialize review engine.

        Args:
            riot_client: RiotAPIClient instance
            cache_service: CacheService instance
        """
        self.riot_client = riot_client
        self.cache_service = cache_service

    def analyze_player(self, game_name, tag_line, region, num_matches=20):
        """
        Main orchestration method to analyze a player's match history.

        Args:
            game_name: Summoner name
            tag_line: Tag line (e.g., "NA1")
            region: Platform region (e.g., "na1")
            num_matches: Number of matches to analyze (default: 20)

        Returns:
            Dictionary containing player stats, match list, and aggregate stats

        Raises:
            PlayerNotFoundError: If player doesn't exist
            RiotAPIError: For other API errors
        """
        logger.info(f"Starting analysis for {game_name}#{tag_line} in {region}")

        # Step 1: Get PUUID (with caching)
        puuid = self._get_puuid_cached(game_name, tag_line, region)
        logger.info(f"PUUID retrieved: {puuid[:8]}...")

        # Step 2: Get match IDs (with caching)
        match_ids = self._get_match_ids_cached(puuid, region, num_matches)
        logger.info(f"Retrieved {len(match_ids)} match IDs")

        if not match_ids:
            logger.warning("No matches found for player")
            return {
                'player': {
                    'game_name': game_name,
                    'tag_line': tag_line,
                    'region': region,
                    'riot_id': f"{game_name}#{tag_line}"
                },
                'matches': [],
                'aggregate_stats': {}
            }

        # Step 3: Get match details and extract player stats
        match_stats_list = []
        for i, match_id in enumerate(match_ids, 1):
            try:
                logger.info(f"Processing match {i}/{len(match_ids)}: {match_id}")
                match_data = self._get_match_details_cached(match_id, region)
                player_stats = self._extract_player_stats(match_data, puuid)
                match_stats_list.append(player_stats)
            except Exception as e:
                logger.error(f"Error processing match {match_id}: {e}")
                # Skip this match and continue with others
                continue

        logger.info(f"Successfully processed {len(match_stats_list)} matches")

        # Step 4: Compute aggregate statistics
        aggregate_stats = self._compute_aggregate_stats(match_stats_list)

        # Step 5: Build result
        return {
            'player': {
                'game_name': game_name,
                'tag_line': tag_line,
                'region': region,
                'riot_id': f"{game_name}#{tag_line}"
            },
            'matches': [match.to_dict() for match in match_stats_list],
            'aggregate_stats': aggregate_stats
        }

    def _get_puuid_cached(self, game_name, tag_line, region):
        """Get PUUID with caching."""
        cache_key = f"puuid:{game_name}:{tag_line}:{region}"
        puuid = self.cache_service.get(cache_key)

        if not puuid:
            puuid = self.riot_client.get_puuid_by_riot_id(game_name, tag_line, region)
            # Cache for 1 hour
            self.cache_service.set(cache_key, puuid, ttl=3600)

        return puuid

    def _get_match_ids_cached(self, puuid, region, count):
        """Get match IDs with caching."""
        cache_key = f"match_ids:{puuid}:{region}:{count}"
        match_ids = self.cache_service.get(cache_key)

        if not match_ids:
            match_ids = self.riot_client.get_match_ids_by_puuid(puuid, region, count)
            # Cache for 5 minutes
            self.cache_service.set(cache_key, match_ids, ttl=300)

        return match_ids

    def _get_match_details_cached(self, match_id, region):
        """Get match details with caching."""
        cache_key = f"match:{match_id}:{region}"
        match_data = self.cache_service.get(cache_key)

        if not match_data:
            match_data = self.riot_client.get_match_details(match_id, region)
            # Cache for 30 minutes
            self.cache_service.set(cache_key, match_data, ttl=1800)

        return match_data

    def _extract_player_stats(self, match_data, puuid):
        """
        Extract player-specific stats from match data.

        Args:
            match_data: Full match data from API
            puuid: Player PUUID to find in the match

        Returns:
            MatchStats instance

        Raises:
            KeyError: If expected data is missing
        """
        # Find the participant matching the PUUID
        participant = None
        for p in match_data['info']['participants']:
            if p['puuid'] == puuid:
                participant = p
                break

        if not participant:
            raise RiotAPIError(f"Player not found in match data")

        # Extract relevant stats
        match_id = match_data['metadata']['matchId']
        champion = participant['championName']
        kills = participant['kills']
        deaths = participant['deaths']
        assists = participant['assists']
        cs = participant['totalMinionsKilled'] + participant.get('neutralMinionsKilled', 0)
        damage = participant['totalDamageDealtToChampions']
        duration = match_data['info']['gameDuration']
        win = participant['win']
        timestamp = match_data['info']['gameEndTimestamp']
        game_mode = match_data['info']['gameMode']

        return MatchStats(
            match_id=match_id,
            champion=champion,
            kills=kills,
            deaths=deaths,
            assists=assists,
            cs=cs,
            damage=damage,
            duration=duration,
            win=win,
            timestamp=timestamp,
            game_mode=game_mode
        )

    def _compute_aggregate_stats(self, matches):
        """
        Compute overall statistics across all matches.

        Args:
            matches: List of MatchStats instances

        Returns:
            Dictionary of aggregate statistics
        """
        if not matches:
            return {}

        total_matches = len(matches)
        wins = sum(1 for m in matches if m.win)
        win_rate = round((wins / total_matches) * 100, 1)

        # Calculate average KDA
        total_kills = sum(m.kills for m in matches)
        total_deaths = sum(m.deaths for m in matches)
        total_assists = sum(m.assists for m in matches)

        if total_deaths == 0:
            avg_kda = "Perfect"
        else:
            avg_kda = round((total_kills + total_assists) / total_deaths, 2)

        # Average CS per minute
        total_cs = sum(m.cs for m in matches)
        total_duration = sum(m.duration for m in matches)
        avg_cs_per_min = round((total_cs / (total_duration / 60)), 1) if total_duration > 0 else 0

        # Average damage
        total_damage = sum(m.damage for m in matches)
        avg_damage = int(total_damage / total_matches)

        # Most played champions
        champion_counts = Counter(m.champion for m in matches)
        most_played = [
            {'champion': champ, 'count': count}
            for champ, count in champion_counts.most_common(5)
        ]

        # Best and worst performances (by KDA)
        matches_with_numeric_kda = [m for m in matches if isinstance(m.kda, (int, float))]
        if matches_with_numeric_kda:
            best_match = max(matches_with_numeric_kda, key=lambda m: m.kda)
            worst_match = min(matches_with_numeric_kda, key=lambda m: m.kda)
        else:
            best_match = matches[0] if matches else None
            worst_match = matches[0] if matches else None

        return {
            'total_matches': total_matches,
            'wins': wins,
            'losses': total_matches - wins,
            'win_rate': win_rate,
            'avg_kda': avg_kda,
            'avg_kills': round(total_kills / total_matches, 1),
            'avg_deaths': round(total_deaths / total_matches, 1),
            'avg_assists': round(total_assists / total_matches, 1),
            'avg_cs_per_min': avg_cs_per_min,
            'avg_damage': avg_damage,
            'most_played_champions': most_played,
            'best_match': best_match.to_dict() if best_match else None,
            'worst_match': worst_match.to_dict() if worst_match else None
        }
