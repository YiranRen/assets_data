"""
数据清洗与验证：确保采集结果符合统一格式并过滤无效记录。
"""
from typing import List, Optional

from ..models import AssetRecord


def validate_record(r: AssetRecord) -> Optional[str]:
    """
    验证单条记录，无效返回错误信息，有效返回 None。
    """
    if not r.category or not r.symbol:
        return "缺少 category 或 symbol"
    if not isinstance(r.price, (int, float)) or r.price < 0:
        return "price 必须为非负数字"
    if not r.unit:
        return "缺少 unit"
    return None


def normalize_records(records: List[AssetRecord]) -> List[AssetRecord]:
    """
    验证并过滤，只返回有效记录；可选简单清洗（如 strip、round）。
    """
    result: List[AssetRecord] = []
    for r in records:
        err = validate_record(r)
        if err:
            continue
        # 简单清洗
        r.category = (r.category or "").strip()
        r.symbol = (r.symbol or "").strip()
        r.name = (r.name or "").strip()
        r.unit = (r.unit or "").strip()
        if r.change_24h is not None and abs(r.change_24h) < 1e-10:
            r.change_24h = 0.0
        if r.change_7d is not None and abs(r.change_7d) < 1e-10:
            r.change_7d = 0.0
        result.append(r)
    return result
