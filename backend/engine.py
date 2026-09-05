from __future__ import annotations
import math
from statistics import mean
from .data_adapter import Candle

def _closes(cs): return [x.close for x in cs]
def _ema(values, n):
    if not values: return 0
    k = 2/(n+1)
    e = values[0]
    for v in values[1:]: e = v*k + e*(1-k)
    return e

def analyze(candles: list[Candle]) -> dict:
    if len(candles) < 40:
        return {"signal":"WAIT","confidence":50.0,"quality":"LOW","components":{}}

    c = _closes(candles)
    recent = candles[-1]
    ema_fast, ema_slow = _ema(c[-60:], 9), _ema(c[-60:], 21)

    returns = [(c[i]-c[i-1])/max(c[i-1],1e-12) for i in range(1,len(c))]
    vol = mean(abs(x) for x in returns[-20:])
    momentum = (c[-1]-c[-6])/max(c[-6],1e-12)
    body = recent.close-recent.open
    rng = max(recent.high-recent.low, 1e-12)
    structure = body/rng

    trend_score = max(-1,min(1,(ema_fast-ema_slow)/(max(c[-1]*0.001,1e-12))))
    momentum_score = max(-1,min(1,momentum/(max(vol*5,1e-9))))
    structure_score = max(-1,min(1,structure))

    raw = 0.46*trend_score + 0.34*momentum_score + 0.20*structure_score
    direction = "UP" if raw > 0 else "DOWN"
    edge = min(abs(raw), 0.95)
    confidence = 50 + edge*45

    # Low-edge markets are explicitly marked WAIT.
    if confidence < 58:
        signal = "WAIT"
        quality = "LOW"
    elif confidence < 68:
        signal = direction
        quality = "MEDIUM"
    elif confidence < 80:
        signal = direction
        quality = "HIGH"
    else:
        signal = direction
        quality = "VERY HIGH"

    return {
        "signal": signal,
        "confidence": round(confidence, 1),
        "quality": quality,
        "components": {
            "trend": round(50 + trend_score*45, 1),
            "momentum": round(50 + momentum_score*45, 1),
            "structure": round(50 + structure_score*45, 1),
            "volatility": round(max(0, min(100, 100 - vol*100000)), 1),
        },
        "price": recent.close,
        "timestamp": recent.timestamp
    }
