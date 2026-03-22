"""
数据库配置
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from buddy.models.base import Base
from buddy.core.config import settings  # 导入配置

# 从配置读取数据库 URL
DATABASE_URL = settings.DATABASE_URL

# 创建引擎（SQLite 不支持连接池配置）
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
