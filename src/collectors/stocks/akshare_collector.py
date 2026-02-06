"""
A股采集：腾讯财经（主）、网易财经（备）、AKShare（备），多源自动切换。
"""
from typing import List, Optional, Tuple

from ...models import AssetRecord
from ..base import BaseCollector

# 默认标的：股票 + 指数
DEFAULT_STOCKS = ["000001", "600036", "600519", "002594"]  # 平安银行、招商银行、贵州茅台、比亚迪
DEFAULT_INDEXES = ["000016", "000300", "399001"]  # 上证50、沪深300、深证成指
NAME_MAP = {
    "000001": "平安银行",
    "600036": "招商银行",
    "600519": "贵州茅台",
    "002594": "比亚迪",
    "000016": "上证50",
    "000300": "沪深300",
    "399001": "深证成指",
}


def _fetch_tencent(symbol: str) -> Optional[Tuple[float, float, float]]:
    """腾讯财经：返回 (price, change_pct_1d, change_pct_7d) 或 None。7d 可能不可用。"""
    try:
        from urllib.request import urlopen
        # 腾讯接口：沪市 sh 前缀，深市 sz 前缀，指数同上
        if symbol.startswith("6"):
            code = "sh" + symbol
        elif symbol.startswith("0") or symbol.startswith("3"):
            code = "sz" + symbol
        else:
            code = "sz" + symbol
        url = f"https://qt.gtimg.cn/q={code}"
        with urlopen(url, timeout=10) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        if not text or "~" not in text:
            return None
        parts = text.split("~")
        if len(parts) < 50:
            return None
        try:
            price = float(parts[3])
            pchange = float(parts[32]) if len(parts) > 32 and parts[32] else 0.0
        except (IndexError, ValueError):
            return None
        return (price, pchange, None)
    except Exception:
        return None


def _fetch_netease(symbol: str) -> Optional[Tuple[float, float, float]]:
    """网易财经：返回 (price, change_24h, change_7d) 或 None。"""
    try:
        from urllib.request import urlopen
        import json
        if symbol.startswith("6"):
            code = "0" + symbol
        else:
            code = "1" + symbol
        url = f"https://api.money.126.net/data/feed/{code},money.api"
        with urlopen(url, timeout=10) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        if not text or "(" not in text:
            return None
        start = text.find("(") + 1
        end = text.rfind(")")
        raw = text[start:end]
        data = json.loads(raw)
        key = code if code in data else next(iter(data.keys()), None)
        if not key:
            return None
        obj = data.get(key, {})
        price = obj.get("price") or obj.get("lastClose")
        if price is None:
            return None
        price = float(price)
        pct = obj.get("percent")
        pct = float(pct) if pct is not None else None
        return (price, pct, None)
    except Exception:
        return None


def _fetch_akshare(symbol: str) -> Optional[Tuple[float, float, float]]:
    """AKShare：返回 (price, change_24h, change_7d) 或 None。"""
    try:
        import akshare as ak
        if symbol.startswith("6"):
            code = "sh" + symbol
        elif symbol.startswith("0") or symbol.startswith("3"):
            code = "sz" + symbol
        else:
            code = "sz" + symbol
        # 股票用 realtime
        if symbol in DEFAULT_INDEXES:
            df = ak.stock_zh_index_spot_em()
            row = df[df["代码"].astype(str) == symbol]
        else:
            df = ak.stock_zh_a_spot_em()
            row = df[df["代码"].astype(str) == symbol]
        if row is None or row.empty:
            return None
        row = row.iloc[0]
        price = float(row.get("最新价", 0))
        if price <= 0:
            return None
        pct = row.get("涨跌幅")
        change_24h = float(pct) if pct is not None else None
        return (price, change_24h, None)
    except Exception:
        return None


def _fetch_ashare_one(symbol: str) -> Optional[AssetRecord]:
    """多源依次尝试：腾讯 -> 网易 -> AKShare。"""
    for fetcher in [_fetch_tencent, _fetch_netease, _fetch_akshare]:
        try:
            t = fetcher(symbol)
            if t is None:
                continue
            price, change_24h, change_7d = t
            if price <= 0:
                continue
            name = NAME_MAP.get(symbol, symbol)
            return AssetRecord(
                category="A股",
                symbol=symbol,
                name=name,
                price=round(price, 2),
                unit="¥",
                currency="CNY",
                change_24h=change_24h,
                change_7d=change_7d,
                source="tencent" if fetcher == _fetch_tencent else "netease" if fetcher == _fetch_netease else "akshare",
            )
        except Exception:
            continue
    return None


class AShareCollector(BaseCollector):
    category = "A股"

    def collect(self) -> List[AssetRecord]:
        result: List[AssetRecord] = []
        for sym in DEFAULT_STOCKS + DEFAULT_INDEXES:
            r = _fetch_ashare_one(sym)
            if r:
                result.append(r)
        return result
