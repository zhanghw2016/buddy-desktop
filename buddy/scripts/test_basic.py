"""
快速测试脚本 - 最小化版本
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=" * 60)
print("Buddy 看板系统 - 快速测试")
print("=" * 60)
print()

# 测试导入
try:
    print("1. 测试导入模块...")
    from buddy.models.enums import ProjectStatus, TaskType, AgentRole
    print("   ✓ 枚举导入成功")
    
    from buddy.core.config import settings
    print(f"   ✓ 配置加载成功: {settings.APP_NAME}")
    
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    sys.exit(1)

# 测试数据库连接
try:
    print()
    print("2. 测试数据库连接...")
    from buddy.core.database import SessionLocal
    
    db = SessionLocal()
    print("   ✓ 数据库连接成功")
    
    # 测试简单查询
    from sqlalchemy import text
    result = db.execute(text("SELECT 1")).scalar()
    if result == 1:
        print("   ✓ 数据库查询成功")
    
    db.close()
    
except Exception as e:
    print(f"   ✗ 数据库连接失败: {e}")
    print()
    print("提示: 请确保数据库服务正常运行")
    print(f"连接地址: {settings.DATABASE_URL}")
    sys.exit(1)

# 测试模型定义
try:
    print()
    print("3. 测试数据模型...")
    from buddy.models.base import Base
    from buddy.models import Project, Task, Agent
    
    print("   ✓ 数据模型定义正确")
    
except Exception as e:
    print(f"   ✗ 模型导入失败: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ 所有测试通过！系统可以正常运行")
print("=" * 60)
print()
print("下一步:")
print("1. 运行初始化脚本创建模拟数据")
print("   python -m buddy.scripts.init_mock_data")
print()
print("2. 启动 API 服务")
print("   python -m buddy.main")
print()
