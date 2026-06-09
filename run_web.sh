#!/bin/bash

echo "=== 启动服务器 ==="
# cd autodl-tmp/EasyEdu

echo ""
echo "=========================================="
echo "🚀 服务器启动中..."
echo "=========================================="
echo ""

# 启动服务器
python -m uvicorn web.main:app --host 0.0.0.0 --port 3003 --workers 1

# 注意：上面的命令会阻塞，直到按Ctrl+C
# 当看到 "Uvicorn running on http://0.0.0.0:3003" 时，
# 请在浏览器访问 http://127.0.0.1:3003 或 http://localhost:3003