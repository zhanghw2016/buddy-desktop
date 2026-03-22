"""
简化测试 - 不需要导入模块
"""
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("=" * 60)
print("Buddy 看板系统 - 环境检查")
print("=" * 60)

# 检查 Python 版本
print(f"\n1. Python 版本: {sys.version}")

# 检查必要的包
packages = ['fastapi', 'sqlalchemy', 'pydantic', 'uvicorn']
print("\n2. 检查依赖包:")
for pkg in packages:
    try:
        __import__(pkg)
        print(f"   [OK] {pkg}")
    except ImportError:
        print(f"   [X] {pkg} - 未安装")

# 检查项目文件
print("\n3. 检查项目文件:")
required_files = [
    'buddy/main.py',
    'buddy/models/base.py',
    'buddy/core/database.py',
    'frontend/index.html'
]
for file in required_files:
    file_path = os.path.join(project_root, file)
    if os.path.exists(file_path):
        print(f"   [OK] {file}")
    else:
        print(f"   [X] {file} - 不存在")

print("\n" + "=" * 60)
print("检查完成！")
print("=" * 60)
print("\n下一步:")
print("1. 如果所有依赖都安装，可以启动服务:")
print("   python -m buddy.main")
print("\n2. 访问登录页面:")
print("   在浏览器打开 frontend/index.html")
