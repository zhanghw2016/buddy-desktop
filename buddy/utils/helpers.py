"""
工具函数
"""
import uuid
from datetime import datetime
from typing import Any, Dict


def generate_id() -> str:
    """生成唯一 ID"""
    return str(uuid.uuid4())


def format_datetime(dt: datetime) -> str:
    """格式化日期时间"""
    return dt.isoformat() if dt else None


def parse_datetime(dt_str: str) -> datetime:
    """解析日期时间字符串"""
    return datetime.fromisoformat(dt_str) if dt_str else None


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """清理字典，移除 None 值"""
    return {k: v for k, v in data.items() if v is not None}
