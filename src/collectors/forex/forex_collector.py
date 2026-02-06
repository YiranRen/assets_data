"""
外汇：yfinance 取主要货币对兑人民币（CNY）。
"""
from typing import List

import yfinance as yf

from ...models import AssetRecord
from ..base import BaseCollector

# yfinance 中兑人民币的代码
PAIRS = [
    ("USDCNY=X", "美元", "USD"),
    ("EURCNY=X", "欧元", "EUR"),
    ("GBPCNY=X", "英镑", "GBP"),
    ("JPYCNY=X", "日元", "JPY"),
    ("HKDCNY=X", "港币", "HKD"),
]


def _safe_float(v, default: float = 0.0) -> float:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class ForexCollector(BaseCollector):
    category = "外汇"

    def collect(self) -> List[AssetRecord]:
        result: List[AssetRecord] = []
        for symbol, name, _ in PAIRS:
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
                change_24h = None
                if prev and prev > 0:
                    change_24h = (price - prev) / prev * 100
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
                        price=round(price, 4),
                        unit="¥",
                        currency="CNY",
                        change_24h=change_24h,
                        change_7d=change_7d,
                        source="yfinance",
                    )
                )
            except Exception:
                continue
        return result
