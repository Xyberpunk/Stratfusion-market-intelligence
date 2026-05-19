# Indian Stock Market News Intelligence Platform

Production-grade async ingestion pipeline for Indian market news, built for duplicate suppression, semantic retrieval, and future AI trading intelligence.

## Architecture

```text
Playwright Scrapers
        |
        v
Normalization Layer
        |
        v
Deduplication Layer
        |
        v
MySQL Storage
        |
        v
Embedding Worker Queue
        |
        v
ChromaDB Vector Store
        |
        v
Semantic Similarity Engine
        |
        v
Future NLP/Sentiment Engine
```

## Sources

Implemented scrapers:

- Moneycontrol: markets, stocks, stock-markets
- CNBC TV18: market, stocks, business
- ET Markets: markets, stocks, stock-market news
- NDTV Profit: markets, business, stock-market news
- CNBC Awaaz: Hindi market and business headline/article-level extraction

The scrapers fetch only public pages, evaluate `robots.txt`, use pacing, and back off on `403` and `429`.

## Setup

Use Python 3.11.

```bash
cd scraper_engine
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install
cp .env.example .env
```

Edit `.env` with MySQL credentials.

```bash
python main.py
```

## MySQL Setup

The application creates the configured database and table if the MySQL user has permission. For a dedicated user:

```sql
CREATE DATABASE IF NOT EXISTS stock_news
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'stock_user'@'%' IDENTIFIED BY 'change_me';
GRANT ALL PRIVILEGES ON stock_news.* TO 'stock_user'@'%';
FLUSH PRIVILEGES;
```

Schema:

```sql
CREATE TABLE news_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    url_hash CHAR(64) NOT NULL,
    content_hash CHAR(64) NOT NULL,
    semantic_hash CHAR(64),
    summary TEXT,
    content LONGTEXT,
    author VARCHAR(255),
    published_at DATETIME NULL,
    scraped_at DATETIME NOT NULL,
    language VARCHAR(20),
    sentiment VARCHAR(50),
    sentiment_score FLOAT,
    embedding_status TINYINT DEFAULT 0,
    semantic_duplicate TINYINT DEFAULT 0,
    raw_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_url_hash (url_hash),
    UNIQUE KEY uq_source_content_hash (source, content_hash),
    INDEX idx_source (source),
    INDEX idx_published_at (published_at),
    INDEX idx_embedding_status (embedding_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

`embedding_status` values:

- `0`: pending
- `1`: processing
- `2`: embedded
- `3`: semantic duplicate
- `4`: failed

## ChromaDB Setup

ChromaDB is persistent and local by default:

```env
CHROMA_DB_PATH=./chroma_db
SEMANTIC_DUPLICATE_THRESHOLD=0.92
```

The collection is:

```text
market_news_embeddings
```

It stores normalized embeddings plus article metadata: article id, source, URL, timestamp, language, and sentiment placeholders.

## Scraper Design

All scrapers inherit `BaseScraper` and implement:

- `source_name`
- `start_urls`
- `scrape()`
- `parse_article()`
- `normalize()`
- `validate()`

The base class provides:

- Async Playwright Chromium
- Reusable browser context
- Session state persisted under `cache/`
- Rotating user agents
- Random request pacing
- `robots.txt` checks with TTL cache
- Defensive BeautifulSoup parsing
- Fallback selectors
- Raw HTML snapshots under `storage/raw/<source>/`
- Source and article-level exception isolation

## Normalized Output

Every scraper emits:

```json
{
  "source": "moneycontrol",
  "title": "Example title",
  "url": "https://example.com/news/article",
  "summary": null,
  "content": null,
  "author": null,
  "published_at": null,
  "scraped_at": "2026-05-19T00:00:00+00:00",
  "tags": [],
  "language": "en",
  "url_hash": "sha256",
  "content_hash": "sha256",
  "semantic_hash": "sha256"
}
```

## Anti-Blocking Design

This system uses safe, ethical controls only:

- Public pages only
- `robots.txt` respected
- Random polling interval from 120 to 300 seconds
- Per-request randomized delay
- Browser context reuse
- Session persistence
- Exponential source retry
- Aggressive backoff for `403` and `429`

It does not bypass CAPTCHAs, login walls, paywalls, or access protections. It does not use illegal proxies or hammer endpoints.

## Dedupe Design

Duplicate suppression has three layers:

1. Exact URL dedupe via normalized URL SHA256.
2. Exact content dedupe via normalized content SHA256 scoped by source.
3. Semantic duplicate detection via `sentence-transformers/all-MiniLM-L6-v2` and ChromaDB cosine similarity.

URL normalization removes query parameters and fragments, removes trailing slashes, and lowercases hostnames.

Semantic duplicate rule:

```text
similarity > 0.92
```

Semantic duplicates are marked in MySQL and are not inserted into ChromaDB again.

## Embedding Worker

Embeddings are not generated inside the scraper pipeline.

Flow:

```text
Scraper -> MySQL insert -> embedding_status=0
EmbeddingWorker -> embedding_status=1
Semantic duplicate check
ChromaDB upsert for non-duplicates
embedding_status=2
```

This keeps scraping latency separate from model latency and makes the design queue-ready for Redis or Kafka.

## Adding New Sources

Create a new file in `sources/` and inherit `BaseScraper`.

Implement the required methods and override selector tuples:

- `article_link_selectors`
- `title_selectors`
- `summary_selectors`
- `author_selectors`
- `published_selectors`
- `content_selectors`
- `tag_selectors`

Add the scraper to `main.py`.

## Scaling Strategy

Near-term scaling:

- Run scraper and embedding worker as separate processes.
- Replace MySQL polling with Redis queues.
- Partition source schedulers by source.
- Use one ChromaDB collection per content class if retrieval quality requires it.

Institutional extensions:

- Kafka topic per normalized news event.
- FinBERT sentiment worker.
- Ticker extraction and symbol normalization.
- Event memory and sector clustering.
- Websocket dashboards.
- Alert and signal engine.
- Market regime detection over rolling event embeddings.

## Tests

```bash
pytest
```

Covered:

- URL normalization
- Text/content hashing
- Exact dedupe
- Semantic threshold behavior
- Normalization helpers
- Parser candidate extraction
- Chroma distance-to-similarity conversion

## Environment

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=stock_user
MYSQL_PASSWORD=change_me
MYSQL_DATABASE=stock_news

HEADLESS=true
SCRAPE_INTERVAL_MIN=120
SCRAPE_INTERVAL_MAX=300

MAX_RETRIES=5
TIMEOUT_SECONDS=60

CHROMA_DB_PATH=./chroma_db
SEMANTIC_DUPLICATE_THRESHOLD=0.92
```

## Operational Notes

- Start with Moneycontrol enabled if validating selectors in a new environment, then enable all sources.
- Monitor logs for `robots_disallowed`, `rate_or_access_limited`, and `source_cycle_failed`.
- Keep polling conservative. Market news pages often cache aggressively and do not require second-level scraping.
- Revisit selectors periodically. News websites change markup without notice.
