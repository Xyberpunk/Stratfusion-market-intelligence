# Adaptive AI/ML Intelligence Layer

Advanced adaptive intelligence module for StratFusion Market Intelligence.

This module is not a stock predictor. It answers:

- What kind of market are we in?
- Which strategies deserve more trust right now?
- Which strategies work best under which market conditions?
- When should strategy weights increase or decrease?
- When is market behavior abnormal?
- How should sentiment, volatility, options data, and technical signals affect decisions?

AI is one intelligence layer, one scoring source, and one adaptive component. It does not override risk controls or claim certainty.

## Architecture

```text
News Scraper
        |
        v
FinBERT Sentiment
        |
        v
Market Feature Builder
        |
        v
Regime Detection
        |
        v
Dynamic Strategy Weighting
        |
        v
Strategy Ensemble
        |
        v
Risk Engine
        |
        v
Final Probability-Based Signal
```

## Modules

- `features/`: volatility, momentum, sentiment, options, correlation, regime, and anomaly features
- `datasets/`: Financial PhraseBank, Yahoo Finance, NSE CSV, Kaggle OHLCV loaders
- `training/`: label building, target engineering, walk-forward validation, model evaluation, persistence
- `regime/`: rule-based regime detection, XGBoost interface, KMeans/HDBSCAN clustering interface
- `weighting/`: rule-based, accuracy-based, AI-assisted, and bandit-ready weighting
- `anomaly/`: z-score, divergence, fake-breakout, and Isolation Forest detectors
- `sentiment/`: FinBERT batch inference, calibration, aggregation, event extraction
- `memory/`: performance, regime, anomaly, and paper-feedback memory
- `adaptive_learning/`: reward engine, safe bandit selector, online-learning interface
- `api/`: FastAPI endpoints
- `storage/`: MySQL migrations and optional persistence adapter

## Setup

```bash
cd adaptive_ai_layer
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

For your current Windows setup with Python 3.11 installed, the code is also compatible:

```bash
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

API docs:

```text
http://127.0.0.1:8090/docs
```

## API

```text
POST /features/build
POST /sentiment/finbert/batch
POST /regime/detect
POST /anomaly/detect
POST /weighting/suggest
POST /training/run
GET  /models
GET  /memory/strategy/{strategy_name}
POST /feedback/paper-trade
```

## FinBERT

By default:

```env
FINBERT_ENABLED=false
```

The service then uses a deterministic lexical fallback for local development and tests. To run true FinBERT inference:

```env
FINBERT_ENABLED=true
FINBERT_MODEL_NAME=ProsusAI/finbert
```

Endpoint output:

```json
{
  "text": "Infosys raises guidance",
  "symbol": "INFY",
  "sentiment": "bullish",
  "confidence": 0.91,
  "raw_scores": {"positive": 0.91, "negative": 0.03, "neutral": 0.06},
  "event_type": "guidance",
  "timestamp": "2026-05-19T00:00:00Z"
}
```

## Regime Detection

Initial regime detection is intentionally transparent and rule-based. Interfaces are included for XGBoost and clustering-based discovery.

Detected regimes:

- `TRENDING`
- `SIDEWAYS`
- `PANIC`
- `LOW_LIQUIDITY`
- `HIGH_VOLATILITY`
- `BULLISH_REGIME`
- `BEARISH_REGIME`
- `RISK_ON`
- `RISK_OFF`

Each output includes features and an explanation.

## Dynamic Weighting

Initial weighting uses transparent rules:

- Trending markets increase momentum, breakout, VWAP, and MACD trust.
- Sideways markets increase RSI, Bollinger, and mean-reversion trust.
- Panic or risk-off markets increase volatility, sentiment, and risk-aware systems.
- Historical performance memory adjusts strategy trust by regime, symbol, sector, and volatility bucket.

Bandit and online-learning interfaces are research-only foundations. They do not place trades.

## MySQL

MySQL is optional by default:

```env
MYSQL_ENABLED=false
```

When enabled, migrations create:

- `ml_features`
- `training_runs`
- `model_registry`
- `model_predictions`
- `regime_snapshots`
- `anomaly_events`
- `sentiment_outputs`
- `strategy_performance_memory`
- `dynamic_weight_snapshots`
- `adaptive_rewards`
- `paper_feedback`

Migration SQL is in [storage/migrations.sql](storage/migrations.sql).

## Tests

```bash
pytest
```

Covered:

- Feature engineering
- Regime detection
- Dynamic weighting
- Anomaly detection
- FinBERT service fallback
- Walk-forward validation
- Market memory

## Safety

The module produces explanations and adaptive intelligence. It must not claim certainty.

Allowed:

- “Market classified as TRENDING with 82% confidence.”
- “Momentum strategies were increased because regime is TRENDING.”
- “Combined market intelligence suggests bullish probability.”

Forbidden:

- “AI guarantees stock will rise.”
- “Sure-shot buy.”
- “Guaranteed profit.”
- “Risk-free trade.”
