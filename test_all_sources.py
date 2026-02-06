#!/usr/bin/env python3
"""
测试所有数据源采集是否正常。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.collectors.factory import create_collectors


def main() -> None:
    collectors = create_collectors()
    total_ok = 0
    total_fail = 0
    for c in collectors:
        try:
            records = c.collect()
            n = len(records)
            total_ok += n
            print(f"[{c.category}] 成功 {n} 条")
        except Exception as e:
            total_fail += 1
            print(f"[{c.category}] 失败: {e}")
    print(f"--- 总计成功 {total_ok} 条，失败 {total_fail} 个采集器 ---")


if __name__ == "__main__":
    main()
