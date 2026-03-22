"""
数据库配置
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from buddy.models.base import Base

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://buddy_desktop:zhu88jie@172.31.3.199:5432/buddy_dashboard"
)

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 开发环境打印 SQL
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
