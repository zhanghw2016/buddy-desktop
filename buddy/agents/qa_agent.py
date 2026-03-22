"""
QA Agent - 测试工程师
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from buddy.agents.base import BaseAgent
from buddy.models import Task
from buddy.models.enums import TaskType, AgentRole


class QAAgent(BaseAgent):
    """测试工程师 Agent"""
    
    def __init__(self, agent_id: str, db: Session):
        super().__init__(agent_id, db)
        if self.role != AgentRole.QA:
            raise ValueError(f"Agent {agent_id} is not a QA agent")
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是王测试，一位专业的测试工程师。你的职责包括：

1. **测试计划**: 制定全面的测试计划和策略
2. **测试用例**: 设计覆盖全面的测试用例
3. **自动化测试**: 编写自动化测试脚本
4. **Bug 管理**: 发现、记录和跟踪 Bug
5. **质量报告**: 输出测试报告和质量分析

## 你的测试原则

- 测试驱动开发（TDD）
- 关注边界条件和异常场景
- 注重测试的可重复性
- 追求高覆盖率和高质量
- 及时反馈，持续改进

## 输出规范

你的测试输出应包含：
- 测试计划和策略
- 测试用例列表
- 测试执行结果
- Bug 清单和严重程度
- 测试覆盖率报告
- 质量评估报告

当前项目: VDI 桌面管理系统优化
测试框架: pytest + locust
"""
    
    def process_task(self, task: Task) -> Dict[str, Any]:
        """处理任务"""
        if task.type == TaskType.TEST:
            return self._process_test(task)
        elif task.type == TaskType.BUG:
            return self._process_bug_report(task)
        else:
            return {"status": "error", "message": "不支持的 任务类型"}
    
    def _process_test(self, task: Task) -> Dict[str, Any]:
        """处理测试任务"""
        # TODO: 调用 AI 生成测试用例
        # 这里需要实现 AI 测试逻辑
        
        result = {
            "test_plan": {
                "scope": "测试范围",
                "strategy": "测试策略",
                "environment": "测试环境",
                "schedule": "测试计划"
            },
            "test_cases": [
                {
                    "id": "TC-001",
                    "title": "创建项目测试",
                    "priority": "高",
                    "steps": [
                        "1. 登录系统",
                        "2. 点击创建项目",
                        "3. 填写项目信息",
                        "4. 提交创建"
                    ],
                    "expected_result": "项目创建成功，跳转到项目详情页"
                },
                {
                    "id": "TC-002",
                    "title": "任务分配测试",
                    "priority": "高",
                    "steps": [
                        "1. 选择待分配任务",
                        "2. 指定负责人",
                        "3. 确认分配"
                    ],
                    "expected_result": "任务成功分配给指定 Agent"
                }
            ],
            "test_results": {
                "total": 20,
                "passed": 18,
                "failed": 2,
                "blocked": 0
            },
            "coverage": {
                "line_coverage": "85%",
                "branch_coverage": "78%",
                "function_coverage": "92%"
            },
            "bugs": [
                {
                    "id": "BUG-001",
                    "title": "项目名称长度限制不合理",
                    "severity": "中",
                    "description": "项目名称超过 100 字符后无提示"
                }
            ],
            "quality_report": {
                "overall": "良好",
                "recommendation": "建议修复中等及以上级别的 Bug 后发布"
            }
        }
        
        return result
    
    def _process_bug_report(self, task: Task) -> Dict[str, Any]:
        """处理 Bug 报告任务"""
        result = {
            "bug_details": {
                "title": task.title,
                "description": task.description,
                "severity": "高",
                "priority": "中",
                "steps_to_reproduce": [
                    "1. 打开系统",
                    "2. 执行操作 X",
                    "3. 观察结果"
                ],
                "expected_behavior": "预期行为",
                "actual_behavior": "实际行为"
            },
            "analysis": {
                "root_cause": "根本原因分析",
                "impact": "影响范围",
                "workaround": "临时解决方案"
            },
            "recommendation": {
                "priority": "建议优先级",
                "estimated_effort": "预估修复工时",
                "assigned_to": "建议分配给"
            }
        }
        
        return result
