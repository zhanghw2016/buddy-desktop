"""
Agent 协作流程测试脚本
演示一个真实需求如何从 PM -> UI -> Backend -> QA 完整流程
"""
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from buddy.core.database import SessionLocal
from buddy.models import (
    Project, Task, Agent, Message,
    ProjectStatus, TaskType, TaskPriority, TaskStatus,
    AgentRole, AgentStatus, MessageType
)
from buddy.workflows.engine import WorkflowEngine
from buddy.agents.pm_agent import PMAgent
from buddy.agents.ui_agent import UIAgent
from buddy.agents.backend_agent import BackendAgent
from buddy.agents.qa_agent import QAAgent
import uuid
from datetime import datetime, timedelta

print("=" * 60)
print("Agent 协作流程测试")
print("=" * 60)

db = SessionLocal()

try:
    # 获取所有 Agent
    agents = db.query(Agent).all()
    print(f"\n[系统] 已加载 {len(agents)} 个 Agent")
    
    # 创建一个新的真实需求
    print("\n[Step 1] 创建测试需求")
    print("-" * 60)
    
    requirement_text = """
需求：为看板系统添加任务评论功能

用户故事：
作为一个项目管理者，我希望能够在任务卡片上添加评论，
以便与团队成员进行沟通和协作。

功能要求：
1. 用户可以在任务详情页添加文本评论
2. 评论支持 @ 提及其他成员
3. 被提及的成员收到通知
4. 评论支持编辑和删除
5. 评论按时间倒序排列
6. 显示评论者的头像和姓名

技术要求：
- 后端 API：RESTful 接口
- 数据库：新增 comments 表
- 前端：React 组件
- 实时通知：WebSocket
"""
    
    print(f"需求内容:\n{requirement_text}")
    
    # 获取 PM Agent
    pm_agent = db.query(Agent).filter(Agent.role == AgentRole.PM).first()
    
    if not pm_agent:
        print("[ERROR] 未找到 PM Agent")
        sys.exit(1)
    
    print(f"\n[Step 2] PM Agent 分析需求: {pm_agent.name}")
    print("-" * 60)
    
    # 模拟 PM Agent 分析需求
    pm_analysis = """
【PM 分析结果】

该需求为中等复杂度功能，涉及前后端开发和数据库设计。

估算工时：
- UI 设计: 8 小时
- 后端开发: 16 小时  
- 前端开发: 12 小时
- 测试: 6 小时
- 总计: 42 小时 (约 5-6 个工作日)

任务拆解：
1. 【设计】设计评论 UI 原型和交互流程
2. 【开发】数据库设计和后端 API 开发
3. 【开发】前端评论组件开发
4. 【开发】WebSocket 实时通知功能
5. 【测试】编写测试用例并执行测试

依赖关系：
- 任务 2 和 3 可以并行进行
- 任务 4 依赖任务 2 和 3
- 任务 5 在所有开发完成后进行

风险点：
- WebSocket 实时通知可能需要额外的技术调研
- @ 提及功能可能影响性能，需要优化
"""
    
    print(pm_analysis)
    
    # 创建子任务
    print(f"\n[Step 3] 自动创建子任务")
    print("-" * 60)
    
    # 获取当前项目
    project = db.query(Project).filter(Project.name == "看板系统开发").first()
    
    if not project:
        # 创建新项目
        project = Project(
            id=str(uuid.uuid4()),
            name="看板系统开发",
            description="开发基于 AI Agent 的项目管理看板系统",
            status=ProjectStatus.IN_PROGRESS,
            owner=pm_agent.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30)
        )
        db.add(project)
        db.commit()
        print(f"  [创建项目] {project.name}")
    
    # 获取其他 Agent
    ui_agent = db.query(Agent).filter(Agent.role == AgentRole.UI).first()
    backend_agent = db.query(Agent).filter(Agent.role == AgentRole.BACKEND).first()
    qa_agent = db.query(Agent).filter(Agent.role == AgentRole.QA).first()
    
    # 创建子任务
    tasks_data = [
        {
            "id": str(uuid.uuid4()),
            "project_id": project.id,
            "title": "设计任务评论 UI 原型",
            "description": "设计评论组件的 UI 原型和交互流程，包括评论列表、输入框、@ 提及等功能",
            "type": TaskType.DESIGN,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.PENDING,
            "assignee": ui_agent.id if ui_agent else None,
            "estimated_hours": 8,
            "due_date": datetime.utcnow() + timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project.id,
            "title": "设计评论数据库表和 RESTful API",
            "description": "设计 comments 表结构，实现评论的 CRUD API 接口",
            "type": TaskType.DEVELOPMENT,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.PENDING,
            "assignee": backend_agent.id if backend_agent else None,
            "estimated_hours": 16,
            "due_date": datetime.utcnow() + timedelta(days=4)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project.id,
            "title": "开发前端评论组件",
            "description": "实现 React 评论组件，包括评论列表、添加评论、编辑删除等功能",
            "type": TaskType.DEVELOPMENT,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.PENDING,
            "assignee": backend_agent.id if backend_agent else None,  # 前端也可以由 backend 做
            "estimated_hours": 12,
            "due_date": datetime.utcnow() + timedelta(days=6)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project.id,
            "title": "实现 WebSocket 实时通知",
            "description": "实现评论的实时推送功能，当有新评论或被 @ 时通知用户",
            "type": TaskType.DEVELOPMENT,
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.PENDING,
            "assignee": backend_agent.id if backend_agent else None,
            "estimated_hours": 8,
            "due_date": datetime.utcnow() + timedelta(days=8)
        },
        {
            "id": str(uuid.uuid4()),
            "project_id": project.id,
            "title": "编写评论功能测试用例",
            "description": "为评论功能编写单元测试、集成测试和 E2E 测试用例",
            "type": TaskType.TEST,
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.PENDING,
            "assignee": qa_agent.id if qa_agent else None,
            "estimated_hours": 6,
            "due_date": datetime.utcnow() + timedelta(days=9)
        }
    ]
    
    created_tasks = []
    for task_data in tasks_data:
        task = Task(**task_data)
        db.add(task)
        created_tasks.append(task)
        
        # 获取负责人名字
        assignee_name = "未分配"
        if task_data["assignee"]:
            assignee_agent = db.query(Agent).filter(Agent.id == task_data["assignee"]).first()
            if assignee_agent:
                assignee_name = assignee_agent.name
        
        print(f"  [{task_data['type'].value}] {task_data['title']}")
        print(f"    负责人: {assignee_name}")
        print(f"    预估工时: {task_data['estimated_hours']} 小时")
        print(f"    截止日期: {task_data['due_date'].strftime('%Y-%m-%d')}")
        print()
    
    db.commit()
    print(f"[OK] 已创建 {len(created_tasks)} 个子任务")
    
    # 发送任务分配消息
    print(f"\n[Step 4] 发送任务分配通知")
    print("-" * 60)
    
    for task in created_tasks[:3]:  # 只发送前3个任务的通知
        if task.assignee:
            message = Message(
                id=str(uuid.uuid4()),
                sender=pm_agent.id,
                receiver=task.assignee,
                content=f"新任务分配: {task.title}\n\n描述: {task.description}\n\n截止日期: {task.due_date.strftime('%Y-%m-%d')}",
                type=MessageType.TASK_ASSIGNED
            )
            db.add(message)
            
            assignee_agent = db.query(Agent).filter(Agent.id == task.assignee).first()
            if assignee_agent:
                print(f"  [{pm_agent.name} -> {assignee_agent.name}] {task.title}")
    
    db.commit()
    print(f"[OK] 已发送任务分配通知")
    
    # 显示最终结果
    print("\n" + "=" * 60)
    print("[SUCCESS] Agent 协作流程测试完成")
    print("=" * 60)
    
    print("\n创建的数据:")
    print(f"  - 项目: 1 个 ({project.name})")
    print(f"  - 任务: {len(created_tasks)} 个")
    print(f"  - 消息: {len(created_tasks[:3])} 条")
    
    print("\n任务分配情况:")
    for task in created_tasks:
        assignee_agent = db.query(Agent).filter(Agent.id == task.assignee).first()
        assignee_name = assignee_agent.name if assignee_agent else "未分配"
        print(f"  [{task.type.value}] {task.title} -> {assignee_name}")
    
    print("\n下一步:")
    print("  1. 查看前端界面: cd frontend && npm run dev")
    print("  2. 访问任务看板: http://localhost:3000/tasks")
    print("  3. 查看任务详情和 Agent 协作")
    
except Exception as e:
    print(f"\n[ERROR] 测试失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
