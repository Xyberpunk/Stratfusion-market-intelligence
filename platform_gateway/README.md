# StratFusion Platform Gateway

Unified orchestration API that connects:

- `scraper_engine`: latest stored market news from MySQL
- `adaptive_ai_layer`: FinBERT sentiment, regime detection, anomaly detection, dynamic weighting
- `algo_trading_lab`: strategy ensemble and risk-aware trading guidance

## Run

```bash
cd platform_gateway
py -3.11 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

Default URL:

```text
http://127.0.0.1:8070/docs
```

## Required Backend Services

Start these in separate terminals:

```bash
cd adaptive_ai_layer
source .venv/Scripts/activate
python main.py
```

```bash
cd algo_trading_lab
source .venv/Scripts/activate
python main.py
```

The scraper news store is optional. Enable it with:

```env
SCRAPER_MYSQL_ENABLED=true
```

## Endpoints

```text
GET  /platform/status
GET  /news/latest
GET  /strategies
POST /pipeline/run
```

`POST /pipeline/run` executes:

```text
FinBERT sentiment
    -> regime detection
    -> anomaly detection
    -> dynamic weighting
    -> Algo Lab signal generation
    -> latest scraper news
```

The response is dashboard-ready and keeps final wording probability-based.
