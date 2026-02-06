"""
美股、日股采集：Yahoo Finance (yfinance)。
"""
from typing import List, Optional

import yfinance as yf

from ...models import AssetRecord
from ..base import BaseCollector


def _safe_float(v, default: float = 0.0) -> float:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _fetch_yf(symbol: str) -> Optional[dict]:
    try:
        t = yf.Ticker(symbol)
        info = t.info
        hist = t.history(period="7d")
        if info is None or info.get("regularMarketPrice") is None:
            if hist is not None and not hist.empty:
                info = info or {}
                info["regularMarketPrice"] = float(hist["Close"].iloc[-1])
                info["shortName"] = symbol
                info["regularMarketChangePercent"] = None
                info["regularMarketPreviousClose"] = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else None
            else:
                return None
        price = _safe_float(info.get("regularMarketPrice"), 0)
        if price <= 0:
            return None
        prev = _safe_float(info.get("regularMarketPreviousClose"), 0)
        change_pct = info.get("regularMarketChangePercent")
        if change_pct is not None:
            change_24h = _safe_float(change_pct, 0)
        elif prev and prev > 0:
            change_24h = (price - prev) / prev * 100
        else:
            change_24h = None
        change_7d = None
        if hist is not None and len(hist) >= 2:
            old = float(hist["Close"].iloc[0])
            if old and old > 0:
                change_7d = (price - old) / old * 100
        return {
            "price": price,
            "name": (info.get("shortName") or info.get("longName") or symbol).strip(),
            "change_24h": change_24h,
            "change_7d": change_7d,
        }
    except Exception:
        return None


class YFinanceUSCollector(BaseCollector):
    """美股采集（yfinance）：美股七姐妹 + VOO"""

    category = "美股"

    # 美股七姐妹 + VOO
    DEFAULT_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "VOO"]
    NAME_MAP = {
        "AAPL": "苹果",
        "MSFT": "微软",
        "GOOGL": "谷歌",
        "AMZN": "亚马逊",
        "NVDA": "英伟达",
        "META": "Meta",
        "TSLA": "特斯拉",
        "VOO": "Vanguard标普500ETF",
    }

    def collect(self) -> List[AssetRecord]:
        result: List[AssetRecord] = []
        for sym in self.DEFAULT_SYMBOLS:
            data = _fetch_yf(sym)
            if not data:
                continue
            name = self.NAME_MAP.get(sym) or data["name"]
            result.append(
                AssetRecord(
                    category=self.category,
                    symbol=sym,
                    name=name,
                    price=data["price"],
                    unit="$",
                    currency="USD",
                    change_24h=data.get("change_24h"),
                    change_7d=data.get("change_7d"),
                    source="yfinance",
                )
            )
        return result


class YFinanceJapanCollector(BaseCollector):
    """日股采集（yfinance）：五大商社 + 日经指数"""

    category = "日股"
    DEFAULT_SYMBOLS = ["8058.T", "8031.T", "8053.T", "8001.T", "8068.T", "^N225"]
    NAME_MAP = {
        "8058.T": "三菱商事",
        "8031.T": "三井物产",
        "8053.T": "住友商事",
        "8001.T": "伊藤忠商事",
        "8068.T": "丸红",
        "^N225": "日经指数",
    }

    def collect(self) -> List[AssetRecord]:
        result: List[AssetRecord] = []
        for sym in self.DEFAULT_SYMBOLS:
            data = _fetch_yf(sym)
            if not data:
                continue
            name = self.NAME_MAP.get(sym) or data["name"]
            result.append(
                AssetRecord(
                    category=self.category,
                    symbol=sym,
                    name=name,
                    price=data["price"],
                    unit="¥",
                    currency="JPY",
                    change_24h=data.get("change_24h"),
                    change_7d=data.get("change_7d"),
                    source="yfinance",
                )
            )
        return result
