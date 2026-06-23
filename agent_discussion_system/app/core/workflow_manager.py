#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讨论流程管理类

该模块负责管理多智能体讨论的流程，包括：
- 讨论流程的配置和执行
- 智能体的调度顺序
- 讨论轮次的管理
- 控制指令的处理
"""

from typing import List, Dict, Any
from app.core.agent import Agent, AgentPermission
from app.database.repositories.agent_repository import AgentRepository
from app.utils.logger import get_logger

logger = get_logger()


class WorkflowManager:
    """讨论流程管理类
    
    负责管理多智能体讨论的流程，包括：
    - 讨论流程的配置和执行
    - 智能体的调度顺序
    - 讨论轮次的管理
    - 控制指令的处理
    """
    
    def __init__(self):
        """初始化流程管理类"""
        self.agents = {}  # 智能体字典，key为agent_id，value为Agent对象
        self.workflow = []  # 讨论流程，包含智能体ID的列表，按发言顺序排列
        self.current_round = 0  # 当前轮次
        self.current_agent_index = 0  # 当前发言的智能体索引
        self.agent_repo = AgentRepository()  # 智能体数据访问层实例
    
    def load_agents_from_database(self):
        """从数据库加载智能体
        
        从数据库中获取所有智能体，并添加到流程管理器中。
        """
        try:
            # 从数据库获取所有智能体
            agent_dicts = self.agent_repo.get_all_agents()
            
            # 清空现有智能体
            self.agents.clear()
            
            # 创建Agent对象并添加到流程管理器
            for agent_dict in agent_dicts:
                # 将权限列表转换为AgentPermission枚举
                permissions = []
                for perm in agent_dict['permissions']:
                    try:
                        permissions.append(AgentPermission[perm])
                    except KeyError:
                        logger.warning(f"无效的智能体权限：{perm}，已忽略")
                        continue
                
                # 创建Agent对象
                agent = Agent(
                    agent_id=agent_dict['agent_id'],
                    name=agent_dict['name'],
                    model_id=agent_dict['model_id'],
                    role_description=agent_dict['role_description'],
                    permissions=permissions
                )
                
                # 添加到流程管理器
                self.add_agent(agent)
            
            logger.info(f"已从数据库加载 {len(self.agents)} 个智能体")
            
            # 如果有智能体，设置默认流程
            if self.agents:
                # 默认按agent_id排序
                default_workflow = sorted(self.agents.keys())
                self.set_workflow(default_workflow)
            
        except Exception as e:
            logger.error(f"从数据库加载智能体失败：{e}")
        
    def add_agent(self, agent: Agent):
        """添加智能体到流程管理器
        
        Args:
            agent (Agent): 要添加的智能体
        """
        self.agents[agent.agent_id] = agent
        logger.info(f"智能体 {agent.name} 已添加到流程管理器")
    
    def remove_agent(self, agent_id: str):
        """从流程管理器中移除智能体
        
        Args:
            agent_id (str): 要移除的智能体ID
        """
        if agent_id in self.agents:
            agent_name = self.agents[agent_id].name
            del self.agents[agent_id]
            # 同时从流程中移除该智能体
            self.workflow = [aid for aid in self.workflow if aid != agent_id]
            logger.info(f"智能体 {agent_name} 已从流程管理器中移除")
    
    def set_workflow(self, agent_ids: List[str]):
        """设置讨论流程
        
        Args:
            agent_ids (List[str]): 智能体ID列表，按发言顺序排列
        """
        # 验证所有智能体ID都存在
        valid_agent_ids = []
        for agent_id in agent_ids:
            if agent_id in self.agents:
                valid_agent_ids.append(agent_id)
            else:
                logger.warning(f"智能体ID {agent_id} 不存在，已跳过")
        
        self.workflow = valid_agent_ids
        logger.info(f"讨论流程已设置，包含 {len(self.workflow)} 个智能体")
    
    def get_next_agent(self) -> Agent:
        """获取下一个发言的智能体
        
        Returns:
            Agent: 下一个发言的智能体，如果没有则返回None
        """
        if not self.workflow:
            logger.warning("讨论流程为空，无法获取下一个智能体")
            return None
        
        # 获取当前智能体ID
        agent_id = self.workflow[self.current_agent_index]
        
        # 更新智能体索引
        self.current_agent_index = (self.current_agent_index + 1) % len(self.workflow)
        
        # 如果索引回到0，说明一轮讨论结束
        if self.current_agent_index == 0:
            self.current_round += 1
            logger.info(f"第 {self.current_round} 轮讨论开始")
        
        return self.agents[agent_id]
    
    def process_control_command(self, agent: Agent, command: str) -> Dict[str, Any]:
        """处理智能体的控制指令
        
        Args:
            agent (Agent): 发送控制指令的智能体
            command (str): 控制指令
        
        Returns:
            Dict[str, Any]: 处理结果，包含success和message字段
        """
        if command == "NEXT_ROUND":
            # 检查智能体是否有开始下一轮的权限
            if agent.has_permission(AgentPermission.CAN_START_NEXT_ROUND):
                self.start_next_round()
                return {
                    "success": True,
                    "message": f"智能体 {agent.name} 已开始下一轮讨论"
                }
            else:
                logger.warning(f"智能体 {agent.name} 没有开始下一轮讨论的权限")
                return {
                    "success": False,
                    "message": f"智能体 {agent.name} 没有开始下一轮讨论的权限"
                }
        
        elif command == "END_DISCUSSION":
            # 检查智能体是否有终止讨论的权限
            if agent.has_permission(AgentPermission.CAN_TERMINATE_DISCUSSION):
                return {
                    "success": True,
                    "message": f"智能体 {agent.name} 已终止讨论",
                    "terminate": True
                }
            else:
                logger.warning(f"智能体 {agent.name} 没有终止讨论的权限")
                return {
                    "success": False,
                    "message": f"智能体 {agent.name} 没有终止讨论的权限"
                }
        
        else:
            logger.warning(f"未知的控制指令: {command}")
            return {
                "success": False,
                "message": f"未知的控制指令: {command}"
            }
    
    def start_next_round(self):
        """开始下一轮讨论"""
        self.current_agent_index = 0
        self.current_round += 1
        logger.info(f"第 {self.current_round} 轮讨论开始")
    
    def reset(self):
        """重置讨论流程"""
        self.current_round = 0
        self.current_agent_index = 0
        # 清空所有智能体的记忆
        for agent in self.agents.values():
            agent.clear_memory()
        logger.info("讨论流程已重置")
    
    def get_current_round(self) -> int:
        """获取当前轮次
        
        Returns:
            int: 当前轮次
        """
        return self.current_round
    
    def get_workflow(self) -> List[str]:
        """获取当前讨论流程
        
        Returns:
            List[str]: 智能体ID列表，按发言顺序排列
        """
        return self.workflow.copy()
    
    def get_agents(self) -> Dict[str, Agent]:
        """获取所有智能体
        
        Returns:
            Dict[str, Agent]: 智能体字典
        """
        return self.agents.copy()
    
    def has_agent(self, agent_id: str) -> bool:
        """检查智能体是否存在
        
        Args:
            agent_id (str): 智能体ID
        
        Returns:
            bool: 存在返回True，否则返回False
        """
        return agent_id in self.agents
