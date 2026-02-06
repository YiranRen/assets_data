"""
采集器工厂：根据配置或默认列表创建所有启用的采集器。
"""
from typing import List, Type

from .base import BaseCollector
from .stocks import YFinanceUSCollector, YFinanceJapanCollector, AShareCollector
from .forex import ForexCollector
from .macro import MacroCollector
from .commodities import CommoditiesCollector


def create_collectors() -> List[BaseCollector]:
    """创建默认采集器列表（不含需额外依赖的 crypto、defi）。"""
    return [
        YFinanceUSCollector(),
        AShareCollector(),
        YFinanceJapanCollector(),
        CommoditiesCollector(),
        ForexCollector(),
        MacroCollector(),
    ]
