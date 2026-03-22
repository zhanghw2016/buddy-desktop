"""
创建 Buddy Dashboard 数据库
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 连接参数
DB_HOST = "172.31.3.199"
DB_PORT = 5432
DB_USER = "buddy_desktop"
DB_PASSWORD = "zhu88jie"
DB_NAME = "buddy_dashboard"

print("=" * 60)
print("创建 Buddy Dashboard 数据库")
print("=" * 60)

try:
    # 连接到默认数据库 postgres
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    # 检查数据库是否已存在
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    exists = cursor.fetchone()
    
    if exists:
        print(f"\n[OK] 数据库 '{DB_NAME}' 已存在")
    else:
        # 创建数据库
        cursor.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER}")
        print(f"\n[SUCCESS] 数据库 '{DB_NAME}' 创建成功")
    
    cursor.close()
    conn.close()
    
    print("\n下一步:")
    print("  python -m buddy.scripts.init_mock_data")
    
except Exception as e:
    print(f"\n[ERROR] 数据库创建失败: {e}")
    print("\n请检查:")
    print("  1. 数据库服务是否启动")
    print("  2. 用户权限是否足够")
