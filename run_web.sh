#!/bin/bash
# 在项目根目录启动 Web 看板
cd "$(dirname "$0")"
echo "启动 Asset Monitor Web @ http://127.0.0.1:8765"
python3 -m uvicorn web.main:app --host 0.0.0.0 --port 8765
