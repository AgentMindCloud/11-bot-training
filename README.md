# Restaurant Bots — 11-Bot Marketing & SEO System

A multi-agent marketing automation system for local restaurants, built with Python 3.11+, Pydantic v2, and OpenAI.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator (Bot 8)                      │
│         Synthesizes all outputs → Weekly Report              │
└──────────┬──────────────────────────────────────────────────┘
           │ reads outputs from
    ┌──────┴──────────────────────────────────────────────┐
    │                   Bot Outputs (./outputs/)           │
    └──────┬───────┬───────┬───────┬───────┬─────────────┘
           │       │       │       │       │
    ┌──────┴─┐ ┌───┴──┐ ┌──┴───┐ ┌─┴────┐ ┌┴──────────┐
    │Bot 1   │ │Bot 2 │ │Bot 3 │ │Bot 4 │ │Bot 5      │
    │LocalSEO│ │Conte │ │Forum │ │Link  │ │Competitor │
    └────────┘ └──────┘ └──────┘ │Build │ └───────────┘
    ┌────────┐ ┌──────┐ ┌──────┐ └──────┘
    │Bot 6   │ │Bot 7 │ │Bot 9 │
    │Trends  │ │Chat  │ │Review│
    └────────┘ └──────┘ └──────┘
    ┌────────┐ ┌──────┐
    │Bot 10  │ │Bot 11│
    │Reserv. │ │Loyal.│
    └────────┘ └──────┘
```

## Bots

| # | Bot | Description | Status |
|---|-----|-------------|--------|
| 1 | Local SEO | Keyword clusters, title tags, meta descriptions, internal links | Complete |
| 2 | Content | Blog posts, Facebook/TikTok content, FAQs | Complete |
| 3 | Forum | Community marketing drafts with human review queue | Complete |
| 4 | Link Building | Prospect discovery, outreach email generation, DB tracking | Complete |
| 5 | Competitor | Website crawling, profile extraction, comparative analysis | Complete |
| 6 | Trend Tracking | News monitoring, weekly trend reports | Complete |
| 7 | Chatbot | Multi-turn restaurant chatbot with marketing automation | Complete |
| 8 | Orchestrator | Synthesizes all outputs into weekly report with task list | Complete |
| 9 | Review Monitor | Google/Yelp/TripAdvisor review monitoring | Stub |
| 10 | Reservation Funnel | Booking flow analysis and optimization | Stub |
| 11 | Loyalty | Customer retention and re-engagement campaigns | Stub |

## Setup

```bash
# 1. Clone and install
pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run tests
pytest tests/ -v
```

## Usage

```bash
# Run individual bots
python -m bots.local_seo.run --city Austin --cuisine Italian
python -m bots.content.run --platform blog
python -m bots.forum.run --topic "best Italian restaurants" --platform reddit
python -m bots.competitor.run https://competitor1.com https://competitor2.com
python -m bots.trend_tracking.run
python -m bots.chatbot.run --message "What are your hours?"

# Run orchestrator (generates weekly report)
python -m bots.orchestrator.run
```

## Configuration

All configuration is via environment variables (12-factor). See `.env.example` for all options.

Key variables:
- `OPENAI_API_KEY` — Required for all LLM-powered bots
- `RESTAURANT_NAME`, `RESTAURANT_CITY`, `RESTAURANT_CUISINE` — Restaurant identity
- `DATABASE_URL` — SQLite (default) or PostgreSQL for link tracking
- `OUTPUT_DIR` — Where bot outputs are saved (default: `./outputs`)

## Project Structure

```
├── infra/           # Config, infrastructure
├── common/          # Shared: models, LLM client, crawler, DB
├── bots/            # Individual bot implementations
│   ├── base.py      # Abstract BaseBot
│   ├── local_seo/
│   ├── content/
│   ├── forum/
│   ├── link_building/
│   ├── competitor/
│   ├── trend_tracking/
│   ├── chatbot/
│   ├── orchestrator/
│   ├── review_monitor/
│   ├── reservation_funnel/
│   └── loyalty/
├── tests/           # Pytest test suite
└── outputs/         # Bot output files (gitignored)
```
