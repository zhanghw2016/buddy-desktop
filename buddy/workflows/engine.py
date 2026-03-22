"""
工作流引擎
"""
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from buddy.models import Workflow, WorkflowStep
from buddy.models.enums import WorkflowStatus, AgentRole
from buddy.agents import PMAgent, UIAgent, BackendAgent, QAAgent
from buddy.utils.logger import logger


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agents = {}
        
    def register_agent(self, role: AgentRole, agent_instance):
        """注册 Agent"""
        self.agents[role] = agent_instance
    
    def create_workflow(self, name: str, description: str, 
                       steps: List[Dict]) -> Workflow:
        """
        创建工作流
        
        Args:
            name: 工作流名称
            description: 工作流描述
            steps: 工作流步骤列表
            
        Returns:
            创建的工作流对象
        """
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            status=WorkflowStatus.PENDING,
            current_step=0,
            total_steps=len(steps),
            steps=steps,
            context={}
        )
        
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        logger.info(f"工作流创建成功: {workflow.name} (ID: {workflow.id})")
        return workflow
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流 ID
            
        Returns:
            执行结果
        """
        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id
        ).first()
        
        if not workflow:
            raise ValueError(f"工作流 {workflow_id} 不存在")
        
        # 更新状态
        workflow.status = WorkflowStatus.IN_PROGRESS
        workflow.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"开始执行工作流: {workflow.name}")
        
        try:
            # 逐步执行
            for i, step_data in enumerate(workflow.steps):
                workflow.current_step = i
                self.db.commit()
                
                result = self._execute_step(workflow, step_data)
                
                # 更新上下文
                workflow.context = {**workflow.context, **result}
                self.db.commit()
            
            # 完成
            workflow.status = WorkflowStatus.COMPLETED
            workflow.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"工作流执行完成: {workflow.name}")
            
            return {
                "status": "success",
                "workflow_id": workflow.id,
                "result": workflow.context
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            workflow.status = WorkflowStatus.FAILED
            workflow.updated_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "status": "failed",
                "workflow_id": workflow.id,
                "error": str(e)
            }
    
    def _execute_step(self, workflow: Workflow, step_data: Dict) -> Dict:
        """执行单个步骤"""
        step_name = step_data.get("name")
        agent_role = step_data.get("agent_role")
        action = step_data.get("action")
        input_data = step_data.get("input_data", {})
        
        logger.info(f"执行步骤: {step_name} (角色: {agent_role})")
        
        # 获取对应的 Agent
        agent = self.agents.get(AgentRole(agent_role))
        if not agent:
            raise ValueError(f"未找到角色 {agent_role} 的 Agent")
        
        # 执行动作
        # TODO: 根据 action 调用相应的 Agent 方法
        # 这里需要实现具体的 Agent 调用逻辑
        
        return {
            "step": step_name,
            "status": "completed",
            "output": {}
        }


class RequirementWorkflow(WorkflowEngine):
    """需求开发工作流"""
    
    def create_requirement_workflow(self, requirement: str, project_id: str) -> Workflow:
        """创建需求开发工作流"""
        steps = [
            {
                "name": "需求分析",
                "agent_role": AgentRole.PM.value,
                "action": "analyze_requirement",
                "input_data": {"requirement": requirement}
            },
            {
                "name": "UI 设计",
                "agent_role": AgentRole.UI.value,
                "action": "design_ui",
                "input_data": {"requirement": requirement}
            },
            {
                "name": "后端开发",
                "agent_role": AgentRole.BACKEND.value,
                "action": "develop_backend",
                "input_data": {"requirement": requirement}
            },
            {
                "name": "测试验证",
                "agent_role": AgentRole.QA.value,
                "action": "test_feature",
                "input_data": {"requirement": requirement}
            }
        ]
        
        return self.create_workflow(
            name=f"需求开发: {requirement[:30]}...",
            description="从需求分析到测试验证的完整开发流程",
            steps=steps
        )


class BugFixWorkflow(WorkflowEngine):
    """Bug 修复工作流"""
    
    def create_bugfix_workflow(self, bug_description: str) -> Workflow:
        """创建 Bug 修复工作流"""
        steps = [
            {
                "name": "Bug 分析",
                "agent_role": AgentRole.QA.value,
                "action": "analyze_bug",
                "input_data": {"bug_description": bug_description}
            },
            {
                "name": "代码修复",
                "agent_role": AgentRole.BACKEND.value,
                "action": "fix_bug",
                "input_data": {"bug_description": bug_description}
            },
            {
                "name": "回归测试",
                "agent_role": AgentRole.QA.value,
                "action": "regression_test",
                "input_data": {"bug_description": bug_description}
            }
        ]
        
        return self.create_workflow(
            name=f"Bug 修复: {bug_description[:30]}...",
            description="从 Bug 分析到回归测试的修复流程",
            steps=steps
        )
