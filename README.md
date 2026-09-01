# United Kingdom Sense — Hyper AI OTC Terminal

A professional black/neon-green OTC next-candle analytics terminal designed for GitHub + Render deployment.

## Important
This project does **not** claim guaranteed or 100% accurate predictions. The prediction engine is a research/analytics engine. For genuine OTC accuracy, connect a permitted/authorized OTC data feed through `backend/data_adapter.py`. Do not enter trading-platform credentials into the frontend.

## Run locally

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Render

Use:
- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

The included engine uses synthetic/demo candles when no external feed is configured. Replace the adapter with your permitted data source before treating results as live OTC data.

## Architecture

Data adapter → candle normalization → feature engine → ensemble scoring → signal validation → WebSocket/API → premium frontend.
