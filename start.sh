#!/bin/bash

echo "=========================================="
echo "  AutoVen - 启动前后端服务"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[1/5] 安装 Python 依赖..."
pip install -r requirements.txt 2>/dev/null
if [ $? -ne 0 ]; then
    echo "警告: requirements.txt 中部分依赖安装失败，继续启动..."
fi

echo ""
echo "[2/5] 检查并安装前端依赖..."
if [ ! -d "web/node_modules" ]; then
    echo "未检测到 node_modules，正在安装前端依赖..."
    cd web
    npm install
    if [ $? -ne 0 ]; then
        echo "错误: 前端依赖安装失败，请检查 Node.js 环境"
        exit 1
    fi
    cd ..
    echo "前端依赖安装完成"
else
    echo "前端依赖已存在，跳过安装"
fi

echo ""
echo "[3/5] 清理端口占用..."
if lsof -i :8000 >/dev/null 2>&1; then
    lsof -t -i :8000 | xargs kill -9 2>/dev/null
    echo "已清理 8000 端口"
fi
if lsof -i :3000 >/dev/null 2>&1; then
    lsof -t -i :3000 | xargs kill -9 2>/dev/null
    echo "已清理 3000 端口"
fi

cleanup() {
    echo ""
    echo "正在停止所有服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "后端服务已停止 (PID: $BACKEND_PID)"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "前端服务已停止 (PID: $FRONTEND_PID)"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "[4/5] 启动后端服务 (FastAPI)..."
echo "      地址: http://localhost:8000"
python -m uvicorn master.server:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "      PID: $BACKEND_PID"

sleep 2

echo ""
echo "[5/5] 启动前端服务 (Next.js)..."
echo "      地址: http://localhost:3000"
cd web
npm run dev &
FRONTEND_PID=$!
echo "      PID: $FRONTEND_PID"
cd ..

echo ""
echo "=========================================="
echo "  所有服务已启动!"
echo "=========================================="
echo ""
echo "  前端: http://localhost:3000"
echo "  后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo "=========================================="
echo ""

wait
