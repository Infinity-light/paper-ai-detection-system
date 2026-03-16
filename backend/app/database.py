"""
Database Connection and Session Management

role: 数据库连接管理，提供SQLAlchemy会话
depends: [config.py]
exports: [engine, SessionLocal, Base, get_db, init_db]
status: IMPLEMENTED

functions:
- get_db() -> Generator: 获取数据库会话（依赖注入）
- init_db(): 初始化数据库表
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    # 导入所有模型以确保它们被注册到Base.metadata
    from app.models import batch, paper, paragraph

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully")
