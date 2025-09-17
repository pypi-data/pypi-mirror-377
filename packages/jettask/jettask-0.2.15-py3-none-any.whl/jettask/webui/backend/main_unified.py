"""
统一的FastAPI应用主文件
简化版本，所有API接口都在unified_api_router.py中定义
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

# 导入统一的路由器
try:
    from unified_api_router import router as api_router
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from jettask.webui.backend.unified_api_router import router as api_router

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="JetTask WebUI API",
    description="统一的任务队列管理系统API",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册统一的API路由
app.include_router(api_router)

# 静态文件服务（如果需要）
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
    logger.info(f"Serving static files from {frontend_path}")

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "jettask-webui"}

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("JetTask WebUI API 启动成功")
    logger.info("所有API接口已统一到 unified_api_router.py 文件中")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("JetTask WebUI API 正在关闭...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_unified:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )