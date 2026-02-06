"""
存储管理：根据配置选择 SQLite / JSON / 双写，统一 save 接口。
"""
from typing import List, Optional
from datetime import datetime

from ..models import AssetRecord
from .sqlite_backend import SQLiteBackend
from .json_backend import JSONBackend


class StorageManager:
    def __init__(
        self,
        enabled: bool = True,
        backend: str = "both",
        sqlite_path: str = "data/asset_monitor.db",
        json_dir: str = "data",
        json_latest: str = "latest.json",
        json_archive_by_date: bool = True,
    ):
        self.enabled = enabled
        self._sqlite: Optional[SQLiteBackend] = None
        self._json: Optional[JSONBackend] = None
        if not enabled:
            return
        if backend in ("sqlite", "both"):
            self._sqlite = SQLiteBackend(db_path=sqlite_path)
        if backend in ("json", "both"):
            self._json = JSONBackend(
                data_dir=json_dir,
                latest_file=json_latest,
                archive_by_date=json_archive_by_date,
            )

    def save(self, records: List[AssetRecord], collected_at: Optional[datetime] = None) -> None:
        if not self.enabled or not records:
            return
        ts = collected_at or datetime.utcnow()
        if self._sqlite:
            self._sqlite.save(records, ts)
        if self._json:
            self._json.save(records, ts)

    def read_latest(self) -> List[dict]:
        """从任一后端读取最新快照（优先 SQLite）。"""
        if self._sqlite:
            rows = self._sqlite.read_latest()
            if rows:
                return rows
        if self._json:
            return self._json.read_latest()
        return []
