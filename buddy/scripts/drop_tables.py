"""
删除旧数据库表
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from buddy.core.database import engine
from sqlalchemy import text

print("=" * 60)
print("删除旧数据库表")
print("=" * 60)

with engine.connect() as conn:
    # 删除所有旧表
    tables = ['messages', 'tasks', 'projects', 'agents']
    for table in tables:
        try:
            conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
            print(f"✓ 删除表 {table}")
        except Exception as e:
            print(f"✗ 删除表 {table} 失败: {e}")

    conn.commit()

print("\n✓ 所有旧表已删除")
