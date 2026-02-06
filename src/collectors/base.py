"""
采集器抽象基类：所有资产采集器实现该接口，返回统一 AssetRecord 列表。
"""
from abc import ABC, abstractmethod
from typing import List

from ..models import AssetRecord


class BaseCollector(ABC):
    """数据采集器基类"""

    @property
    @abstractmethod
    def category(self) -> str:
        """资产类别标识"""
        pass

    @abstractmethod
    def collect(self) -> List[AssetRecord]:
        """
        执行一次采集，返回统一格式记录列表。
        可同步或异步实现；当前为同步，异常时返回空列表或部分结果。
        """
        pass
