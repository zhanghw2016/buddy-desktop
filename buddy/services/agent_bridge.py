"""
Agent AI 桥接服务
让 Agent 能够直接使用我的能力
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from buddy.models import Task, Message, Agent
from buddy.models.enums import TaskStatus, MessageType
from buddy.utils.logger import logger


class AgentBridge:
    """
    Agent AI 桥接器
    
    这个类负责：
    1. 接收 Agent 的请求
    2. 将请求转发给我（AI 助手）
    3. 将我的响应返回给 Agent
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.request_queue = []  # 请求队列
        self.response_cache = {}  # 响应缓存
    
    async def request_analysis(self, agent_id: str, task: Task, 
                               analysis_type: str) -> Dict[str, Any]:
        """
        请求 AI 分析
        
        Args:
            agent_id: Agent ID
            task: 任务对象
            analysis_type: 分析类型 (requirement/design/code/test/bug)
            
        Returns:
            分析结果
        """
        logger.info(f"Agent {agent_id} 请求 {analysis_type} 分析")
        
        # 根据分析类型构建提示词
        prompt = self._build_analysis_prompt(task, analysis_type)
        
        # 创建请求记录
        request_id = f"req_{datetime.now().timestamp()}"
        
        # 将请求加入队列（等待 AI 处理）
        request = {
            "id": request_id,
            "agent_id": agent_id,
            "task_id": task.id,
            "type": analysis_type,
            "prompt": prompt,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        self.request_queue.append(request)
        
        # 返回请求 ID（Agent 可以轮询结果）
        return {
            "request_id": request_id,
            "status": "pending",
            "message": "请求已提交，等待 AI 处理"
        }
    
    def get_pending_requests(self) -> list:
        """获取待处理的请求（给我看的）"""
        return [req for req in self.request_queue if req["status"] == "pending"]
    
    async def submit_response(self, request_id: str, response: Dict[str, Any]):
        """
        提交 AI 响应（我来调用）
        
        Args:
            request_id: 请求 ID
            response: AI 响应内容
        """
        # 找到对应请求
        request = next((req for req in self.request_queue 
                       if req["id"] == request_id), None)
        
        if not request:
            logger.error(f"请求 {request_id} 不存在")
            return
        
        # 更新请求状态
        request["status"] = "completed"
        request["response"] = response
        request["completed_at"] = datetime.utcnow()
        
        # 缓存响应
        self.response_cache[request_id] = response
        
        logger.info(f"AI 响应已提交: {request_id}")
    
    async def get_response(self, request_id: str) -> Optional[Dict[str, Any]]:
        """获取 AI 响应（Agent 轮询）"""
        return self.response_cache.get(request_id)
    
    def _build_analysis_prompt(self, task: Task, analysis_type: str) -> str:
        """构建分析提示词"""
        base_info = f"""
任务标题: {task.title}
任务描述: {task.description}
任务类型: {task.type.value}
优先级: {task.priority.value}
"""
        
        if analysis_type == "requirement":
            return f"""
{base_info}

请分析以上需求，输出以下内容：
1. 需求摘要
2. 功能点列表
3. 技术要点
4. 潜在风险
5. 建议的任务拆解（JSON 格式）

请以结构化的方式输出。
"""
        
        elif analysis_type == "design":
            return f"""
{base_info}

请设计 UI 方案，输出以下内容：
1. 设计理念
2. 页面布局描述
3. 交互流程
4. 设计规范（颜色、字体、间距）
5. 组件结构

请以 Markdown 格式输出。
"""
        
        elif analysis_type == "code":
            return f"""
{base_info}

请设计技术方案，输出以下内容：
1. 架构设计
2. API 接口定义
3. 数据库设计
4. 核心代码实现
5. 测试用例

请以代码和文档的形式输出。
"""
        
        elif analysis_type == "test":
            return f"""
{base_info}

请设计测试方案，输出以下内容：
1. 测试策略
2. 测试用例列表
3. 测试数据准备
4. 自动化测试脚本
5. 验收标准

请以结构化文档输出。
"""
        
        elif analysis_type == "bug":
            return f"""
{base_info}

请分析 Bug，输出以下内容：
1. Bug 描述
2. 根本原因分析
3. 修复方案
4. 代码修改建议
5. 防止复发的建议

请以详细文档形式输出。
"""
        
        return base_info


# 全局桥接器实例（单例）
_bridge_instance = None


def get_bridge(db: Session) -> AgentBridge:
    """获取全局桥接器实例"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = AgentBridge(db)
    return _bridge_instance
