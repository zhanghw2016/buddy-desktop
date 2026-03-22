"""
AI 服务抽象层
支持多种 AI 后端，包括本地 AI（直接使用当前会话）
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseAIService(ABC):
    """AI 服务基类"""
    
    @abstractmethod
    async def chat(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        与 AI 对话
        
        Args:
            prompt: 提示词
            context: 上下文信息
            
        Returns:
            AI 响应
        """
        pass
    
    @abstractmethod
    async def analyze(self, content: str, task_type: str) -> Dict[str, Any]:
        """
        分析内容
        
        Args:
            content: 待分析内容
            task_type: 任务类型
            
        Returns:
            分析结果
        """
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, output_format: str = "text") -> str:
        """
        生成内容
        
        Args:
            prompt: 提示词
            output_format: 输出格式 (text/json/markdown)
            
        Returns:
            生成的内容
        """
        pass


class LocalAIService(BaseAIService):
    """
    本地 AI 服务 - 直接使用当前会话的 AI
    
    这个服务可以让 Agent 直接通过我（AI 助手）来完成工作
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id
        self.conversation_history = []
    
    async def chat(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        与 AI 对话
        
        注意：实际实现需要与前端/后端集成，
        通过 WebSocket 或 API 将请求发送到我这里处理
        """
        # 构建完整提示
        full_prompt = prompt
        if context:
            full_prompt = f"{prompt}\n\n上下文信息：\n{context}"
        
        # 记录对话历史
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # 这里需要通过某种机制将请求发送到我（当前会话的 AI）
        # 实际实现方式：
        # 1. WebSocket 实时通信
        # 2. API 轮询
        # 3. 直接调用（如果在同一进程）
        
        # 模拟返回 - 实际需要实现
        return f"[本地 AI 响应] 正在处理：{prompt[:50]}..."
    
    async def analyze(self, content: str, task_type: str) -> Dict[str, Any]:
        """分析内容"""
        prompt = f"""
请分析以下内容（任务类型：{task_type}）：

{content}

请以结构化的 JSON 格式输出分析结果。
"""
        response = await self.chat(prompt)
        
        # 解析 JSON 响应
        import json
        try:
            return json.loads(response)
        except:
            return {"raw_response": response}
    
    async def generate(self, prompt: str, output_format: str = "text") -> str:
        """生成内容"""
        full_prompt = prompt
        if output_format == "json":
            full_prompt += "\n\n请以 JSON 格式输出。"
        elif output_format == "markdown":
            full_prompt += "\n\n请以 Markdown 格式输出。"
        
        return await self.chat(full_prompt)


class OpenAIService(BaseAIService):
    """OpenAI API 服务（备用方案）"""
    
    def __init__(self, api_key: str, api_base: Optional[str] = None):
        self.api_key = api_key
        self.api_base = api_base or "https://api.openai.com/v1"
    
    async def chat(self, prompt: str, context: Optional[Dict] = None) -> str:
        """调用 OpenAI API"""
        # 实际实现需要安装 openai 库
        # import openai
        # response = await openai.ChatCompletion.acreate(...)
        raise NotImplementedError("需要配置 OpenAI API")
    
    async def analyze(self, content: str, task_type: str) -> Dict[str, Any]:
        """分析内容"""
        raise NotImplementedError("需要配置 OpenAI API")
    
    async def generate(self, prompt: str, output_format: str = "text") -> str:
        """生成内容"""
        raise NotImplementedError("需要配置 OpenAI API")


class AIServiceFactory:
    """AI 服务工厂"""
    
    @staticmethod
    def create(service_type: str = "local", **kwargs) -> BaseAIService:
        """
        创建 AI 服务
        
        Args:
            service_type: 服务类型 (local/openai/claude)
            **kwargs: 服务参数
            
        Returns:
            AI 服务实例
        """
        if service_type == "local":
            return LocalAIService(**kwargs)
        elif service_type == "openai":
            return OpenAIService(**kwargs)
        else:
            raise ValueError(f"不支持的 AI 服务类型: {service_type}")
