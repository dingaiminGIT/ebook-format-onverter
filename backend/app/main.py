from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import converter
import os

app = FastAPI(
    title="电子书格式转换器",
    description="支持多种电子书格式转换的API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保上传目录存在
os.makedirs("uploads", exist_ok=True)

# 注册路由
app.include_router(converter.router, prefix="/api/v1", tags=["converter"])

@app.get("/")
async def root():
    return {"message": "电子书格式转换器 API 服务正在运行"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}