from __future__ import annotations
import random, time
from dataclasses import dataclass

@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

class DemoAdapter:
    """Replace this adapter with a permitted/authorized OTC feed.

    The demo adapter exists only to make the project immediately runnable.
    It must never be presented as real Quotex/OTC market data.
    """
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.price = 1.1000
        self.candles = []

    def get_candles(self, limit=180):
        now = int(time.time())
        if not self.candles:
            p = self.price
            for i in range(limit):
                drift = self.rng.gauss(0, 0.00035)
                o = p
                c = max(0.0001, p + drift)
                h = max(o, c) + abs(self.rng.gauss(0, 0.00012))
                l = min(o, c) - abs(self.rng.gauss(0, 0.00012))
                self.candles.append(Candle(now - (limit-i)*60, o, h, l, c, self.rng.uniform(10, 100)))
                p = c
            self.price = p
        return self.candles[-limit:]
