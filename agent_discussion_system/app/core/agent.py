#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体（Agent）类

该模块实现了智能体的基本属性和方法，是多智能体系统的基本组成单元。
每个智能体包含唯一标识、显示名称、使用的AI模型、角色描述、权限集合和独立上下文记忆。
"""

from typing import List, Dict, Any
from enum import Enum
from app.utils.logger import get_logger

logger = get_logger()


class AgentPermission(Enum):
    """智能体权限枚举
    
    定义了智能体在讨论中的各种权限：
    - CAN_SPEAK：可以发言
    - CAN_START_NEXT_ROUND：可以开始下一轮讨论
    - CAN_TERMINATE_DISCUSSION：可以终止讨论
    """
    CAN_SPEAK = "can_speak"
    CAN_START_NEXT_ROUND = "can_start_next_round"
    CAN_TERMINATE_DISCUSSION = "can_terminate_discussion"


class Agent:
    """智能体类
    
    表示多智能体系统中的一个智能体，包含以下属性：
    - agent_id：内部唯一标识
    - name：显示名称
    - model_id：使用的AI模型ID
    - role_description：角色描述
    - permissions：权限集合
    - context_memory：独立上下文记忆
    """
    
    def __init__(self, agent_id: str, name: str, model_id: str, role_description: str, permissions: List[AgentPermission]):
        """初始化智能体
        
        Args:
            agent_id (str): 内部唯一标识
            name (str): 显示名称
            model_id (str): 使用的AI模型ID
            role_description (str): 角色描述
            permissions (List[AgentPermission]): 权限集合
        """
        self.agent_id = agent_id
        self.name = name
        self.model_id = model_id
        self.role_description = role_description
        self.permissions = permissions
        self.context_memory = []  # 上下文记忆，存储该智能体的历史消息
    
    def has_permission(self, permission: AgentPermission) -> bool:
        """检查智能体是否拥有特定权限
        
        Args:
            permission (AgentPermission): 要检查的权限
        
        Returns:
            bool: 拥有权限返回True，否则返回False
        """
        return permission in self.permissions
    
    def add_to_memory(self, message: Dict[str, Any]):
        """将消息添加到智能体的上下文记忆中
        
        Args:
            message (Dict[str, Any]): 要添加的消息，包含role和content字段
        """
        self.context_memory.append(message)
        logger.debug(f"智能体 {self.name} 记忆添加成功，当前记忆长度: {len(self.context_memory)}")
    
    def clear_memory(self):
        """清空智能体的上下文记忆"""
        self.context_memory.clear()
        logger.debug(f"智能体 {self.name} 记忆已清空")
    
    def get_context(self, max_tokens: int = None) -> List[Dict[str, Any]]:
        """获取智能体的上下文记忆
        
        Args:
            max_tokens (int, optional): 最大令牌数，用于限制上下文长度
        
        Returns:
            List[Dict[str, Any]]: 上下文记忆列表
        """
        # 当前实现简单返回所有记忆，未来可以根据令牌数进行截断
        return self.context_memory.copy()
    
    def generate_prompt(self, discussion_topic: str, recent_messages: List[Dict[str, Any]]) -> str:
        """生成智能体的提示词
        
        Args:
            discussion_topic (str): 讨论主题
            recent_messages (List[Dict[str, Any]]): 最近的讨论消息
        
        Returns:
            str: 生成的提示词
        """
        # 构建系统提示
        system_prompt = f"""你是{self.name}，{self.role_description}
        
讨论主题：{discussion_topic}
        
你的权限：{[perm.value for perm in self.permissions]}
        
讨论规则：
1. 请根据你的角色和讨论主题进行发言
2. 请基于最近的讨论内容进行回应
3. 如果你的发言包含控制指令，请使用以下格式：
   - 要开始下一轮讨论，请在发言末尾添加："NEXT_ROUND"
   - 要终止讨论，请在发言末尾添加："END_DISCUSSION"
4. 控制指令仅在你拥有相应权限时生效
5. 请保持发言简洁明了，聚焦讨论主题
        
最近的讨论内容：
{chr(10).join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])}
        
请开始你的发言："""
        
        return system_prompt
    
    def process_response(self, response: str) -> Dict[str, Any]:
        """处理智能体的响应
        
        Args:
            response (str): 智能体的原始响应
        
        Returns:
            Dict[str, Any]: 处理后的响应，包含content和control字段
        """
        content = response
        control = None
        
        # 检查是否包含控制指令
        if "NEXT_ROUND" in response:
            content = response.replace("NEXT_ROUND", "").strip()
            control = "NEXT_ROUND"
        elif "END_DISCUSSION" in response:
            content = response.replace("END_DISCUSSION", "").strip()
            control = "END_DISCUSSION"
        
        return {
            "content": content,
            "control": control
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """将智能体对象转换为字典，用于序列化
        
        Returns:
            Dict[str, Any]: 智能体的字典表示
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "model_id": self.model_id,
            "role_description": self.role_description,
            "permissions": [perm.value for perm in self.permissions],
            "context_memory": self.context_memory
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """从字典创建智能体对象
        
        Args:
            data (Dict[str, Any]): 智能体的字典表示
        
        Returns:
            Agent: 创建的智能体对象
        """
        permissions = [AgentPermission(perm) for perm in data["permissions"]]
        agent = cls(
            agent_id=data["agent_id"],
            name=data["name"],
            model_id=data["model_id"],
            role_description=data["role_description"],
            permissions=permissions
        )
        agent.context_memory = data.get("context_memory", [])
        return agent
    
    def __str__(self) -> str:
        """返回智能体的字符串表示
        
        Returns:
            str: 智能体的字符串表示
        """
        return f"Agent(id={self.agent_id}, name={self.name}, model={self.model_id})"
    
    def __repr__(self) -> str:
        """返回智能体的详细字符串表示
        
        Returns:
            str: 智能体的详细字符串表示
        """
        return self.__str__()
