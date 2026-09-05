from __future__ import annotations
import asyncio, os
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .data_adapter import AuthorizedOTCAdapter, FeedError
from .engine import analyze

app = FastAPI(title="United Kingdom Sense Hyper AI")
adapter = AuthorizedOTCAdapter()

BASE = os.path.dirname(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "frontend")), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "frontend", "index.html"))

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "data_mode": "AUTHORIZED_LIVE_FEED",
        "feed_configured": bool(os.getenv("OTC_FEED_URL")),
        "engine": "hyper-ai"
    }

def get_result(pair="EURUSD-OTC", timeframe="1m"):
    candles = adapter.get_candles(pair=pair, timeframe=timeframe, limit=180)
    result = analyze(candles)
    return {
        "pair": pair,
        "timeframe": timeframe,
        "mode": "LIVE_AUTHORIZED_FEED",
        "engine": "HYPER AI",
        **result
    }

@app.get("/api/signal")
def signal(pair: str = "EURUSD-OTC", timeframe: str = "1m"):
    try:
        return get_result(pair, timeframe)
    except FeedError as e:
        return {"ok": False, "error": str(e), "signal": "FEED OFFLINE", "confidence": 0}

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    pair = "EURUSD-OTC"
    timeframe = "1m"
    try:
        while True:
            try:
                await ws.send_json({"type":"scan_start","pair":pair,"timeframe":timeframe})
                result = get_result(pair, timeframe)
                await ws.send_json({"type":"signal","ok":True,**result})
            except FeedError as e:
                await ws.send_json({
                    "type":"signal","ok":False,"signal":"FEED OFFLINE",
                    "confidence":0,"quality":"NO DATA","error":str(e),
                    "pair":pair,"timeframe":timeframe
                })
            await asyncio.sleep(3)
    except Exception:
        await ws.close()
