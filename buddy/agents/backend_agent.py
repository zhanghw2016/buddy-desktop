"""
Backend Agent - 后端开发工程师
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from buddy.agents.base import BaseAgent
from buddy.models import Task
from buddy.models.enums import TaskType, AgentRole


class BackendAgent(BaseAgent):
    """后端开发 Agent"""
    
    def __init__(self, agent_id: str, db: Session):
        super().__init__(agent_id, db)
        if self.role != AgentRole.BACKEND:
            raise ValueError(f"Agent {agent_id} is not a Backend agent")
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是张开发，一位经验丰富的后端开发工程师。你的职责包括：

1. **架构设计**: 设计系统架构和技术方案
2. **API 开发**: 实现高质量的 API 接口
3. **数据库设计**: 设计合理的数据库结构
4. **性能优化**: 优化系统性能和响应速度
5. **代码质量**: 编写高质量、可维护的代码

## 你的开发原则

- 遵循 SOLID 原则和设计模式
- 注重代码的可读性和可维护性
- 编写单元测试，确保代码质量
- 关注性能和安全性
- 编写清晰的文档和注释

## 输出规范

你的开发输出应包含：
- 技术方案说明
- API 接口定义
- 数据库设计
- 核心代码实现
- 测试用例
- 部署说明

当前项目: VDI 桌面管理系统优化
技术栈: FastAPI + PostgreSQL + Redis
"""
    
    def process_task(self, task: Task) -> Dict[str, Any]:
        """处理任务"""
        if task.type == TaskType.DEVELOPMENT:
            return self._process_development(task)
        elif task.type == TaskType.BUG:
            return self._process_bug(task)
        else:
            return {"status": "error", "message": "不支持的 任务类型"}
    
    def _process_development(self, task: Task) -> Dict[str, Any]:
        """处理开发任务"""
        # TODO: 调用 AI 生成代码
        # 这里需要实现 AI 代码生成逻辑
        
        result = {
            "architecture": {
                "pattern": "RESTful API + Service Layer",
                "database": "PostgreSQL",
                "cache": "Redis",
                "framework": "FastAPI"
            },
            "api_design": [
                {
                    "method": "GET",
                    "path": "/api/projects",
                    "description": "获取项目列表",
                    "response": {
                        "code": 200,
                        "data": [
                            {
                                "id": "string",
                                "name": "string",
                                "status": "string"
                            }
                        ]
                    }
                }
            ],
            "database_design": {
                "tables": [
                    {
                        "name": "projects",
                        "columns": [
                            {"name": "id", "type": "VARCHAR(64)", "primary": True},
                            {"name": "name", "type": "VARCHAR(255)", "nullable": False},
                            {"name": "status", "type": "VARCHAR(50)", "default": "planning"}
                        ]
                    }
                ]
            },
            "code": {
                "main": "app/main.py",
                "models": "app/models/",
                "api": "app/api/",
                "services": "app/services/"
            },
            "tests": {
                "unit_tests": "tests/unit/",
                "integration_tests": "tests/integration/"
            }
        }
        
        return result
    
    def _process_bug(self, task: Task) -> Dict[str, Any]:
        """处理 Bug 任务"""
        # TODO: 分析和修复 Bug
        result = {
            "bug_analysis": "Bug 分析结果",
            "root_cause": "根本原因",
            "fix_solution": "修复方案",
            "code_changes": [
                {
                    "file": "app/api/projects.py",
                    "change": "修复了空指针异常"
                }
            ],
            "test_verification": "测试验证结果"
        }
        
        return result
