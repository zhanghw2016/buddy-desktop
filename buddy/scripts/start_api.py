"""
启动 Buddy API 服务
"""
import sys
import os

# 添加项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import uvicorn
from buddy.main import app

if __name__ == "__main__":
    print("=" * 60)
    print("Buddy Dashboard API 服务")
    print("=" * 60)
    print("\n访问地址:")
    print("  - API 文档: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\n按 Ctrl+C 停止服务\n")
    print("=" * 60)
    
    uvicorn.run(
        "buddy.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
