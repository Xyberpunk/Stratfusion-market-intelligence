# Algo Trading Lab

Adaptive multi-strategy trading intelligence module for an Adaptive Quant Intelligence Platform.

This is not an AI stock predictor. AI is one scoring layer inside a broader ensemble that also includes technical strategies, options positioning, regime detection, accuracy tracking, and risk controls.

Allowed platform language:

```text
Combined market intelligence suggests bullish probability.
```

Forbidden platform language:

```text
AI guarantees stock will rise.
Sure-shot buy.
Guaranteed profit.
Risk-free trade.
```

## Architecture

```text
Market Data + News Sentiment + Options Chain
        |
        v
Data Normalization + Feature Builder
        |
        v
Independent Strategy Engines
        |
        v
Regime Detection Engine
        |
        v
Dynamic Weight Manager
        |
        v
Ensemble Probability Engine
        |
        v
Risk Engine Overrides
        |
        v
Dashboard API Responses
```

## Setup

Python 3.11 is supported for your current environment.

```bash
cd algo_trading_lab
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

API runs by default at:

```text
http://127.0.0.1:8080
```

OpenAPI docs:

```text
http://127.0.0.1:8080/docs
```

## Main Modules

- Data Layer: normalized OHLCV, NSEPython snapshot adapter, options-chain normalization, sentiment aggregation, feature building.
- Strategy Layer: independent momentum, mean-reversion, volatility, statistical, and AI/ML-ready strategies.
- Regime Engine: trend, volatility, liquidity, panic, bullish, bearish, sideways detection.
- Ensemble Engine: static, user, regime, accuracy, and confidence-based weighting.
- Risk Engine: stop loss, target, position sizing, risk/reward, drawdown controls, final action overrides.
- Backtesting Engine: single-strategy backtests with win rate, profit factor, max drawdown, average return, and Sharpe-ready stats.
- Accuracy Tracking: strategy performance by symbol, regime, timeframe, and sample size.
- Custom Strategy Builder: user-selected strategy combinations with weight caps.
- AI Assistance Layer: sentiment strategies, anomaly detection, and advisory weight tilts.
- Dashboard API: frontend-ready endpoints for the Algo Trading Lab.

## API Endpoints

```text
GET  /strategies
POST /strategies/custom
GET  /strategies/custom
POST /signals/generate
POST /backtest/run
GET  /backtest/results/{id}
GET  /accuracy/strategy/{strategy_name}
GET  /regime/{symbol}
GET  /risk/{symbol}
POST /ensemble/run
```

## Example Custom Strategy

```json
{
  "name": "My Adaptive NIFTY Strategy",
  "strategies": [
    {"name": "RSI Reversal", "weight": 0.10},
    {"name": "MACD Momentum", "weight": 0.15},
    {"name": "VWAP", "weight": 0.20},
    {"name": "FinBERT Sentiment", "weight": 0.25},
    {"name": "Options Chain PCR", "weight": 0.30}
  ],
  "risk_profile": "moderate",
  "dynamic_weighting": true
}
```

## MySQL

MySQL is optional at runtime by default:

```env
MYSQL_ENABLED=false
```

Set `MYSQL_ENABLED=true` to initialize the production tables:

- `strategy_definitions`
- `strategy_signals`
- `ensemble_signals`
- `regime_snapshots`
- `risk_outputs`
- `backtest_runs`
- `backtest_results`
- `strategy_accuracy`
- `custom_strategies`
- `anomaly_events`

Indexes are defined on `symbol`, `timestamp`, `strategy_name`, `regime`, `signal`, and `created_at` where relevant.

## Dashboard Sections

The API is prepared for two frontend sections:

- Web & News Market Intelligence
- AI Algo Trading Lab

The Algo Trading Lab responses include final action, bullish/bearish/neutral probabilities, risk score, stop loss, target, strategy breakdown, anomalies, and regime context.

## Tests

```bash
pytest
```

Covered:

- Strategy signal generation
- Regime detection
- Ensemble probability output
- Risk engine stop/target/final action
- Backtesting metrics
- Custom strategy validation
