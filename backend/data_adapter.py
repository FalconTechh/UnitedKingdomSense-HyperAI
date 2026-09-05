from __future__ import annotations
import os, time, json
from dataclasses import dataclass
from urllib.request import Request, urlopen
from urllib.parse import urlencode

@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

class FeedError(RuntimeError):
    pass

class AuthorizedOTCAdapter:
    """
    Reads candles from an authorized broker/data-provider HTTP endpoint.

    Required environment variable:
      OTC_FEED_URL=https://your-authorized-provider.example/candles

    Optional:
      OTC_FEED_TOKEN=...
      OTC_FEED_TIMEOUT=8

    The endpoint may return either:
      {"candles":[{"timestamp":..., "open":..., "high":..., "low":..., "close":..., "volume":...}]}
    or a plain list of candle objects.

    No synthetic/fake candles are generated. If the feed is unavailable,
    the API returns a clear feed error instead of pretending the data is live.
    """
    def __init__(self):
        self.base_url = os.getenv("OTC_FEED_URL", "").strip()
        self.token = os.getenv("OTC_FEED_TOKEN", "").strip()
        self.timeout = float(os.getenv("OTC_FEED_TIMEOUT", "8"))

    def get_candles(self, pair="EURUSD-OTC", timeframe="1m", limit=180):
        if not self.base_url:
            raise FeedError("OTC_FEED_URL is not configured. Add your authorized OTC feed in Render Environment.")
        query = urlencode({"pair": pair, "timeframe": timeframe, "limit": limit})
        url = self.base_url + ("&" if "?" in self.base_url else "?") + query
        headers = {"Accept": "application/json", "User-Agent": "UKSense-HyperAI/2.0"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = Request(url, headers=headers, method="GET")
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise FeedError(f"Live feed request failed: {e}") from e

        rows = payload.get("candles") if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise FeedError("Feed response must contain a 'candles' array or be a candle array.")

        candles=[]
        for row in rows[-limit:]:
            try:
                ts = row.get("timestamp", row.get("time"))
                if isinstance(ts, str):
                    ts = int(float(ts))
                ts = int(ts)
                # Accept either epoch seconds or epoch milliseconds.
                if ts > 10_000_000_000:
                    ts //= 1000
                candles.append(Candle(
                    timestamp=ts,
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume", 0) or 0),
                ))
            except Exception as e:
                raise FeedError(f"Invalid candle in feed response: {e}") from e

        if len(candles) < 40:
            raise FeedError(f"Feed returned only {len(candles)} candles; at least 40 are required.")
        return candles
