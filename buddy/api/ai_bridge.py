"""
AI 桥接 API
用于前端和我（AI）之间的通信
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from buddy.core.database import get_db
from buddy.services.agent_bridge import get_bridge


router = APIRouter(prefix="/api/ai-bridge", tags=["ai-bridge"])


class AnalysisRequest(BaseModel):
    """分析请求"""
    agent_id: str
    task_id: str
    analysis_type: str  # requirement/design/code/test/bug


class AIResponse(BaseModel):
    """AI 响应"""
    request_id: str
    response: Dict[str, Any]


@router.post("/request-analysis")
async def request_ai_analysis(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Agent 请求 AI 分析
    
    这个接口供 Agent 调用，将分析请求提交给我
    """
    from buddy.models import Task
    
    # 获取任务
    task = db.query(Task).filter(Task.id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 获取桥接器
    bridge = get_bridge(db)
    
    # 提交分析请求
    result = await bridge.request_analysis(
        agent_id=request.agent_id,
        task=task,
        analysis_type=request.analysis_type
    )
    
    return result


@router.get("/pending-requests")
async def get_pending_ai_requests(db: Session = Depends(get_db)):
    """
    获取待处理的 AI 请求
    
    这个接口供我（AI 助手）查看当前有哪些 Agent 请求需要处理
    """
    bridge = get_bridge(db)
    pending = bridge.get_pending_requests()
    
    return {
        "count": len(pending),
        "requests": pending
    }


@router.post("/submit-response")
async def submit_ai_response(
    request_id: str,
    response: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    提交 AI 响应
    
    这个接口供我（AI 助手）提交对 Agent 请求的响应
    """
    bridge = get_bridge(db)
    await bridge.submit_response(request_id, response)
    
    return {
        "status": "success",
        "message": "AI 响应已提交"
    }


@router.get("/get-response/{request_id}")
async def get_ai_response(
    request_id: str,
    db: Session = Depends(get_db)
):
    """
    获取 AI 响应
    
    这个接口供 Agent 轮询，获取我的响应
    """
    bridge = get_bridge(db)
    response = await bridge.get_response(request_id)
    
    if not response:
        return {
            "status": "pending",
            "message": "响应还未准备好"
        }
    
    return {
        "status": "completed",
        "response": response
    }
