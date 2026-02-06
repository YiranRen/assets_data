"""
统一资产数据模型。
所有采集器输出均转换为该格式，便于存储与展示。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AssetRecord:
    """单条资产行情记录（统一格式）"""

    category: str  # 资产类别：美股、A股、日股、贵金属、外汇、宏观、加密货币、DeFi
    symbol: str  # 代码，如 AAPL、600519、XAUUSDT
    name: str  # 中文或英文名称
    price: float  # 最新价
    unit: str  # 显示单位：$、¥、% 等
    currency: str = "USD"  # 基准货币
    change_24h: Optional[float] = None  # 24小时涨跌幅（百分比）
    change_7d: Optional[float] = None  # 7日涨跌幅（百分比）
    source: str = ""  # 数据源标识
    collected_at: Optional[datetime] = None  # 采集时间

    def __post_init__(self) -> None:
        if self.collected_at is None:
            self.collected_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """用于 JSON 序列化与 SQLite 写入"""
        return {
            "category": self.category,
            "symbol": self.symbol,
            "name": self.name,
            "price": self.price,
            "unit": self.unit,
            "currency": self.currency,
            "change_24h": self.change_24h,
            "change_7d": self.change_7d,
            "source": self.source,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AssetRecord":
        """从字典还原（如从 JSON/SQLite 读取）"""
        collected = d.get("collected_at")
        if isinstance(collected, str):
            collected = datetime.fromisoformat(collected.replace("Z", "+00:00"))
        return cls(
            category=d.get("category", ""),
            symbol=d.get("symbol", ""),
            name=d.get("name", ""),
            price=float(d.get("price", 0)),
            unit=d.get("unit", ""),
            currency=d.get("currency", "USD"),
            change_24h=float(d["change_24h"]) if d.get("change_24h") is not None else None,
            change_7d=float(d["change_7d"]) if d.get("change_7d") is not None else None,
            source=d.get("source", ""),
            collected_at=collected,
        )
