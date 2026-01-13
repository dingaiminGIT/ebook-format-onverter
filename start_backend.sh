#!/bin/bash

# 启动后端服务的脚本

echo "启动电子书格式转换器后端服务..."

# 进入后端目录
cd backend

# 激活虚拟环境
source venv/bin/activate

# 启动FastAPI服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo "后端服务已启动在 http://localhost:8000"
echo "API文档可访问: http://localhost:8000/docs"