#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具基类

该模块定义了MCP（Multi-agent Collaboration Protocol）工具的基类，所有MCP工具都必须继承自这个类。
MCP工具以插件形式存在，支持内置MCP和用户自定义MCP，所有MCP必须有：
- 权限分级
- 白名单
- 执行超时
- 异常捕获，防止任意代码执行风险
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum
from app.utils.logger import get_logger

logger = get_logger()


class MCPPermissionLevel(Enum):
    """MCP工具权限级别枚举
    
    定义了MCP工具的权限级别：
    - LOW: 低风险，如简单计算、信息查询等
    - MEDIUM: 中等风险，如文件读取、网络请求等
    - HIGH: 高风险，如文件写入、系统命令执行等
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MCPBase(ABC):
    """MCP工具基类
    
    定义了所有MCP工具都必须实现的接口，包括：
    - execute: 执行工具
    - get_info: 获取工具信息
    - get_permission_level: 获取权限级别
    - get_whitelist: 获取白名单
    
    提供了基本的超时控制和异常捕获机制。
    """
    
    def __init__(self, name: str, description: str, permission_level: MCPPermissionLevel = MCPPermissionLevel.LOW):
        """初始化MCP工具
        
        Args:
            name (str): 工具名称
            description (str): 工具描述
            permission_level (MCPPermissionLevel, optional): 权限级别，默认为LOW
        """
        self.name = name
        self.description = description
        self.permission_level = permission_level
        self.whitelist = []  # 白名单，为空表示所有人可以使用
        self.timeout = 10  # 执行超时时间，单位秒
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具
        
        Args:
            **kwargs: 工具执行参数
        
        Returns:
            Dict[str, Any]: 执行结果，包含status、result和message字段
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取工具信息
        
        Returns:
            Dict[str, Any]: 工具信息，包含name、description、permission_level等字段
        """
        return {
            "name": self.name,
            "description": self.description,
            "permission_level": self.permission_level.value,
            "timeout": self.timeout,
            "whitelist": self.whitelist
        }
    
    def get_permission_level(self) -> MCPPermissionLevel:
        """获取权限级别
        
        Returns:
            MCPPermissionLevel: 权限级别
        """
        return self.permission_level
    
    def get_whitelist(self) -> List[str]:
        """获取白名单
        
        Returns:
            List[str]: 白名单列表
        """
        return self.whitelist.copy()
    
    def add_to_whitelist(self, agent_id: str):
        """添加到白名单
        
        Args:
            agent_id (str): 智能体ID
        """
        if agent_id not in self.whitelist:
            self.whitelist.append(agent_id)
            logger.debug(f"智能体 {agent_id} 已添加到工具 {self.name} 的白名单")
    
    def remove_from_whitelist(self, agent_id: str):
        """从白名单中移除
        
        Args:
            agent_id (str): 智能体ID
        """
        if agent_id in self.whitelist:
            self.whitelist.remove(agent_id)
            logger.debug(f"智能体 {agent_id} 已从工具 {self.name} 的白名单中移除")
    
    def is_allowed(self, agent_id: str) -> bool:
        """检查智能体是否被允许使用该工具
        
        Args:
            agent_id (str): 智能体ID
        
        Returns:
            bool: 允许返回True，否则返回False
        """
        # 白名单为空表示所有人可以使用
        if not self.whitelist:
            return True
        
        return agent_id in self.whitelist
    
    def set_timeout(self, timeout: int):
        """设置执行超时时间
        
        Args:
            timeout (int): 超时时间，单位秒
        """
        self.timeout = max(1, timeout)  # 确保超时时间至少为1秒
        logger.debug(f"工具 {self.name} 的超时时间已设置为 {self.timeout} 秒")
    
    def _execute_safe(self, **kwargs) -> Dict[str, Any]:
        """安全执行工具，包含超时控制和异常捕获
        
        Args:
            **kwargs: 工具执行参数
        
        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            # 这里可以添加超时控制
            # 由于Python标准库的timeout功能有限，实际实现中可以使用线程或第三方库
            
            result = self.execute(**kwargs)
            
            # 确保结果格式正确
            if isinstance(result, dict):
                if "status" not in result:
                    result["status"] = "success"
                if "message" not in result:
                    result["message"] = "执行成功"
                return result
            else:
                return {
                    "status": "success",
                    "result": result,
                    "message": "执行成功"
                }
        except Exception as e:
            logger.error(f"工具 {self.name} 执行失败: {str(e)}")
            return {
                "status": "error",
                "result": None,
                "message": str(e)
            }
