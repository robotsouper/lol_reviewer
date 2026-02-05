# LoL Match Reviewer

A Flask-based web application that analyzes League of Legends match history using the Riot Games API. Get detailed per-game statistics and overall performance trends for any player.

## Features

- **Player Analysis**: Analyze any player by Riot ID (GameName#TAG) and region
- **Match Statistics**: View KDA, CS, damage dealt for last 15-20 matches
- **Performance Trends**: See win rate, average stats, most played champions
- **Best/Worst Highlights**: Identify top and bottom performances
- **Smart Caching**: In-memory cache reduces API calls and respects rate limits
- **Responsive Design**: Clean, modern UI that works on all devices

## Prerequisites

- Python 3.8+
- Riot Games API Key (free development key)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd lol_reviewer
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Riot API Key

1. Go to [Riot Developer Portal](https://developer.riotgames.com/)
2. Sign in with your Riot account
3. Register a new application
4. Copy your Development API Key

**Note**: Development keys expire every 24 hours and must be regenerated daily.

### 5. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
FLASK_ENV=development
FLASK_DEBUG=1
```

## Usage

### Running the Application

```bash
python run.py
```

The application will start at `http://127.0.0.1:5000`

### Using the Web Interface

1. Open your browser and navigate to `http://127.0.0.1:5000`
2. Enter a Riot ID in the format `GameName#TAG` (e.g., `Doublelift#NA1`)
3. Select the appropriate region (e.g., `na1` for North America)
4. Choose number of matches to analyze (1-20, default: 20)
5. Click "Analyze Matches"

### Supported Regions

**Americas**: na1, br1, la1, la2
**Europe**: euw1, eun1, tr1, ru
**Asia**: kr, jp1
**SEA/Oceania**: oc1, ph2, sg2, th2, tw2, vn2

## API Endpoints

### Web Interface

- `GET /` - Home page with input form
- `POST /review` - Process review request (HTML response)

### JSON API

- `POST /api/review` - Process review request (JSON response)

**Request Body**:
```json
{
    "riot_id": "PlayerName#TAG",
    "region": "na1",
    "num_matches": 20
}
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "player": { ... },
        "matches": [ ... ],
        "aggregate_stats": { ... }
    }
}
```

## Project Structure

```
lol_reviewer/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration
│   ├── clients/
│   │   ├── riot_client.py       # Riot API wrapper
│   │   └── rate_limiter.py      # Rate limiting
│   ├── services/
│   │   ├── review_engine.py     # Business logic
│   │   └── cache_service.py     # Caching
│   ├── models/
│   │   ├── player.py            # Player data model
│   │   └── match.py             # Match data model
│   ├── routes/
│   │   └── main.py              # Flask routes
│   ├── utils/
│   │   ├── validators.py        # Input validation
│   │   └── exceptions.py        # Custom exceptions
│   ├── templates/               # HTML templates
│   └── static/                  # CSS and JavaScript
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Example environment file
├── requirements.txt             # Python dependencies
└── run.py                       # Application entry point
```

## Architecture

### Data Flow

1. User enters Riot ID and region
2. Input validation
3. Get PUUID from Riot API (cached)
4. Fetch match IDs (cached)
5. Fetch match details for each ID (cached, rate-limited)
6. Extract player statistics
7. Compute aggregate statistics
8. Display results

### Key Components

- **Riot Client**: Handles all API communication with error handling and retries
- **Rate Limiter**: Token bucket algorithm enforces 20 req/sec, 100 req/2min limits
- **Cache Service**: In-memory cache with TTL to reduce API calls
- **Review Engine**: Orchestrates data fetching and statistics computation

## Configuration

Edit [app/config.py](app/config.py) to customize:

- `RATE_LIMIT_PER_SECOND`: API calls per second (default: 20)
- `RATE_LIMIT_PER_TWO_MINUTES`: API calls per 2 minutes (default: 100)
- `CACHE_TTL_PUUID`: PUUID cache duration (default: 1 hour)
- `CACHE_TTL_MATCH_IDS`: Match IDs cache duration (default: 5 minutes)
- `CACHE_TTL_MATCH_DETAILS`: Match details cache duration (default: 30 minutes)

## Troubleshooting

### "RIOT_API_KEY not found" Error

- Make sure you created a `.env` file in the project root
- Verify the API key is correctly copied (starts with `RGAPI-`)
- Check that `python-dotenv` is installed

### "Player not found" Error

- Verify the Riot ID format: `GameName#TAG`
- Ensure the tag is correct (it's case-sensitive)
- Check that the region matches the player's account

### Rate Limit Errors

- The app has built-in rate limiting, but if you're testing heavily, wait a minute
- Development keys have strict limits (20/sec, 100/2min)

### No Matches Found

- The player may be new or have no recent matches
- Match data can take ~5 minutes to appear after a game ends
- Some players may have private profiles

## Development

### Running in Debug Mode

Debug mode is enabled by default in development:

```bash
FLASK_ENV=development python run.py
```

### Adding New Features

The application follows a clean architecture:

1. Add API methods in [riot_client.py](app/clients/riot_client.py)
2. Add business logic in [review_engine.py](app/services/review_engine.py)
3. Add routes in [main.py](app/routes/main.py)
4. Update templates in [templates/](app/templates/)

## Rate Limits

**Development Key Limits**:
- 20 requests per second
- 100 requests per 2 minutes
- Key expires every 24 hours

**API Call Optimization**:
- Cold cache: ~22 calls (1 PUUID + 1 match IDs + 20 match details)
- Warm cache: 0 calls (instant response)

## License

This project is for educational purposes. Not affiliated with Riot Games.

## Acknowledgments

- Powered by [Riot Games API](https://developer.riotgames.com/)
- Built with Flask and Python

## Support

For issues or questions, please open an issue on GitHub