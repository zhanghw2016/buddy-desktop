"""
系统配置
"""
import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    """系统配置"""
    # 应用配置
    APP_NAME: str = "Buddy Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://buddy_desktop:zhu88jie@172.31.3.199:5432/buddy_dashboard"
    
    # Redis 配置
    REDIS_URL: str = "redis://172.31.3.199:6379/0"
    
    # AI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = ""
    MODEL_NAME: str = "gpt-4"
    
    # Agent 配置
    AGENT_TIMEOUT: int = 300  # Agent 超时时间（秒）
    MAX_RETRIES: int = 3      # 最大重试次数
    
    # 工作流配置
    WORKFLOW_MAX_STEPS: int = 50  # 工作流最大步骤数
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
