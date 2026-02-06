"""
加载 config/config.yaml，缺失时使用默认值。
"""
from pathlib import Path
from typing import Any

def load_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "config.yaml"
    if not config_path.exists():
        return _default_config()
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or _default_config()
    except Exception:
        return _default_config()


def _default_config() -> dict:
    return {
        "storage": {
            "enabled": True,
            "backend": "both",
            "sqlite": {"path": "data/asset_monitor.db"},
            "json": {
                "dir": "data",
                "latest_file": "latest.json",
                "archive_by_date": True,
            },
        },
        "collect": {"timeout": 15, "retry": 2},
    }
