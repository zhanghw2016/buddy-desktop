"""
使用本地数据库进行测试（SQLite）
"""
import sys
import os

# 添加项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlalchemy import create_engine, text
from buddy.models.base import Base

# 使用 SQLite 数据库（本地测试）
DATABASE_URL = "sqlite:///./buddy_dashboard.db"

print("=" * 60)
print("初始化 Buddy Dashboard（本地 SQLite）")
print("=" * 60)
print(f"\n数据库文件: {os.path.abspath('buddy_dashboard.db')}")
print()

# 创建引擎
engine = create_engine(DATABASE_URL, echo=False)

# 创建所有表
print("创建数据表...")
Base.metadata.create_all(bind=engine)
print("[OK] 数据表创建成功")

# 测试连接
with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = result.fetchall()
    print(f"\n已创建 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")

print("\n[SUCCESS] 本地数据库初始化完成")
print("\n下一步:")
print("  1. 修改 buddy/core/config.py 的 DATABASE_URL 为:")
print(f"     DATABASE_URL = '{DATABASE_URL}'")
print("  2. 运行初始化脚本:")
print("     python buddy/scripts/init_mock_data.py")
