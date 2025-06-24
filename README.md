# rustrocket_x

Lightweight Python package for X/Twitter API analytics (Free Plan)

## Features

- 🚀 Simple CLI interface (`rrx`)
- 📊 Pull user metrics (followers, tweets, etc.)
- 🆓 Works with X/Twitter Free Plan API
- 🔮 Ready for future write/ads functionality (Basic/Ads-Basic plans)
- 🎨 Beautiful output with Rich formatting

## Installation

### Prerequisites

- Python >=3.11
- Poetry (for development)

### Install with Poetry

```bash
git clone <repository-url>
cd rustrocket_x
poetry install
```

### Setup X/Twitter API

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your X/Twitter API credentials:
   ```env
   X_BEARER_TOKEN=your_bearer_token_here
   ```

   **Note**: For Free Plan, you only need the `X_BEARER_TOKEN`. Get it from the [X Developer Portal](https://developer.twitter.com/).

## Quickstart

### Pull User Metrics

```bash
# Dry run (preview only)
poetry run rrx metrics pull --user rustrocket --dry-run

# Save to file
poetry run rrx metrics pull --user rustrocket --outfile data/metrics.json

# Auto-generated filename
poetry run rrx metrics pull --user rustrocket
```

### CLI Help

```bash
poetry run rrx --help
poetry run rrx metrics --help
```

## X Analytics (Free Plan)

The Free Plan provides read-only access to public user metrics:

- **Followers count**: Number of followers
- **Following count**: Number of accounts followed
- **Tweet count**: Total number of tweets
- **Listed count**: Number of public lists that include this account
- **Like count**: Total likes received

### Example Output

```
                X/Twitter Metrics for @rustrocket                
┏━━━━━━━━━━┳━━━━━━━━━┓
┃ Metric   ┃   Count ┃
┡━━━━━━━━━━╇━━━━━━━━━┩
│ Followers│  12,345 │
│ Following│     567 │
│ Tweets   │   8,901 │
│ Listed   │      23 │
│ Likes    │  45,678 │
└──────────┴─────────┘
```

## Future Features

Write and Ads functionality will be available for Basic/Ads-Basic plan users:

- Tweet posting and management
- Advertising campaign analytics
- Advanced engagement metrics
- Real-time streaming

## Development

### Setup

```bash
poetry install
poetry shell
```

### Run Tests

```bash
poetry run pytest
```

### Code Quality

```bash
poetry run black .
poetry run ruff check .
```

### Run CLI in Development

```bash
poetry run python -m rustrocket_x.cli --help
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here] 