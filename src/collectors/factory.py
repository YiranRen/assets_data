"""
采集器工厂：根据配置或默认列表创建所有启用的采集器。
"""
from typing import List, Type

from .base import BaseCollector
from .stocks import (
    YFinanceUSCollector,
    YFinanceJapanCollector,
    YFinanceEuroCollector,
    YFinanceHKCollector,
    YFinanceGlobalETFCollector,
    YFinanceTWCollector,
    AShareCollector,
)
from .forex import ForexCollector
from .macro import MacroCollector
from .commodities import CommoditiesCollector, OilCollector
from .crypto import CryptoCollector


def create_collectors() -> List[BaseCollector]:
    """创建默认采集器列表（含加密货币，需安装 ccxt）。"""
    return [
        YFinanceUSCollector(),
        AShareCollector(),
        YFinanceJapanCollector(),
        YFinanceEuroCollector(),
        YFinanceHKCollector(),
        YFinanceTWCollector(),
        CommoditiesCollector(),
        OilCollector(),
        ForexCollector(),
        MacroCollector(),
        YFinanceGlobalETFCollector(),
        CryptoCollector(),
    ]
