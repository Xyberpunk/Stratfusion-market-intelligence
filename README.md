# StratFusion Market Intelligence

StratFusion is an adaptive Indian market-intelligence platform with three production-oriented modules:

1. **Web & News Market Intelligence**
   Real-time ethical news ingestion, duplicate suppression, semantic event detection, MySQL storage, embeddings, and ChromaDB vector search.

2. **AI Algo Trading Lab**
   Adaptive multi-strategy trading intelligence with independent strategy engines, regime-aware ensemble weighting, risk controls, backtesting, accuracy tracking, custom strategy building, and FastAPI dashboard endpoints.

3. **Adaptive AI/ML Intelligence Layer**
   Advanced feature engineering, FinBERT sentiment, regime intelligence, anomaly detection, dynamic strategy-weight learning, market memory, training pipelines, and safe adaptive-learning foundations.

The platform is intentionally not a simple AI stock predictor. AI is one intelligence layer inside a broader system of market data, news intelligence, algorithms, regime detection, and risk management.

## Modules

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

Read the full module guide:

[adaptive_ai_layer/README.md](adaptive_ai_layer/README.md)

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

API docs:

```text
Algo Trading Lab: http://127.0.0.1:8080/docs
Adaptive AI Layer: http://127.0.0.1:8090/docs
```

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
└── README.md
```

## Status

This repository contains the initial production-grade scaffold and working core logic for both modules. Configure `.env` files before running live MySQL-backed ingestion or APIs.
