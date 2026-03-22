"""
任务相关 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from buddy.core.database import get_db
from buddy.models import Task, TaskType, TaskPriority, TaskStatus
from pydantic import BaseModel


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str = ""
    type: TaskType = TaskType.DEVELOPMENT
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    estimated_hours: float = 0
    tags: List[str] = []
    dependencies: List[str] = []


class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    type: TaskType = None
    priority: TaskPriority = None
    status: TaskStatus = None
    assignee: str = None
    estimated_hours: float = None
    actual_hours: float = None
    tags: List[str] = None
    dependencies: List[str] = None


class TaskResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    type: str
    priority: str
    status: str
    assignee: str
    
    class Config:
        orm_mode = True


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    project_id: str = None,
    assignee: str = None,
    status: TaskStatus = None,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    query = db.query(Task)
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if assignee:
        query = query.filter(Task.assignee == assignee)
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """获取任务详情"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """创建任务"""
    task = Task(
        id=str(uuid.uuid4()),
        project_id=task_data.project_id,
        title=task_data.title,
        description=task_data.description,
        type=task_data.type,
        priority=task_data.priority,
        status=TaskStatus.PENDING,
        assignee=task_data.assignee,
        estimated_hours=task_data.estimated_hours,
        tags=task_data.tags,
        dependencies=task_data.dependencies
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task_data: TaskUpdate, 
                db: Session = Depends(get_db)):
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_data.title:
        task.title = task_data.title
    if task_data.description:
        task.description = task_data.description
    if task_data.type:
        task.type = task_data.type
    if task_data.priority:
        task.priority = task_data.priority
    if task_data.status:
        task.status = task_data.status
    if task_data.assignee:
        task.assignee = task_data.assignee
    if task_data.estimated_hours:
        task.estimated_hours = task_data.estimated_hours
    if task_data.actual_hours:
        task.actual_hours = task_data.actual_hours
    if task_data.tags:
        task.tags = task_data.tags
    if task_data.dependencies:
        task.dependencies = task_data.dependencies
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
