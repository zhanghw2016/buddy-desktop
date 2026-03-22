"""
项目相关 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from buddy.core.database import get_db
from buddy.models import Project, ProjectStatus, Task, TaskStatus
from pydantic import BaseModel


router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    owner: str = ""


class ProjectUpdate(BaseModel):
    name: str = None
    description: str = None
    status: ProjectStatus = None
    owner: str = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    owner: str
    progress: int = 0  # 添加进度字段
    task_count: int = 0  # 添加任务数字段
    
    class Config:
        orm_mode = True


def calculate_project_progress(db: Session, project_id: str) -> tuple:
    """计算项目进度和任务数"""
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    if not tasks:
        return 0, 0
    
    total = len(tasks)
    completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    progress = int((completed / total) * 100) if total > 0 else 0
    
    return progress, total


@router.get("/", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """获取项目列表"""
    projects = db.query(Project).all()
    
    # 为每个项目计算进度
    result = []
    for project in projects:
        progress, task_count = calculate_project_progress(db, str(project.id))
        result.append(ProjectResponse(
            id=str(project.id),
            name=project.name,
            description=project.description or "",
            status=project.status.value if project.status else "planning",
            owner=project.owner or "",
            progress=progress,
            task_count=task_count
        ))
    
    return result


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """获取项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    progress, task_count = calculate_project_progress(db, project_id)
    
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description or "",
        status=project.status.value if project.status else "planning",
        owner=project.owner or "",
        progress=progress,
        task_count=task_count
    )


@router.post("/", response_model=ProjectResponse)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """创建项目"""
    project = Project(
        id=str(uuid.uuid4()),
        name=project_data.name,
        description=project_data.description,
        status=ProjectStatus.PLANNING,
        owner=project_data.owner
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, project_data: ProjectUpdate, 
                   db: Session = Depends(get_db)):
    """更新项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project_data.name:
        project.name = project_data.name
    if project_data.description:
        project.description = project_data.description
    if project_data.status:
        project.status = project_data.status
    if project_data.owner:
        project.owner = project_data.owner
    
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """删除项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
