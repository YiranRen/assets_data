"""
SQLite 存储：持久化资产快照与历史（按采集时间写入）。
"""
import sqlite3
from pathlib import Path
from typing import List
from datetime import datetime

from ..models import AssetRecord


def _ensure_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


class SQLiteBackend:
    def __init__(self, db_path: str = "data/asset_monitor.db"):
        self.db_path = db_path
        _ensure_dir(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS asset_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    unit TEXT NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    change_24h REAL,
                    change_7d REAL,
                    source TEXT,
                    collected_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_collected ON asset_snapshots(collected_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_symbol ON asset_snapshots(symbol)"
            )

    def save(self, records: List[AssetRecord], collected_at: datetime) -> None:
        ts = collected_at.isoformat()
        with sqlite3.connect(self.db_path) as conn:
            for r in records:
                conn.execute(
                    """INSERT INTO asset_snapshots
                       (category, symbol, name, price, unit, currency, change_24h, change_7d, source, collected_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        r.category,
                        r.symbol,
                        r.name,
                        r.price,
                        r.unit,
                        r.currency,
                        r.change_24h,
                        r.change_7d,
                        r.source or "",
                        ts,
                    ),
                )

    def read_latest(self, limit: int = 500) -> List[dict]:
        """读取最近一次快照（按 collected_at 取最新一批）。"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """SELECT category, symbol, name, price, unit, currency, change_24h, change_7d, source, collected_at
                   FROM asset_snapshots
                   WHERE collected_at = (SELECT MAX(collected_at) FROM asset_snapshots)
                   ORDER BY id
                   LIMIT ?""",
                (limit,),
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
