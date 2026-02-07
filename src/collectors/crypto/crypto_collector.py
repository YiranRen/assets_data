"""
加密货币：通过 OKX 或 Binance API（CCXT）获取现货价格。
标的：BTC、ETH、SOL、XRP、BNB、OKB。
"""
from typing import List, Optional, Tuple

from ...models import AssetRecord
from ..base import BaseCollector

# CCXT 统一使用 /USDT 交易对
SYMBOLS = [
    ("BTC/USDT", "BTC", "比特币"),
    ("ETH/USDT", "ETH", "以太坊"),
    ("SOL/USDT", "SOL", "Solana"),
    ("XRP/USDT", "XRP", "瑞波币"),
    ("BNB/USDT", "BNB", "币安币"),
    ("OKB/USDT", "OKB", "OKB"),
    ("HYPE/USDT", "HYPE", "HYPE"),
]


def _fetch_exchange(exchange_id: str) -> Optional[Tuple[str, List[AssetRecord]]]:
    """从指定交易所拉取行情，返回 (source, records) 或 None。"""
    try:
        import ccxt
        exchange = ccxt.binance({"enableRateLimit": True}) if exchange_id == "binance" else ccxt.okx({"enableRateLimit": True})
        result: List[AssetRecord] = []
        for pair, symbol, name in SYMBOLS:
            try:
                ticker = exchange.fetch_ticker(pair)
                if not ticker or ticker.get("last") is None:
                    continue
                price = float(ticker["last"])
                change_24h = ticker.get("percentage")  # 24h 涨跌幅
                if change_24h is not None:
                    change_24h = float(change_24h)
                result.append(
                    AssetRecord(
                        category="加密货币",
                        symbol=symbol,
                        name=name,
                        price=price,
                        unit="$",
                        currency="USD",
                        change_24h=change_24h,
                        change_7d=None,
                        source=exchange_id,
                    )
                )
            except Exception:
                continue
        if result:
            return (exchange_id, result)
    except Exception:
        pass
    return None


class CryptoCollector(BaseCollector):
    """加密货币采集：优先 OKX，失败则用 Binance。"""

    category = "加密货币"

    def collect(self) -> List[AssetRecord]:
        # 先试 OKX（含 OKB），再试 Binance
        for exchange_id in ["okx", "binance"]:
            out = _fetch_exchange(exchange_id)
            if out:
                return out[1]
        return []
