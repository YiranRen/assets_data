"""
JSON 存储：最新快照写 latest.json，可选按日期归档。
"""
import json
from pathlib import Path
from typing import List
from datetime import datetime

from ..models import AssetRecord


def _ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


class JSONBackend:
    def __init__(
        self,
        data_dir: str = "data",
        latest_file: str = "latest.json",
        archive_by_date: bool = True,
    ):
        self.data_dir = Path(data_dir)
        self.latest_file = latest_file
        self.archive_by_date = archive_by_date
        _ensure_dir(str(self.data_dir))

    def save(self, records: List[AssetRecord], collected_at: datetime) -> None:
        payload = {
            "collected_at": collected_at.isoformat(),
            "count": len(records),
            "records": [r.to_dict() for r in records],
        }
        # 最新快照
        latest_path = self.data_dir / self.latest_file
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        # 按日期归档
        if self.archive_by_date:
            date_path = self.data_dir / f"{collected_at.date().isoformat()}.json"
            with open(date_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

    def read_latest(self) -> List[dict]:
        latest_path = self.data_dir / self.latest_file
        if not latest_path.exists():
            return []
        with open(latest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("records", [])
