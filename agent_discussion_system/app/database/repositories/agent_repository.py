#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体数据访问层

负责智能体相关的数据库操作，包括获取、创建、更新和删除智能体等功能。
"""

import json
from typing import List, Dict, Optional

from app.database import db_manager
from app.utils.logger import get_logger

logger = get_logger()


class AgentRepository:
    """智能体数据访问类
    
    负责智能体相关的数据库操作，包括：
    - 获取所有智能体
    - 根据ID获取智能体
    - 创建智能体
    - 更新智能体
    - 删除智能体
    """
    
    def __init__(self):
        """初始化智能体数据访问层
        
        使用全局数据库管理器实例。
        """
        self.db = db_manager
    
    def get_all_agents(self) -> List[Dict[str, any]]:
        """获取所有智能体
        
        Returns:
            List[Dict[str, any]]: 智能体列表，每个智能体包含完整信息
        """
        try:
            query = """SELECT * FROM agents ORDER BY created_at"""
            agents = self.db.fetch_all(query)
            
            # 解析JSON字段
            for agent in agents:
                agent['permissions'] = json.loads(agent['permissions'])
            
            logger.debug(f"获取所有智能体成功，共 {len(agents)} 个")
            return agents
            
        except Exception as e:
            logger.error(f"获取所有智能体失败：{e}")
            raise
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Dict[str, any]]:
        """根据ID获取智能体
        
        Args:
            agent_id: 智能体ID
        
        Returns:
            Optional[Dict[str, any]]: 智能体信息，不存在则返回None
        """
        try:
            query = """SELECT * FROM agents WHERE agent_id = ?"""
            agent = self.db.fetch_one(query, (agent_id,))
            
            if agent:
                # 解析JSON字段
                agent['permissions'] = json.loads(agent['permissions'])
                logger.debug(f"根据ID {agent_id} 获取智能体成功")
            else:
                logger.debug(f"未找到ID为 {agent_id} 的智能体")
            
            return agent
            
        except Exception as e:
            logger.error(f"根据ID获取智能体失败：{e}")
            raise
    
    def create_agent(self, agent_data: Dict[str, any]) -> str:
        """创建智能体
        
        Args:
            agent_data: 智能体数据，包含以下字段：
                - agent_id: 智能体ID
                - name: 智能体名称
                - model_id: 模型ID
                - role_description: 角色描述
                - permissions: 权限列表
        
        Returns:
            str: 创建的智能体ID
        """
        try:
            # 准备SQL语句
            query = """
            INSERT INTO agents (agent_id, name, model_id, role_description, permissions)
            VALUES (?, ?, ?, ?, ?)
            """
            
            # 序列化权限列表为JSON字符串
            permissions_json = json.dumps(agent_data['permissions'])
            
            # 执行插入操作
            self.db.execute(
                query, 
                (
                    agent_data['agent_id'],
                    agent_data['name'],
                    agent_data['model_id'],
                    agent_data['role_description'],
                    permissions_json
                )
            )
            
            self.db.commit()
            logger.info(f"智能体创建成功：{agent_data['name']} (ID: {agent_data['agent_id']})")
            return agent_data['agent_id']
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建智能体失败：{e}")
            raise
    
    def update_agent(self, agent_id: str, agent_data: Dict[str, any]) -> bool:
        """更新智能体
        
        Args:
            agent_id: 智能体ID
            agent_data: 要更新的智能体数据，可包含以下字段：
                - name: 智能体名称
                - model_id: 模型ID
                - role_description: 角色描述
                - permissions: 权限列表
        
        Returns:
            bool: 更新成功返回True，否则返回False
        """
        try:
            # 检查智能体是否存在
            existing_agent = self.get_agent_by_id(agent_id)
            if not existing_agent:
                logger.warning(f"更新智能体失败：未找到ID为 {agent_id} 的智能体")
                return False
            
            # 准备更新字段
            update_fields = []
            update_values = []
            
            if 'name' in agent_data:
                update_fields.append("name = ?")
                update_values.append(agent_data['name'])
            
            if 'model_id' in agent_data:
                update_fields.append("model_id = ?")
                update_values.append(agent_data['model_id'])
            
            if 'role_description' in agent_data:
                update_fields.append("role_description = ?")
                update_values.append(agent_data['role_description'])
            
            if 'permissions' in agent_data:
                update_fields.append("permissions = ?")
                update_values.append(json.dumps(agent_data['permissions']))
            
            # 更新更新时间
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            if not update_fields:
                logger.info(f"智能体 {agent_id} 未进行任何更新")
                return True
            
            # 构建SQL语句
            query = f"""
            UPDATE agents 
            SET {', '.join(update_fields)} 
            WHERE agent_id = ?
            """
            
            update_values.append(agent_id)
            
            # 执行更新操作
            self.db.execute(query, tuple(update_values))
            self.db.commit()
            
            logger.info(f"智能体更新成功：{agent_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新智能体失败：{e}")
            raise
    
    def delete_agent(self, agent_id: str) -> bool:
        """删除智能体
        
        Args:
            agent_id: 智能体ID
        
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 检查智能体是否存在
            existing_agent = self.get_agent_by_id(agent_id)
            if not existing_agent:
                logger.warning(f"删除智能体失败：未找到ID为 {agent_id} 的智能体")
                return False
            
            # 执行删除操作
            query = """DELETE FROM agents WHERE agent_id = ?"""
            self.db.execute(query, (agent_id,))
            self.db.commit()
            
            logger.info(f"智能体删除成功：{agent_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除智能体失败：{e}")
            raise
    
    def get_agent_count(self) -> int:
        """获取智能体数量
        
        Returns:
            int: 智能体数量
        """
        try:
            query = """SELECT COUNT(*) as count FROM agents"""
            result = self.db.fetch_one(query)
            count = result['count'] if result else 0
            logger.debug(f"获取智能体数量成功：{count}")
            return count
            
        except Exception as e:
            logger.error(f"获取智能体数量失败：{e}")
            raise
