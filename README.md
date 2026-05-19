# StratFusion Market Intelligence

StratFusion is an adaptive Indian market-intelligence platform with five production-oriented modules:

1. **Web & News Market Intelligence**
   Real-time ethical news ingestion, duplicate suppression, semantic event detection, MySQL storage, embeddings, and ChromaDB vector search.

2. **AI Algo Trading Lab**
   Adaptive multi-strategy trading intelligence with independent strategy engines, regime-aware ensemble weighting, risk controls, backtesting, accuracy tracking, custom strategy building, and FastAPI dashboard endpoints.

3. **Adaptive AI/ML Intelligence Layer**
   Advanced feature engineering, FinBERT sentiment, regime intelligence, anomaly detection, dynamic strategy-weight learning, market memory, training pipelines, and safe adaptive-learning foundations.

4. **Platform Gateway**
   Unified orchestration API that connects scraper news storage, Adaptive AI outputs, and Algo Trading Lab guidance into one dashboard-ready pipeline.

5. **Dashboard Web**
   Static operating console for Web & News Market Intelligence and the AI Algo Trading Lab.

The platform is intentionally not a simple AI stock predictor. AI is one intelligence layer inside a broader system of market data, news intelligence, algorithms, regime detection, and risk management.

## Modules

## Target Architecture

```text
Market Data / News Scrapers
        |
        v
Kafka Event Bus
        |
        v
Data Quality Layer
        |
        v
Feature Store
        |
        v
Adaptive AI Layer
        |
        v
Regime Engine
        |
        v
Strategy Engines
        |
        v
Dynamic Weight Engine
        |
        v
Risk Engine
        |
        v
Signal Orchestrator
        |
        v
Platform Gateway
        |
        v
Dashboard Web
```

The current repository now supports this architecture with Kafka-ready event contracts, optional Kafka producers/consumers, data quality validation, feature-store interfaces, model lifecycle management, signal lifecycle orchestration, and dashboard-ready gateway APIs.

### `scraper_engine/`

Indian stock-market news ingestion and semantic intelligence engine.

Key features:

- Async Playwright scrapers for Moneycontrol, CNBC TV18, ET Markets, NDTV Profit, and CNBC Awaaz
- Public-page-only ethical scraping with robots.txt checks, pacing, retry, and backoff
- Normalized news schema
- MySQL 8 storage
- Exact URL/content dedupe
- ChromaDB semantic duplicate detection
- Sentence-transformer embedding worker
- Semantic similarity engine
- Kafka-ready publishing hooks for `news.raw` and `news.cleaned`
- Data quality checks and source reliability scoring

Read the full module guide:

[scraper_engine/README.md](scraper_engine/README.md)

### `algo_trading_lab/`

Adaptive Quant Intelligence module for probability-based trading guidance.

Key features:

- Normalized OHLCV, sentiment, and options-chain inputs
- Momentum, mean-reversion, volatility, statistical, and AI/ML-ready strategies
- Market regime detection
- Dynamic ensemble weighting
- Risk engine with stop loss, target, position sizing, and signal overrides
- Backtesting and accuracy tracking
- Custom strategy builder
- FastAPI dashboard API
- Shared execution context for `BACKTEST`, `PAPER`, and `LIVE_SIMULATION`
- Strategy runner reused across execution modes
- Risk gatekeeper that can downgrade or block unsafe signals

Read the full module guide:

[algo_trading_lab/README.md](algo_trading_lab/README.md)

### `adaptive_ai_layer/`

Adaptive AI/ML intelligence module for knowing when to trust which strategy.

Key features:

- Volatility, momentum, sentiment, options, correlation, regime, and anomaly features
- FinBERT batch sentiment service with calibration and event extraction
- Rule-based regime engine plus XGBoost and HDBSCAN/KMeans interfaces
- Dynamic strategy weighting using regime, sentiment, volatility, anomalies, risk, and performance memory
- Isolation Forest, z-score, divergence, and fake-breakout anomaly detection
- Walk-forward training pipeline with model registry and evaluation
- Strategy performance memory and paper-trading feedback loop
- FastAPI endpoints for features, sentiment, regime, anomaly, weighting, training, models, memory, and feedback
- Central feature store with definitions, versions, freshness, latest serving, and historical lookup
- MLOps registry, model versions, training run tracker, evaluation store, prediction logs, and rollback
- Persistent intelligence memory contracts

Read the full module guide:

[adaptive_ai_layer/README.md](adaptive_ai_layer/README.md)

### `platform_gateway/`

Connection layer for the full platform.

Key features:

- Health checks across gateway, Adaptive AI, Algo Lab, and scraper news storage
- Latest stored scraper news endpoint
- Unified `/pipeline/run` endpoint
- FinBERT sentiment -> regime -> anomaly -> weighting -> strategy/risk guidance orchestration
- CORS enabled for the dashboard
- Signal orchestrator with lifecycle states, dependency checks, audit trail, metrics, and final event publishing
- Pipeline status, deep health, metrics, symbol APIs, and websocket stream endpoints

Read the full module guide:

[platform_gateway/README.md](platform_gateway/README.md)

### `dashboard_web/`

Static dashboard UI for the platform.

Key features:

- Service status band
- Web & News Market Intelligence section
- AI Algo Trading Lab section
- Symbol, capital, risk, and headline controls
- Canvas market visualization
- Pipeline execution from the browser
- Strategy weights, risk guidance, probabilities, news, and explanations

Read the full module guide:

[dashboard_web/README.md](dashboard_web/README.md)

## Quick Start

Clone the repo:

```bash
git clone https://github.com/xyberpunk/Stratfusion-market-intelligence.git
cd Stratfusion-market-intelligence
```

Run the news intelligence engine:

```bash
cd scraper_engine
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
python main.py
```

Run the Algo Trading Lab API:

```bash
cd algo_trading_lab
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

Run the Adaptive AI/ML Intelligence Layer:

```bash
cd adaptive_ai_layer
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

Run the Platform Gateway:

```bash
cd platform_gateway
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

Run the dashboard:

```bash
cd dashboard_web
python -m http.server 8060
```

API docs:

```text
Algo Trading Lab: http://127.0.0.1:8080/docs
Adaptive AI Layer: http://127.0.0.1:8090/docs
Platform Gateway: http://127.0.0.1:8070/docs
Dashboard: http://127.0.0.1:8060
```

## Kafka Topics

```text
news.raw
news.cleaned
news.sentiment.completed
market.ohlcv.raw
market.options.raw
features.generated
regime.detected
strategy.signal.generated
ensemble.signal.generated
risk.evaluated
final.signal.generated
anomaly.detected
model.prediction.generated
system.dead_letter
system.health
```

Every event uses the shared envelope:

```json
{
  "event_id": "uuid",
  "event_type": "news.raw",
  "source": "scraper_engine",
  "timestamp": "2026-05-19T00:00:00Z",
  "symbol": "INFY",
  "correlation_id": "uuid",
  "payload": {},
  "schema_version": "1.0"
}
```

## Signal Lifecycle

The gateway orchestrator tracks every signal through:

```text
CREATED
DATA_COLLECTED
FEATURES_READY
REGIME_READY
STRATEGIES_READY
ENSEMBLE_READY
RISK_READY
FINALIZED
FAILED
EXPIRED
```

The orchestrator refuses to publish `final.signal.generated` until required dependencies are complete.

## Docker Compose

The repository includes `docker-compose.yml` for:

- MySQL
- Kafka
- Zookeeper
- scraper_engine
- adaptive_ai_layer
- algo_trading_lab
- platform_gateway
- dashboard_web

Run:

```bash
docker compose up --build
```

Dashboard:

```text
http://127.0.0.1:8060
```

Gateway:

```text
http://127.0.0.1:8070/docs
```

## Observability

Shared observability primitives include:

- structlog configuration
- correlation id propagation
- in-memory metrics registry
- latency timing
- component health snapshots
- audit records

Gateway endpoints:

```text
GET /health
GET /health/deep
GET /metrics
GET /pipeline/status/{correlation_id}
```

## Production Scaling Roadmap

- Move all service-to-service handoffs from HTTP orchestration to Kafka consumers.
- Persist orchestrator state and audit logs in MySQL.
- Promote feature store from in-memory serving to MySQL-backed online/offline serving.
- Add consumer lag monitoring and dead-letter replay tooling.
- Add authentication and rate limits at `platform_gateway`.
- Split model training into asynchronous jobs.
- Add CI that runs tests per module with isolated `PYTHONPATH`.
- Add schema compatibility checks for event versions.

## Safety Policy

The platform returns probability-based intelligence and risk-aware guidance. It must not use guarantee language.

Allowed:

- “Bullish probability: 74%”
- “Suggested action: BUY”
- “Risk level: MODERATE”
- “Signal supported by 4 out of 5 engines”

Forbidden:

- “AI guarantees stock will rise”
- “Sure-shot buy”
- “Guaranteed profit”
- “Risk-free trade”

## Repository Layout

```text
.
├── scraper_engine/
│   ├── sources/
│   ├── workers/
│   ├── utils/
│   └── tests/
│
├── algo_trading_lab/
│   ├── data/
│   ├── strategies/
│   ├── regime/
│   ├── ensemble/
│   ├── risk/
│   ├── backtesting/
│   ├── accuracy/
│   ├── custom_builder/
│   ├── ai/
│   ├── api/
│   └── tests/
│
├── adaptive_ai_layer/
│   ├── features/
│   ├── datasets/
│   ├── training/
│   ├── regime/
│   ├── weighting/
│   ├── anomaly/
│   ├── sentiment/
│   ├── memory/
│   ├── adaptive_learning/
│   ├── api/
│   └── tests/
│
├── platform_gateway/
│   ├── api/
│   ├── clients/
│   ├── models/
│   ├── storage/
│   └── tests/
│
├── dashboard_web/
│   ├── assets/
│   └── samples/
│
└── README.md
```

## Status

This repository contains the initial production-grade scaffold and working core logic for both modules. Configure `.env` files before running live MySQL-backed ingestion or APIs.
