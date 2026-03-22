"""
项目相关枚举定义
"""
from enum import Enum


class ProjectStatus(str, Enum):
    """项目状态"""
    PLANNING = "planning"          # 规划中
    IN_PROGRESS = "in_progress"    # 进行中
    ON_HOLD = "on_hold"            # 暂停
    COMPLETED = "completed"        # 已完成
    CANCELLED = "cancelled"        # 已取消


class TaskType(str, Enum):
    """任务类型"""
    REQUIREMENT = "requirement"    # 需求
    DESIGN = "design"              # 设计
    DEVELOPMENT = "development"    # 开发
    TEST = "test"                  # 测试
    BUG = "bug"                    # Bug
    DOCUMENTATION = "documentation" # 文档


class TaskPriority(str, Enum):
    """任务优先级"""
    HIGH = "high"                  # 高
    MEDIUM = "medium"              # 中
    LOW = "low"                    # 低


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"            # 待处理
    IN_PROGRESS = "in_progress"    # 进行中
    COMPLETED = "completed"        # 已完成
    BLOCKED = "blocked"            # 阻塞
    CANCELLED = "cancelled"        # 已取消


class AgentRole(str, Enum):
    """Agent 角色"""
    PM = "pm"                      # 项目经理
    UI = "ui"                      # UI 设计师
    BACKEND = "backend"            # 后端开发
    QA = "qa"                      # 测试工程师


class AgentStatus(str, Enum):
    """Agent 状态"""
    IDLE = "idle"                  # 空闲
    WORKING = "working"            # 工作中
    OFFLINE = "offline"            # 离线


class WorkflowStatus(str, Enum):
    """工作流状态"""
    PENDING = "pending"            # 待执行
    IN_PROGRESS = "in_progress"    # 执行中
    COMPLETED = "completed"        # 已完成
    FAILED = "failed"              # 失败


class MessageType(str, Enum):
    """消息类型"""
    TASK_ASSIGNED = "task_assigned"          # 任务分配
    TASK_COMPLETED = "task_completed"        # 任务完成
    QUESTION = "question"                    # 提问
    ANSWER = "answer"                        # 回答
    REVIEW_REQUEST = "review_request"        # 评审请求
    REVIEW_RESULT = "review_result"          # 评审结果
    BLOCK = "block"                          # 阻塞通知
    UNBLOCK = "unblock"                      # 解除阻塞
    NOTIFICATION = "notification"            # 通知
