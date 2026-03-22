"""
测试数据库连接
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
print(f"项目根目录: {project_root}")

from buddy.core.database import engine
from sqlalchemy import text

print("=" * 60)
print("测试数据库连接")
print("=" * 60)
print(f"\n数据库地址: {engine.url}")
print()

try:
    with engine.connect() as conn:
        # 测试连接
        result = conn.execute(text("SELECT version();"))
        version = result.scalar()
        print(f"✓ PostgreSQL 版本: {version}")
        
        # 测试数据库
        result = conn.execute(text("SELECT current_database();"))
        db = result.scalar()
        print(f"✓ 当前数据库: {db}")
        
        # 测试用户
        result = conn.execute(text("SELECT current_user;"))
        user = result.scalar()
        print(f"✓ 当前用户: {user}")
        
        print("\n✅ 数据库连接成功！")
        print("\n现在可以运行初始化脚本：")
        print("  python buddy/scripts/init_mock_data")
        
except Exception as e:
    print(f"\n❌ 数据库连接失败: {e}")
    print("\n请检查：")
    print("  1. 数据库服务是否启动")
    print("  2. 网络是否通畅（ping 172.31.3.199）")
    print("  3. 用户名密码是否正确")
    print("  4. 数据库 buddy_dashboard 是否存在")
    sys.exit(1)
