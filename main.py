from __future__ import annotations
import asyncio, os, time
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .data_adapter import DemoAdapter
from .engine import analyze

app = FastAPI(title="United Kingdom Sense Hyper AI")
adapter = DemoAdapter()

BASE = os.path.dirname(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "frontend")), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "frontend", "index.html"))

@app.get("/api/health")
def health():
    return {"status":"online","data_mode":"DEMO_ADAPTER","engine":"hyper-ai"}

@app.get("/api/signal")
def signal():
    candles = adapter.get_candles(180)
    result = analyze(candles)
    return {"pair":"EURUSD-OTC","timeframe":"1m","mode":"DEMO","engine":"HYPER AI",**result}

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            candles = adapter.get_candles(180)
            result = analyze(candles)
            await ws.send_json({
                "pair":"EURUSD-OTC","timeframe":"1m",
                "mode":"DEMO — CONNECT YOUR AUTHORIZED OTC FEED",
                "engine":"HYPER AI",
                **result
            })
            await asyncio.sleep(3)
    except Exception:
        await ws.close()
