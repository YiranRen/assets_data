"""
简约风格 Web 看板：展示最新资产数据，按类别分组。
启动：uvicorn web.main:app --reload --app-dir .
或：python -m uvicorn web.main:app --reload
"""
import sys
from pathlib import Path
from collections import defaultdict

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.utils.config import load_config
from src.storage.manager import StorageManager

app = FastAPI(title="Asset Monitor", description="全球资产监控看板")

# 静态资源（若有）
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def get_storage() -> StorageManager:
    config = load_config()
    sc = config.get("storage", {})
    return StorageManager(
        enabled=True,
        backend=sc.get("backend", "both"),
        sqlite_path=sc.get("sqlite", {}).get("path", "data/asset_monitor.db"),
        json_dir=sc.get("json", {}).get("dir", "data"),
        json_latest=sc.get("json", {}).get("latest_file", "latest.json"),
        json_archive_by_date=sc.get("json", {}).get("archive_by_date", True),
    )


# 类别展示顺序
CATEGORY_ORDER = [
    "美股", "A股", "日股", "港股", "欧股", "台股",
    "外汇", "原油", "贵金属", "宏观", "全球ETF",
    "加密货币", "DeFi",
]


@app.get("/api/latest", summary="最新快照（按类别分组）")
def api_latest():
    """返回最新一次采集的数据，按 category 分组。"""
    storage = get_storage()
    records = storage.read_latest()
    if not records:
        return {"collected_at": None, "by_category": {}, "records": []}
    by_category = defaultdict(list)
    for r in records:
        cat = r.get("category") or "其他"
        by_category[cat].append(r)
    # 按固定顺序排列 key
    ordered = {
        k: by_category[k]
        for k in CATEGORY_ORDER
        if k in by_category
    }
    # 未在顺序中的类别追加
    for k in sorted(by_category.keys()):
        if k not in ordered:
            ordered[k] = by_category[k]
    collected_at = records[0].get("collected_at") if records else None
    return {
        "collected_at": collected_at,
        "count": len(records),
        "by_category": ordered,
        "records": records,
    }


@app.get("/", response_class=HTMLResponse)
def index():
    """返回看板首页。"""
    html_path = Path(__file__).parent / "index.html"
    if not html_path.exists():
        return HTMLResponse("<h1>Not Found</h1><p>index.html missing</p>", status_code=404)
    return FileResponse(html_path, media_type="text/html; charset=utf-8")
