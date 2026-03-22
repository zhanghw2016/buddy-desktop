"""
Buddy 看板系统 - 模拟数据初始化
用于快速搭建可演示的系统
"""
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from buddy.core.database import SessionLocal
from buddy.models import (
    Project, Task, Agent, Workflow, Message,
    ProjectStatus, TaskType, TaskPriority, TaskStatus,
    AgentRole, AgentStatus, WorkflowStatus, MessageType
)
import uuid
from datetime import datetime, timedelta
import random


def create_mock_agents(db):
    """创建模拟 Agent"""
    agents = [
        {
            "id": str(uuid.uuid4()),
            "name": "林经理",
            "role": AgentRole.PM,
            "status": AgentStatus.IDLE,
            "capabilities": ["需求分析", "项目规划", "任务分配", "进度跟踪", "风险管理"],
            "config": {"model": "gpt-4", "temperature": 0.7}
        },
        {
            "id": str(uuid.uuid4()),
            "name": "秦设计",
            "role": AgentRole.UI,
            "status": AgentStatus.IDLE,
            "capabilities": ["UI设计", "交互设计", "原型制作", "设计规范"],
            "config": {"model": "gpt-4", "temperature": 0.8}
        },
        {
            "id": str(uuid.uuid4()),
            "name": "张开发",
            "role": AgentRole.BACKEND,
            "status": AgentStatus.WORKING,
            "capabilities": ["后端开发", "API设计", "数据库设计", "性能优化", "代码重构"],
            "config": {"model": "gpt-4", "temperature": 0.5}
        },
        {
            "id": str(uuid.uuid4()),
            "name": "王测试",
            "role": AgentRole.QA,
            "status": AgentStatus.IDLE,
            "capabilities": ["测试计划", "测试用例设计", "自动化测试", "Bug分析", "质量报告"],
            "config": {"model": "gpt-4", "temperature": 0.6}
        }
    ]
    
    for agent_data in agents:
        agent = Agent(**agent_data)
        db.add(agent)
    
    db.commit()
    print(f"✅ 创建了 {len(agents)} 个 Agent")
    return agents


def create_mock_projects(db, agents):
    """创建模拟项目"""
    pm_agent = next(a for a in agents if a["role"] == AgentRole.PM)
    
    projects = [
        {
            "id": str(uuid.uuid4()),
            "name": "VDI 桌面管理系统优化",
            "description": "对现有 VDI 桌面管理系统进行性能优化和功能增强",
            "status": ProjectStatus.IN_PROGRESS,
            "owner": pm_agent["id"],
            "start_date": datetime.utcnow() - timedelta(days=30),
            "end_date": datetime.utcnow() + timedelta(days=60)
        },
        {
            "id": str(uuid.uuid4()),
            "name": "看板系统开发",
            "description": "开发基于 AI Agent 的项目管理看板系统",
            "status": ProjectStatus.IN_PROGRESS,
            "owner": pm_agent["id"],
            "start_date": datetime.utcnow() - timedelta(days=15),
            "end_date": datetime.utcnow() + timedelta(days=45)
        }
    ]
    
    for project_data in projects:
        project = Project(**project_data)
        db.add(project)
    
    db.commit()
    print(f"✅ 创建了 {len(projects)} 个项目")
    return projects


def create_mock_tasks(db, projects, agents):
    """创建模拟任务"""
    tasks = []
    
    # 为第一个项目创建任务
    project1 = projects[0]
    backend_agent = next(a for a in agents if a["role"] == AgentRole.BACKEND)
    qa_agent = next(a for a in agents if a["role"] == AgentRole.QA)
    ui_agent = next(a for a in agents if a["role"] == AgentRole.UI)
    
    project1_tasks = [
        {
            "id": str(uuid.uuid4()),
            "project_id": project1["id"],
            "title": "优化桌面组创建性能",
            "description": "优化桌面组创建流程，减少响应时间",
            "type": TaskType.DEVELOPMENT,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.IN_PROGRESS,
            "assignee": backend_agent["id"],
            "estimated_hours": 16,
            "actual_hours": 8,
            "due_date": datetime.utcnow() + timedelta(days=7)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project1["id"],
            "title": "修复用户登录偶发失败问题",
            "description": "排查并修复用户登录时偶发的认证失败问题",
            "type": TaskType.BUG,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.COMPLETED,
            "assignee": backend_agent["id"],
            "estimated_hours": 4,
            "actual_hours": 3,
            "due_date": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project1["id"],
            "title": "编写 API 性能测试用例",
            "description": "为核心 API 接口编写性能测试用例",
            "type": TaskType.TEST,
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.PENDING,
            "assignee": qa_agent["id"],
            "estimated_hours": 8,
            "due_date": datetime.utcnow() + timedelta(days=5)
        }
    ]
    
    # 为第二个项目创建任务
    project2 = projects[1]
    pm_agent = next(a for a in agents if a["role"] == AgentRole.PM)
    
    project2_tasks = [
        {
            "id": str(uuid.uuid4()),
            "project_id": project2["id"],
            "title": "设计看板界面原型",
            "description": "设计任务看板的主界面和交互流程",
            "type": TaskType.DESIGN,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.COMPLETED,
            "assignee": ui_agent["id"],
            "estimated_hours": 12,
            "actual_hours": 10,
            "due_date": datetime.utcnow() - timedelta(days=5)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project2["id"],
            "title": "实现 Agent 基础框架",
            "description": "开发 Agent 基类和四个专业 Agent",
            "type": TaskType.DEVELOPMENT,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.IN_PROGRESS,
            "assignee": backend_agent["id"],
            "estimated_hours": 20,
            "actual_hours": 15,
            "due_date": datetime.utcnow() + timedelta(days=3)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project2["id"],
            "title": "需求分析：任务拖拽功能",
            "description": "分析任务拖拽功能需求，拆解为具体任务",
            "type": TaskType.REQUIREMENT,
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.PENDING,
            "assignee": pm_agent["id"],
            "estimated_hours": 4,
            "due_date": datetime.utcnow() + timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project2["id"],
            "title": "编写 Agent 单元测试",
            "description": "为 Agent 基类和实现类编写单元测试",
            "type": TaskType.TEST,
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.PENDING,
            "assignee": qa_agent["id"],
            "estimated_hours": 6,
            "due_date": datetime.utcnow() + timedelta(days=7)
        }
    ]
    
    all_tasks = project1_tasks + project2_tasks
    
    for task_data in all_tasks:
        task = Task(**task_data)
        db.add(task)
        tasks.append(task_data)
    
    db.commit()
    print(f"✅ 创建了 {len(all_tasks)} 个任务")
    return tasks


def create_mock_messages(db, agents):
    """创建模拟消息"""
    messages = []
    
    pm_agent = agents[0]
    backend_agent = agents[2]
    qa_agent = agents[3]
    
    sample_messages = [
        {
            "id": str(uuid.uuid4()),
            "sender": pm_agent["id"],
            "receiver": backend_agent["id"],
            "content": "桌面组优化任务的进度如何？",
            "type": MessageType.QUESTION,
            "read": "read"
        },
        {
            "id": str(uuid.uuid4()),
            "sender": backend_agent["id"],
            "receiver": pm_agent["id"],
            "content": "已完成性能分析，正在优化 SQL 查询，预计明天完成",
            "type": MessageType.ANSWER,
            "read": "read"
        },
        {
            "id": str(uuid.uuid4()),
            "sender": qa_agent["id"],
            "receiver": pm_agent["id"],
            "content": "性能测试用例已完成初稿，请审核",
            "type": MessageType.NOTIFICATION,
            "read": "unread"
        }
    ]
    
    for msg_data in sample_messages:
        message = Message(**msg_data)
        db.add(message)
    
    db.commit()
    print(f"✅ 创建了 {len(sample_messages)} 条消息")
    return messages


def main():
    """主函数"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Buddy 看板系统 - 模拟数据初始化")
        print("=" * 60)
        
        # 检查是否已有数据
        existing_agents = db.query(Agent).count()
        if existing_agents > 0:
            print(f"⚠️  数据库中已存在 {existing_agents} 个 Agent")
            print("是否清空并重新初始化？(y/n): ", end="")
            choice = input().strip().lower()
            if choice != 'y':
                print("❌ 取消初始化")
                return
            
            # 清空现有数据
            db.query(Message).delete()
            db.query(Task).delete()
            db.query(Project).delete()
            db.query(Agent).delete()
            db.commit()
            print("🗑️  已清空现有数据")
        
        # 创建模拟数据
        agents = create_mock_agents(db)
        projects = create_mock_projects(db, agents)
        tasks = create_mock_tasks(db, projects, agents)
        messages = create_mock_messages(db, agents)
        
        print("=" * 60)
        print("✅ 模拟数据初始化完成！")
        print("=" * 60)
        print()
        print("📊 数据统计:")
        print(f"  - Agent: {len(agents)} 个")
        print(f"  - 项目: {len(projects)} 个")
        print(f"  - 任务: {len(tasks)} 个")
        print(f"  - 消息: {len(messages)} 条")
        print()
        print("🚀 现在可以启动服务查看数据:")
        print("  python -m buddy.main")
        print("  访问 http://localhost:8000/docs 查看 API")
        print()
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
