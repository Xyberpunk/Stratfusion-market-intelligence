# StratFusion Dashboard Web

Static dashboard for the full StratFusion platform.

It connects to `platform_gateway` and displays:

- Web & News Market Intelligence
- AI Algo Trading Lab
- Gateway/service status
- Sentiment, regime, anomaly, and weighting results
- Bullish/bearish probabilities
- Final action, risk level, stop loss, target, and strategy breakdown

## Run

No build step is required.

```bash
cd dashboard_web
python -m http.server 8060
```

Open:

```text
http://127.0.0.1:8060
```

The dashboard expects the gateway at:

```text
http://127.0.0.1:8070
```

You can change the gateway URL in the top-right input.

## Full Local Stack

Start each service in its own terminal:

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

```bash
cd platform_gateway
source .venv/Scripts/activate
python main.py
```

```bash
cd dashboard_web
python -m http.server 8060
```

The scraper engine remains a background ingestion worker. When its MySQL database is enabled in `platform_gateway/.env`, the dashboard will show latest stored news from `/news/latest`.
