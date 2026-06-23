#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讨论历史数据访问层

负责讨论相关的数据库操作，包括创建讨论、获取讨论列表、添加讨论消息等功能。
"""

from typing import List, Dict, Optional

from app.database import db_manager
from app.utils.logger import get_logger

logger = get_logger()


class DiscussionRepository:
    """讨论数据访问类
    
    负责讨论相关的数据库操作，包括：
    - 创建讨论
    - 获取所有讨论
    - 根据ID获取讨论
    - 更新讨论状态
    - 删除讨论
    - 添加讨论消息
    - 获取讨论消息
    """
    
    def __init__(self):
        """初始化讨论数据访问层
        
        使用全局数据库管理器实例。
        """
        self.db = db_manager
    
    def create_discussion(self, title: str, description: str = "") -> str:
        """创建新讨论
        
        Args:
            title: 讨论标题
            description: 讨论描述
        
        Returns:
            str: 创建的讨论ID
        """
        try:
            import uuid
            discussion_id = f"discussion_{uuid.uuid4().hex[:12]}"
            
            query = """
            INSERT INTO discussions (discussion_id, title, description, status)
            VALUES (?, ?, ?, ?)
            """
            
            self.db.execute(
                query, 
                (discussion_id, title, description, "in_progress")
            )
            
            self.db.commit()
            logger.info(f"讨论创建成功：{title} (ID: {discussion_id})")
            return discussion_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建讨论失败：{e}")
            raise
    
    def get_all_discussions(self, status: Optional[str] = None) -> List[Dict[str, any]]:
        """获取所有讨论
        
        Args:
            status: 讨论状态过滤，可选值：in_progress/ended
        
        Returns:
            List[Dict[str, any]]: 讨论列表
        """
        try:
            if status:
                query = """SELECT * FROM discussions WHERE status = ? ORDER BY created_at DESC"""
                discussions = self.db.fetch_all(query, (status,))
            else:
                query = """SELECT * FROM discussions ORDER BY created_at DESC"""
                discussions = self.db.fetch_all(query)
            
            logger.debug(f"获取讨论列表成功，共 {len(discussions)} 个")
            return discussions
            
        except Exception as e:
            logger.error(f"获取讨论列表失败：{e}")
            raise
    
    def get_discussion_by_id(self, discussion_id: str) -> Optional[Dict[str, any]]:
        """根据ID获取讨论
        
        Args:
            discussion_id: 讨论ID
        
        Returns:
            Optional[Dict[str, any]]: 讨论信息，不存在则返回None
        """
        try:
            query = """SELECT * FROM discussions WHERE discussion_id = ?"""
            discussion = self.db.fetch_one(query, (discussion_id,))
            
            if discussion:
                logger.debug(f"根据ID {discussion_id} 获取讨论成功")
            else:
                logger.debug(f"未找到ID为 {discussion_id} 的讨论")
            
            return discussion
            
        except Exception as e:
            logger.error(f"根据ID获取讨论失败：{e}")
            raise
    
    def update_discussion_status(self, discussion_id: str, status: str) -> bool:
        """更新讨论状态
        
        Args:
            discussion_id: 讨论ID
            status: 新状态，可选值：in_progress/ended
        
        Returns:
            bool: 更新成功返回True，否则返回False
        """
        try:
            # 检查讨论是否存在
            existing_discussion = self.get_discussion_by_id(discussion_id)
            if not existing_discussion:
                logger.warning(f"更新讨论状态失败：未找到ID为 {discussion_id} 的讨论")
                return False
            
            query = """
            UPDATE discussions 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE discussion_id = ?
            """
            
            # 如果状态为ended，更新结束时间
            if status == "ended":
                query = """
                UPDATE discussions 
                SET status = ?, ended_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE discussion_id = ?
                """
            
            self.db.execute(query, (status, discussion_id))
            self.db.commit()
            
            logger.info(f"讨论状态更新成功：{discussion_id} -> {status}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新讨论状态失败：{e}")
            raise
    
    def update_discussion_round(self, discussion_id: str, round_number: int) -> bool:
        """更新讨论当前轮次
        
        Args:
            discussion_id: 讨论ID
            round_number: 当前轮次
        
        Returns:
            bool: 更新成功返回True，否则返回False
        """
        try:
            # 检查讨论是否存在
            existing_discussion = self.get_discussion_by_id(discussion_id)
            if not existing_discussion:
                logger.warning(f"更新讨论轮次失败：未找到ID为 {discussion_id} 的讨论")
                return False
            
            query = """
            UPDATE discussions 
            SET current_round = ?, updated_at = CURRENT_TIMESTAMP
            WHERE discussion_id = ?
            """
            
            self.db.execute(query, (round_number, discussion_id))
            self.db.commit()
            
            logger.info(f"讨论轮次更新成功：{discussion_id} -> 第 {round_number} 轮")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新讨论轮次失败：{e}")
            raise
    
    def delete_discussion(self, discussion_id: str) -> bool:
        """删除讨论
        
        Args:
            discussion_id: 讨论ID
        
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 检查讨论是否存在
            existing_discussion = self.get_discussion_by_id(discussion_id)
            if not existing_discussion:
                logger.warning(f"删除讨论失败：未找到ID为 {discussion_id} 的讨论")
                return False
            
            query = """DELETE FROM discussions WHERE discussion_id = ?"""
            self.db.execute(query, (discussion_id,))
            self.db.commit()
            
            logger.info(f"讨论删除成功：{discussion_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除讨论失败：{e}")
            raise
    
    def add_discussion_message(self, discussion_id: str, agent_id: str, content: str, 
                              round_number: int = 1, message_type: str = "normal") -> str:
        """添加讨论消息
        
        Args:
            discussion_id: 讨论ID
            agent_id: 智能体ID
            content: 消息内容
            round_number: 轮次号，默认为1
            message_type: 消息类型，可选值：normal/system，默认为normal
        
        Returns:
            str: 创建的消息ID
        """
        try:
            import uuid
            message_id = f"message_{uuid.uuid4().hex[:12]}"
            
            query = """
            INSERT INTO discussion_messages 
            (message_id, discussion_id, agent_id, round_number, content, message_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute(
                query, 
                (message_id, discussion_id, agent_id, round_number, content, message_type)
            )
            
            self.db.commit()
            logger.debug(f"讨论消息添加成功：{discussion_id} - {agent_id}")
            return message_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加讨论消息失败：{e}")
            raise
    
    def get_discussion_messages(self, discussion_id: str, order_by: str = "created_at") -> List[Dict[str, any]]:
        """获取讨论的所有消息
        
        Args:
            discussion_id: 讨论ID
            order_by: 排序字段，默认为created_at
        
        Returns:
            List[Dict[str, any]]: 讨论消息列表
        """
        try:
            query = f"""
            SELECT * FROM discussion_messages 
            WHERE discussion_id = ? 
            ORDER BY {order_by}
            """
            
            messages = self.db.fetch_all(query, (discussion_id,))
            logger.debug(f"获取讨论消息成功，共 {len(messages)} 条")
            return messages
            
        except Exception as e:
            logger.error(f"获取讨论消息失败：{e}")
            raise
    
    def get_discussion_messages_by_round(self, discussion_id: str, round_number: int) -> List[Dict[str, any]]:
        """获取讨论特定轮次的消息
        
        Args:
            discussion_id: 讨论ID
            round_number: 轮次号
        
        Returns:
            List[Dict[str, any]]: 特定轮次的讨论消息列表
        """
        try:
            query = """
            SELECT * FROM discussion_messages 
            WHERE discussion_id = ? AND round_number = ? 
            ORDER BY created_at
            """
            
            messages = self.db.fetch_all(query, (discussion_id, round_number))
            logger.debug(f"获取讨论第 {round_number} 轮消息成功，共 {len(messages)} 条")
            return messages
            
        except Exception as e:
            logger.error(f"获取讨论轮次消息失败：{e}")
            raise
    
    def get_latest_discussion_message(self, discussion_id: str) -> Optional[Dict[str, any]]:
        """获取讨论的最新消息
        
        Args:
            discussion_id: 讨论ID
        
        Returns:
            Optional[Dict[str, any]]: 最新消息，不存在则返回None
        """
        try:
            query = """
            SELECT * FROM discussion_messages 
            WHERE discussion_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
            """
            
            message = self.db.fetch_one(query, (discussion_id,))
            
            if message:
                logger.debug(f"获取讨论最新消息成功：{discussion_id}")
            else:
                logger.debug(f"未找到讨论 {discussion_id} 的消息")
            
            return message
            
        except Exception as e:
            logger.error(f"获取讨论最新消息失败：{e}")
            raise
    
    def get_discussion_count(self) -> int:
        """获取讨论数量
        
        Returns:
            int: 讨论数量
        """
        try:
            query = """SELECT COUNT(*) as count FROM discussions"""
            result = self.db.fetch_one(query)
            count = result['count'] if result else 0
            logger.debug(f"获取讨论数量成功：{count}")
            return count
            
        except Exception as e:
            logger.error(f"获取讨论数量失败：{e}")
            raise
