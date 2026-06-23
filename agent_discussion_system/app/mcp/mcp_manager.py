#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具管理器

该模块实现了MCP工具的管理功能，包括：
- 注册和注销MCP工具
- 执行工具（包含权限检查和安全控制）
- 获取工具列表和信息
- 管理工具权限

确保所有MCP工具的执行都经过严格的权限检查和安全控制。
"""

from typing import Dict, Any, List
from app.mcp.mcp_base import MCPBase, MCPPermissionLevel
from app.utils.logger import get_logger

logger = get_logger()


class MCPManager:
    """MCP工具管理器
    
    负责管理所有的MCP工具，包括注册、执行和获取工具信息等功能。
    """
    
    def __init__(self):
        """初始化MCP工具管理器"""
        self.tools: Dict[str, MCPBase] = {}  # 工具字典，key为工具名称，value为工具实例
        self.enabled = True  # 是否启用MCP工具系统
        logger.info("MCP工具管理器初始化完成")
    
    def register_tool(self, tool: MCPBase):
        """注册MCP工具
        
        Args:
            tool (MCPBase): 要注册的MCP工具实例
        """
        if not isinstance(tool, MCPBase):
            logger.error(f"注册失败：{tool} 不是MCPBase的实例")
            return False
        
        self.tools[tool.name] = tool
        logger.info(f"MCP工具已注册：{tool.name}")
        return True
    
    def unregister_tool(self, tool_name: str):
        """注销MCP工具
        
        Args:
            tool_name (str): 要注销的工具名称
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"MCP工具已注销：{tool_name}")
            return True
        else:
            logger.warning(f"注销失败：工具 {tool_name} 不存在")
            return False
    
    def execute_tool(self, tool_name: str, agent_id: str, **kwargs) -> Dict[str, Any]:
        """执行MCP工具
        
        Args:
            tool_name (str): 工具名称
            agent_id (str): 执行工具的智能体ID
            **kwargs: 工具执行参数
        
        Returns:
            Dict[str, Any]: 执行结果，包含status、result和message字段
        """
        # 检查MCP工具系统是否启用
        if not self.enabled:
            return {
                "status": "error",
                "result": None,
                "message": "MCP工具系统已禁用"
            }
        
        # 检查工具是否存在
        if tool_name not in self.tools:
            logger.warning(f"执行失败：工具 {tool_name} 不存在")
            return {
                "status": "error",
                "result": None,
                "message": f"工具 {tool_name} 不存在"
            }
        
        tool = self.tools[tool_name]
        
        # 检查智能体是否有权限使用该工具
        if not tool.is_allowed(agent_id):
            logger.warning(f"智能体 {agent_id} 没有权限使用工具 {tool_name}")
            return {
                "status": "error",
                "result": None,
                "message": f"没有权限使用工具 {tool_name}"
            }
        
        # 执行工具
        logger.debug(f"智能体 {agent_id} 执行工具 {tool_name}，参数：{kwargs}")
        result = tool._execute_safe(**kwargs)
        
        logger.debug(f"工具 {tool_name} 执行结果：{result}")
        return result
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """获取工具信息
        
        Args:
            tool_name (str): 工具名称
        
        Returns:
            Dict[str, Any]: 工具信息，如果工具不存在返回空字典
        """
        if tool_name in self.tools:
            return self.tools[tool_name].get_info()
        else:
            logger.warning(f"获取工具信息失败：工具 {tool_name} 不存在")
            return {}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有可用工具
        
        Returns:
            List[Dict[str, Any]]: 工具信息列表
        """
        return [tool.get_info() for tool in self.tools.values()]
    
    def get_tool(self, tool_name: str) -> MCPBase:
        """获取工具实例
        
        Args:
            tool_name (str): 工具名称
        
        Returns:
            MCPBase: 工具实例，如果工具不存在返回None
        """
        return self.tools.get(tool_name)
    
    def enable(self):
        """启用MCP工具系统"""
        self.enabled = True
        logger.info("MCP工具系统已启用")
    
    def disable(self):
        """禁用MCP工具系统"""
        self.enabled = False
        logger.info("MCP工具系统已禁用")
    
    def is_enabled(self) -> bool:
        """检查MCP工具系统是否启用
        
        Returns:
            bool: 启用返回True，否则返回False
        """
        return self.enabled
    
    def add_agent_to_tool_whitelist(self, tool_name: str, agent_id: str):
        """将智能体添加到工具白名单
        
        Args:
            tool_name (str): 工具名称
            agent_id (str): 智能体ID
        """
        if tool_name in self.tools:
            self.tools[tool_name].add_to_whitelist(agent_id)
            return True
        else:
            logger.warning(f"添加白名单失败：工具 {tool_name} 不存在")
            return False
    
    def remove_agent_from_tool_whitelist(self, tool_name: str, agent_id: str):
        """将智能体从工具白名单中移除
        
        Args:
            tool_name (str): 工具名称
            agent_id (str): 智能体ID
        """
        if tool_name in self.tools:
            self.tools[tool_name].remove_from_whitelist(agent_id)
            return True
        else:
            logger.warning(f"移除白名单失败：工具 {tool_name} 不存在")
            return False
    
    def set_tool_timeout(self, tool_name: str, timeout: int):
        """设置工具执行超时时间
        
        Args:
            tool_name (str): 工具名称
            timeout (int): 超时时间，单位秒
        """
        if tool_name in self.tools:
            self.tools[tool_name].set_timeout(timeout)
            return True
        else:
            logger.warning(f"设置超时时间失败：工具 {tool_name} 不存在")
            return False
    
    def get_tools_by_permission_level(self, permission_level: MCPPermissionLevel) -> List[Dict[str, Any]]:
        """根据权限级别获取工具列表
        
        Args:
            permission_level (MCPPermissionLevel): 权限级别
        
        Returns:
            List[Dict[str, Any]]: 工具信息列表
        """
        return [
            tool.get_info() for tool in self.tools.values()
            if tool.permission_level == permission_level
        ]
