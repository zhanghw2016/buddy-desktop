"""
Buddy 看板系统 - 模拟数据初始化（简化版）
"""
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from buddy.core.database import SessionLocal, engine
from buddy.models.base import Base
from buddy.models import (
    Project, Task, Agent, Workflow, Message,
    ProjectStatus, TaskType, TaskPriority, TaskStatus,
    AgentRole, AgentStatus, WorkflowStatus, MessageType
)
import uuid
from datetime import datetime, timedelta

print("=" * 60)
print("Buddy 看板系统 - 模拟数据初始化")
print("=" * 60)

# 创建所有表
print("\n创建数据库表...")
Base.metadata.create_all(bind=engine)
print("✓ 数据库表创建完成")

db = SessionLocal()

try:
    # 检查是否已有数据
    existing_agents = db.query(Agent).count()
    if existing_agents > 0:
        print(f"\n[WARNING] 数据库已有 {existing_agents} 个 Agent")
        response = input("是否清空并重新初始化？(y/n): ").strip().lower()
        if response != 'y':
            print("[CANCELLED] 操作已取消")
            db.close()
            sys.exit(0)
        
        # 清空所有表
        print("[INFO] 清空数据库...")
        db.query(Message).delete()
        db.query(Workflow).delete()
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Agent).delete()
        db.commit()
    
    print("\n[STEP 1] 创建 Agent...")
    
    # 创建 4 个 Agent
    agents_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "林经理",
            "role": AgentRole.PM,
            "status": AgentStatus.IDLE,
            "capabilities": ["需求分析", "任务分配", "进度跟踪", "风险管理"],
            "config": {"ai_model": "local", "max_tasks": 10}
        },
        {
            "id": str(uuid.uuid4()),
            "name": "秦设计",
            "role": AgentRole.UI,
            "status": AgentStatus.IDLE,
            "capabilities": ["UI设计", "原型制作", "交互设计", "视觉设计"],
            "config": {"ai_model": "local", "max_tasks": 8}
        },
        {
            "id": str(uuid.uuid4()),
            "name": "张开发",
            "role": AgentRole.BACKEND,
            "status": AgentStatus.IDLE,
            "capabilities": ["后端开发", "API设计", "数据库设计", "性能优化"],
            "config": {"ai_model": "local", "max_tasks": 12}
        },
        {
            "id": str(uuid.uuid4()),
            "name": "王测试",
            "role": AgentRole.QA,
            "status": AgentStatus.IDLE,
            "capabilities": ["测试用例", "Bug分析", "性能测试", "自动化测试"],
            "config": {"ai_model": "local", "max_tasks": 10}
        }
    ]
    
    agents = []
    for agent_data in agents_data:
        agent = Agent(**agent_data)
        db.add(agent)
        agents.append(agent_data)
        print(f"  - {agent_data['name']} ({agent_data['role'].value})")
    
    db.commit()
    print(f"[OK] 创建了 {len(agents)} 个 Agent")
    
    # 创建项目
    print("\n[STEP 2] 创建项目...")
    pm_agent = agents[0]
    
    projects_data = [
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
    
    projects = []
    for project_data in projects_data:
        project = Project(**project_data)
        db.add(project)
        projects.append(project_data)
        print(f"  - {project_data['name']}")
    
    db.commit()
    print(f"[OK] 创建了 {len(projects)} 个项目")
    
    # 创建任务
    print("\n[STEP 3] 创建任务...")
    backend_agent = agents[3]
    qa_agent = agents[3]
    ui_agent = agents[1]
    
    tasks_data = [
        {
            "id": str(uuid.uuid4()),
            "project_id": projects[0]["id"],
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
            "project_id": projects[0]["id"],
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
            "project_id": projects[0]["id"],
            "title": "编写 API 性能测试用例",
            "description": "为核心 API 接口编写性能测试用例",
            "type": TaskType.TEST,
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.PENDING,
            "assignee": qa_agent["id"],
            "estimated_hours": 8,
            "due_date": datetime.utcnow() + timedelta(days=5)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": projects[1]["id"],
            "title": "设计看板 UI 原型",
            "description": "设计项目管理看板的 UI 原型和交互流程",
            "type": TaskType.DESIGN,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.IN_PROGRESS,
            "assignee": ui_agent["id"],
            "estimated_hours": 12,
            "due_date": datetime.utcnow() + timedelta(days=10)
        }
    ]
    
    for task_data in tasks_data:
        task = Task(**task_data)
        db.add(task)
        print(f"  - {task_data['title']} [{task_data['status'].value}]")
    
    db.commit()
    print(f"[OK] 创建了 {len(tasks_data)} 个任务")
    
    # 创建消息
    print("\n[STEP 4] 创建消息...")
    
    messages_data = [
        {
            "id": str(uuid.uuid4()),
            "sender": pm_agent["id"],
            "receiver": backend_agent["id"],
            "content": "请优先处理桌面组性能优化任务，客户反馈响应时间较长。",
            "type": MessageType.TASK_ASSIGNED
        },
        {
            "id": str(uuid.uuid4()),
            "sender": backend_agent["id"],
            "receiver": pm_agent["id"],
            "content": "收到，我已经开始分析性能瓶颈，预计明天完成优化。",
            "type": MessageType.NOTIFICATION
        },
        {
            "id": str(uuid.uuid4()),
            "sender": qa_agent["id"],
            "receiver": pm_agent["id"],
            "content": "性能测试用例已编写完成，等待开发完成后执行测试。",
            "type": MessageType.NOTIFICATION
        }
    ]
    
    for msg_data in messages_data:
        message = Message(**msg_data)
        db.add(message)
    
    db.commit()
    print(f"[OK] 创建了 {len(messages_data)} 条消息")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 模拟数据初始化完成")
    print("=" * 60)
    print("\n创建的数据:")
    print(f"  - Agent: {len(agents)} 个")
    print(f"  - 项目: {len(projects)} 个")
    print(f"  - 任务: {len(tasks_data)} 个")
    print(f"  - 消息: {len(messages_data)} 条")
    print("\n下一步:")
    print("  1. 启动 API 服务:")
    print("     python -m buddy.main")
    print("  2. 访问 API 文档:")
    print("     http://localhost:8000/docs")
    
except Exception as e:
    print(f"\n[ERROR] 初始化失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
