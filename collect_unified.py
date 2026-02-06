#!/usr/bin/env python3
"""
统一格式数据采集 + 终端看板展示 + 存储。
运行：python collect_unified.py
"""
import sys
from pathlib import Path
from datetime import datetime

# 保证项目根在 path 中
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.config import load_config
from src.collectors.factory import create_collectors
from src.processors.normalizer import normalize_records
from src.storage.manager import StorageManager
from src.models import AssetRecord


def main() -> None:
    config = load_config()
    storage_cfg = config.get("storage", {})
    sqlite_cfg = storage_cfg.get("sqlite", {})
    json_cfg = storage_cfg.get("json", {})

    storage = StorageManager(
        enabled=storage_cfg.get("enabled", True),
        backend=storage_cfg.get("backend", "both"),
        sqlite_path=sqlite_cfg.get("path", "data/asset_monitor.db"),
        json_dir=json_cfg.get("dir", "data"),
        json_latest=json_cfg.get("latest_file", "latest.json"),
        json_archive_by_date=json_cfg.get("archive_by_date", True),
    )

    collectors = create_collectors()
    all_records: list[AssetRecord] = []
    for c in collectors:
        try:
            records = c.collect()
            all_records.extend(records)
        except Exception as e:
            print(f"[{c.category}] 采集异常: {e}", file=sys.stderr)

    all_records = normalize_records(all_records)
    collected_at = datetime.utcnow()
    for r in all_records:
        r.collected_at = collected_at

    # 存储
    storage.save(all_records, collected_at)

    # Rich 终端展示
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
    except ImportError:
        for r in all_records:
            print(r.category, r.symbol, r.name, r.price, r.unit)
        return

    console = Console()
    console.print(
        Panel(
            f"[bold]🚀 Asset Monitor - 全球资产监控看板[/bold]\n更新时间: {collected_at.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            title="",
            border_style="blue",
        )
    )
    table = Table(show_header=True, header_style="bold")
    table.add_column("资产类别", style="cyan")
    table.add_column("代码", style="green")
    table.add_column("名称", style="white")
    table.add_column("价格", justify="right", style="yellow")
    table.add_column("24h涨跌", justify="right")
    table.add_column("7日涨跌", justify="right")
    for r in all_records:
        ch24 = f"{r.change_24h:+.2f}%" if r.change_24h is not None else "-"
        ch7 = f"{r.change_7d:+.2f}%" if r.change_7d is not None else "-"
        if r.change_24h is not None:
            ch24 = f"[green]{ch24}[/green]" if r.change_24h >= 0 else f"[red]{ch24}[/red]"
        if r.change_7d is not None:
            ch7 = f"[green]{ch7}[/green]" if r.change_7d >= 0 else f"[red]{ch7}[/red]"
        if r.unit == "%":
            price_str = f"{r.price:,.2f}%"
        elif r.unit:
            price_str = f"{r.unit}{r.price:,.2f}"
        else:
            price_str = str(r.price)
        table.add_row(r.category, r.symbol, r.name, price_str, ch24, ch7)
    console.print(table)
    console.print(f"[dim]共 {len(all_records)} 条，已写入存储（SQLite/JSON）[/dim]")


if __name__ == "__main__":
    main()
