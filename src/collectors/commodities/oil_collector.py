"""
原油：WTI、布伦特（yfinance 期货）。
"""
from typing import List

import yfinance as yf

from ...models import AssetRecord
from ..base import BaseCollector

SYMBOLS = [
    ("CL=F", "WTI原油"),
    ("BZ=F", "布伦特原油"),
]


def _safe_float(v, default: float = 0.0) -> float:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class OilCollector(BaseCollector):
    category = "原油"

    def collect(self) -> List[AssetRecord]:
        result: List[AssetRecord] = []
        for symbol, name in SYMBOLS:
            try:
                t = yf.Ticker(symbol)
                info = t.info
                hist = t.history(period="7d")
                price = _safe_float(info.get("regularMarketPrice"), 0)
                if price <= 0 and hist is not None and not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                if price <= 0:
                    continue
                prev = _safe_float(info.get("regularMarketPreviousClose"), 0)
                change_24h = (price - prev) / prev * 100 if prev and prev > 0 else None
                change_7d = None
                if hist is not None and len(hist) >= 2:
                    old = float(hist["Close"].iloc[0])
                    if old and old > 0:
                        change_7d = (price - old) / old * 100
                result.append(
                    AssetRecord(
                        category=self.category,
                        symbol=symbol,
                        name=name,
                        price=round(price, 2),
                        unit="$",
                        currency="USD",
                        change_24h=change_24h,
                        change_7d=change_7d,
                        source="yfinance",
                    )
                )
            except Exception:
                continue
        return result
