"""
贵金属：优先 Binance 永续（XAUUSDT、XAGUSDT），铂金等用 yfinance ETF（如 PPLT）。
"""
from typing import List, Optional

from ...models import AssetRecord
from ..base import BaseCollector

# 先尝试 ccxt Binance，失败则用 yfinance
def _binance_metal(symbol: str, name: str) -> Optional[AssetRecord]:
    try:
        import ccxt
        exchange = ccxt.binance({"enableRateLimit": True})
        ticker = exchange.fetch_ticker(symbol)
        if not ticker or ticker.get("last") is None:
            return None
        price = float(ticker["last"])
        change_24h = ticker.get("percentage")  # 24h 涨跌幅
        if change_24h is not None:
            change_24h = float(change_24h)
        return AssetRecord(
            category="贵金属",
            symbol=symbol,
            name=name,
            price=price,
            unit="$",
            currency="USD",
            change_24h=change_24h,
            change_7d=None,
            source="binance",
        )
    except Exception:
        return None


def _yf_metal(symbol: str, name: str) -> Optional[AssetRecord]:
    try:
        import yfinance as yf
        t = yf.Ticker(symbol)
        info = t.info
        hist = t.history(period="7d")
        price = info.get("regularMarketPrice")
        if price is None and hist is not None and not hist.empty:
            price = float(hist["Close"].iloc[-1])
        if price is None or float(price) <= 0:
            return None
        price = float(price)
        prev = info.get("regularMarketPreviousClose")
        change_24h = (price - float(prev)) / float(prev) * 100 if prev else None
        change_7d = None
        if hist is not None and len(hist) >= 2:
            old = float(hist["Close"].iloc[0])
            if old > 0:
                change_7d = (price - old) / old * 100
        return AssetRecord(
            category="贵金属",
            symbol=symbol,
            name=name,
            price=round(price, 2),
            unit="$",
            currency="USD",
            change_24h=change_24h,
            change_7d=change_7d,
            source="yfinance",
        )
    except Exception:
        return None


class CommoditiesCollector(BaseCollector):
    category = "贵金属"

    def collect(self) -> List[AssetRecord]:
        result: List[AssetRecord] = []
        # 黄金、白银：Binance 优先
        for sym, name in [("XAU/USDT", "黄金"), ("XAG/USDT", "白银")]:
            r = _binance_metal(sym, name)
            if r:
                r.symbol = name  # 展示用
                result.append(r)
            else:
                # 备用：yfinance 黄金/白银 ETF 或现货代码
                yf_sym = "GC=F" if "黄金" in name else "SI=F"
                r2 = _yf_metal(yf_sym, name)
                if r2:
                    r2.symbol = name
                    result.append(r2)
        # 铂金：yfinance ETF
        r3 = _yf_metal("PPLT", "铂金")
        if r3:
            r3.symbol = "铂金"
            result.append(r3)
        return result
