# 📚 Kindle Trend-Flywheel (MVP)

Automated research tool to identify **validated Kindle niches** on Amazon.com. Discovers high-sales books (low BSR), cross-references with Google Trends for longevity, and uses AI to find content gaps in competitor reviews.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│ Scout Agent  │────▶│  Validator   │────▶│   Gap Analyst    │
│ (Amazon BSR) │     │(Google Trends)│     │ (Gemini 1.5 Pro) │
└─────────────┘     └──────────────┘     └──────────────────┘
       │                    │                      │
       └────────────────────┴──────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   SQLite    │
                    │  Database   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Streamlit  │
                    │  Dashboard  │
                    └─────────────┘
```

**Orchestrated by [LangGraph](https://github.com/langchain-ai/langgraph)** as a stateful multi-agent workflow.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the dashboard
streamlit run app.py
```

The app starts in **mock mode** by default — no API keys required. Set environment variables to enable live data sources.

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph (stateful multi-agent) |
| LLM | Gemini 1.5 Pro (Google AI Studio) |
| Backend | Python 3.11+ |
| Amazon Data | Mock (MVP) → Rainforest / Apify / Oxylabs |
| Trends | pytrends (Google Trends) |
| Frontend | Streamlit (Dark Mode) |
| Database | SQLite |

## Agent Pipeline

### 1. Scout Agent
- Accepts a KDP category
- Fetches top 50 products (mock data for MVP)
- **Filters:** Only keeps products with BSR between 1,000 and 100,000
- Collects reviews (prioritizing 3-star)

### 2. Validator Agent
- Queries Google Trends for primary keywords
- Calculates **Trend Stability Score** (0-100)
- Detects terminal declines, seasonal patterns, and rising trends

### 3. Gap Analyst (Gemini-Powered)
- Feeds top 100 reviews (3-star priority) into Gemini 1.5 Pro
- Identifies "Missing Value" — unmet reader needs
- Generates strategy brief with target audience, content gaps, and suggested titles

## Flywheel Score

The primary ranking metric:

- **70% Weight:** BSR Score (normalized, lower BSR = higher score)
- **30% Weight:** Trend Stability (Google Trends consistency)
- **Display:** Estimated Daily Royalty = Units × Price × 0.70

## Dashboard Views

| View | Description |
|------|-------------|
| **Opportunity Matrix** | Sortable table of niches by Flywheel Score |
| **Deep Dive** | Dual-axis chart: BSR (inverted) vs. Google Trends over 12 months |
| **Blueprint** | Gemini-generated strategy with target audience, content gaps, titles |

## Environment Variables

```bash
# LLM (required for real analysis)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro        # default

# Amazon Data Source
DATA_SOURCE=mock                    # mock | rainforest | apify | oxylabs
RAINFOREST_API_KEY=your-key
APIFY_API_KEY=your-key
```

## Alternative Data Sourcing Tools

The MVP uses mock data. Here are the recommended real data sources to integrate:

### Amazon Product Data
| Tool | Cost | Best For | URL |
|------|------|----------|-----|
| **Rainforest API** | From $49/mo | Real-time product/review data | [rainforestapi.com](https://www.rainforestapi.com/) |
| **Apify** | Free tier + paid | Flexible web scraping with pre-built Amazon actors | [apify.com](https://apify.com/) |
| **Oxylabs** | From $49/mo | E-Commerce Scraper with structured data | [oxylabs.io](https://oxylabs.io/) |
| **Keepa** | From €19/mo | Historical BSR & price tracking | [keepa.com](https://keepa.com/) |
| **Jungle Scout API** | Enterprise | KDP-focused product research | [junglescout.com](https://www.junglescout.com/) |
| **Helium 10 API** | Enterprise | Amazon seller tools & keyword research | [helium10.com](https://www.helium10.com/) |
| **SP-API** | Free (with seller account) | Official Amazon Selling Partner API | [developer.amazonservices.com](https://developer-docs.amazon.com/sp-api/) |

### Trend & Keyword Data
| Tool | Cost | Best For |
|------|------|----------|
| **pytrends** | Free | Google Trends programmatic access |
| **SerpApi** | From $50/mo | Google search results + trends |
| **Mangools / KWFinder** | From $29/mo | Keyword difficulty & search volume |

### Review Analysis
| Tool | Cost | Best For |
|------|------|----------|
| **Gemini 1.5 Pro** | Pay per token | Large context window for bulk review analysis |
| **Claude** | Pay per token | Alternative for review synthesis |
| **GPT-4o** | Pay per token | Alternative for structured analysis |

## Project Structure

```
AmazonNicheFinder/
├── app.py                  # Streamlit dashboard entry point
├── pyproject.toml          # Python project config & dependencies
├── src/
│   ├── config.py           # App configuration & env vars
│   ├── scoring.py          # Flywheel Score calculation
│   ├── workflow.py         # LangGraph state machine
│   ├── agents/
│   │   ├── scout.py        # Scout Agent (product discovery)
│   │   ├── validator.py    # Validator Agent (trend analysis)
│   │   └── gap_analyst.py  # Gap Analyst (Gemini review analysis)
│   ├── data/
│   │   └── mock_amazon.py  # Mock product/review data
│   ├── db/
│   │   └── models.py       # SQLite schema & queries
│   └── prompts/
│       └── gap_system.txt  # System prompt for Gap Analyst
├── tests/
│   └── test_scoring.py     # Unit tests
└── .streamlit/
    └── config.toml         # Streamlit dark mode theme
```

## License

MIT
