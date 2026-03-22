"""
数据库初始化脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from buddy.core.database import engine, SessionLocal
from buddy.models import (
    Base, Project, Task, Agent, Workflow, Message,
    AgentRole, AgentStatus, ProjectStatus, TaskType, TaskPriority, TaskStatus
)
from buddy.core.config import settings
import uuid


def init_database():
    """初始化数据库表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def init_agents():
    """初始化四个 Agent"""
    db = SessionLocal()
    try:
        # 检查是否已存在 Agent
        existing_agents = db.query(Agent).count()
        if existing_agents > 0:
            print(f"已存在 {existing_agents} 个 Agent，跳过初始化")
            return
        
        # 创建四个 Agent
        agents_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "林经理",
                "role": AgentRole.PM,
                "status": AgentStatus.IDLE,
                "capabilities": [
                    "需求分析",
                    "项目规划",
                    "任务分配",
                    "进度跟踪",
                    "风险管理"
                ],
                "config": {
                    "model": settings.MODEL_NAME,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            },
            {
                "id": str(uuid.uuid4()),
                "name": "秦设计",
                "role": AgentRole.UI,
                "status": AgentStatus.IDLE,
                "capabilities": [
                    "UI设计",
                    "交互设计",
                    "原型制作",
                    "设计规范"
                ],
                "config": {
                    "model": settings.MODEL_NAME,
                    "temperature": 0.8,
                    "max_tokens": 2000
                }
            },
            {
                "id": str(uuid.uuid4()),
                "name": "张开发",
                "role": AgentRole.BACKEND,
                "status": AgentStatus.IDLE,
                "capabilities": [
                    "后端开发",
                    "API设计",
                    "数据库设计",
                    "性能优化",
                    "代码重构"
                ],
                "config": {
                    "model": settings.MODEL_NAME,
                    "temperature": 0.5,
                    "max_tokens": 3000
                }
            },
            {
                "id": str(uuid.uuid4()),
                "name": "王测试",
                "role": AgentRole.QA,
                "status": AgentStatus.IDLE,
                "capabilities": [
                    "测试计划",
                    "测试用例设计",
                    "自动化测试",
                    "Bug分析",
                    "质量报告"
                ],
                "config": {
                    "model": settings.MODEL_NAME,
                    "temperature": 0.6,
                    "max_tokens": 2000
                }
            }
        ]
        
        # 插入数据
        for agent_data in agents_data:
            agent = Agent(**agent_data)
            db.add(agent)
        
        db.commit()
        print("四个 Agent 初始化完成")
        
        # 打印 Agent 信息
        for agent_data in agents_data:
            print(f"  - {agent_data['name']} ({agent_data['role'].value}): {agent_data['id']}")
        
    except Exception as e:
        print(f"初始化 Agent 失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_sample_project():
    """创建示例项目"""
    db = SessionLocal()
    try:
        # 检查是否已存在项目
        existing_projects = db.query(Project).count()
        if existing_projects > 0:
            print(f"已存在 {existing_projects} 个项目，跳过创建示例项目")
            return
        
        # 创建示例项目
        project = Project(
            id=str(uuid.uuid4()),
            name="VDI 桌面管理系统优化",
            description="对现有 VDI 桌面管理系统进行性能优化和功能增强",
            status=ProjectStatus.PLANNING,
            owner="林经理"
        )
        db.add(project)
        db.commit()
        
        print(f"示例项目创建完成: {project.name}")
        print(f"项目 ID: {project.id}")
        
    except Exception as e:
        print(f"创建示例项目失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Buddy Dashboard 数据库初始化")
    print("=" * 60)
    
    # 初始化数据库表
    init_database()
    
    # 初始化 Agent
    init_agents()
    
    # 创建示例项目
    create_sample_project()
    
    print("=" * 60)
    print("初始化完成！")
    print("=" * 60)
