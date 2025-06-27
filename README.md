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

## Monitoring

RustRocket X includes built-in Prometheus metrics for monitoring CLI usage and performance:

- **Endpoint:** `http://localhost:9100/metrics`
- **Metrics:**
  - `rrx_runs_total` - Total CLI command executions
  - `rrx_failures_total` - Commands that raised exceptions  
  - `rrx_duration_seconds` - Command execution time histogram

The metrics server starts automatically when running any CLI command and exposes metrics on port 9100.

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

## Twitter Automation (Basic Plan)

**Rate Limits**: 300 tweets per 3-hour window  
**Cost**: $100/month for Basic Plan

### Features

- 🤖 **Automated posting** from queue files
- 📝 **Markdown support** with YAML front-matter
- 📌 **Tweet pinning** capability
- 🔁 **Reply threading** support
- 🛡️ **Rate limiting** with exponential backoff
- 📊 **JSON logging** of all activities
- 🧪 **Dry-run mode** for testing

### Setup Tweet Queue

Create tweet files in `tweets/queue/` directory:

```bash
mkdir -p tweets/queue tweets/done
```

### Tweet File Format

**Markdown tweets** (`.tweet.md`):
```markdown
---
pin: true
tags: ["announcement", "feature"]
---

# 🚀 New Feature Launch

Excited to announce **RustRocket X** v2.0!

Features:
- Automated posting
- Rate limit handling  
- Analytics dashboard

#RustRocket #TwitterAutomation
```

**Text tweets** (`.tweet.txt`):
```yaml
---
reply_to: "1234567890123456789"
tags: ["reply", "community"]
---

Thanks for the feedback! We're working on adding more features.

What would you like to see next? 🤔
```

### Autopost Commands

```bash
# Preview tweets in queue (dry-run)
poetry run rrx autopost run --dry-run

# Post tweets from queue
poetry run rrx autopost run

# Check status and recent activity
poetry run rrx autopost status

# Custom directories
poetry run rrx autopost run --queue-dir custom/queue --done-dir custom/done

# Limit number of tweets per run
poetry run rrx autopost run --max-tweets 5
```

### YAML Front-Matter Options

| Option | Type | Description |
|--------|------|-------------|
| `pin` | boolean | Pin this tweet after posting |
| `reply_to` | string | Tweet ID to reply to |
| `tags` | array | Tags for organization (not posted) |

### Automation Pipeline

1. **Queue**: Place `.tweet.md` or `.tweet.txt` files in `tweets/queue/`
2. **Process**: Run `rrx autopost run` (manually or via cron)
3. **Post**: Tweets are posted to X/Twitter via OAuth 1.0a
4. **Archive**: Files moved to `tweets/done/` with JSON logs
5. **Pin**: Optional tweet pinning if `pin: true`

### Rate Limiting

- **Built-in delays**: 1 second between tweets
- **429 handling**: 60-second backoff on rate limits
- **Batch processing**: Configurable max tweets per run
- **Safe defaults**: Designed for Basic Plan limits

### Logging

All tweet activity is logged to `tweets/done/autopost.log`:

```json
{
  "timestamp": "2025-06-24T08:00:00Z",
  "filename": "announcement.tweet.md",
  "tweet_id": "1234567890123456789",
  "text": "🚀 New Feature Launch...",
  "metadata": {"pin": true, "tags": ["announcement"]},
  "success": true,
  "char_count": 156
}
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