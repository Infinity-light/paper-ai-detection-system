"""
FastAPI Application Entry Point

role: FastAPI应用入口，配置路由、中间件、CORS
depends: [api/upload.py, api/batch.py, api/paper.py, database.py, config.py]
exports: [app]
status: IMPLEMENTED

functions:
- create_app() -> FastAPI: 创建并配置FastAPI应用实例
- lifespan(app): 应用生命周期管理（启动/关闭）
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.api import upload, batch, paper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("Application starting...")
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    yield
    # 关闭时执行
    print("Application shutting down...")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="Paper AI Detection System",
        description="论文AI检测系统API",
        version="1.0.0",
        lifespan=lifespan
    )

    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理器"""
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": str(exc)
            }
        )

    # 注册路由
    app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
    app.include_router(batch.router, prefix="/api/v1", tags=["batch"])
    app.include_router(paper.router, prefix="/api/v1", tags=["paper"])

    return app


app = create_app()


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "Paper AI Detection System API"}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "paper-ai-detection-system",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
