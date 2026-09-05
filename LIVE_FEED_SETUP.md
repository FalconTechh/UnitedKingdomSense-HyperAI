# Hyper AI live-feed setup

This version removes the synthetic/demo candle generator. It will only analyze candles returned by an authorized data feed.

## Render settings

Build:
`pip install -r requirements.txt`

Start:
`uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

Root Directory: blank

## Required Environment Variables

`OTC_FEED_URL` = HTTPS endpoint supplied by your authorized broker/data provider.

Optional:
`OTC_FEED_TOKEN` = bearer token if the provider requires one
`OTC_FEED_TIMEOUT` = request timeout in seconds (default 8)

The endpoint is called with:
`?pair=EURUSD-OTC&timeframe=1m&limit=180`

Expected JSON:
`{"candles":[{"timestamp":1720000000,"open":1.1,"high":1.101,"low":1.099,"close":1.1005,"volume":10}]}`

The frontend supports pair/timeframe selection and animated scan states. If no authorized feed is configured, it shows FEED OFFLINE rather than inventing market data.

Important: OTC prices are broker/provider-specific. A normal forex price API is not automatically the same as a broker's OTC feed.
