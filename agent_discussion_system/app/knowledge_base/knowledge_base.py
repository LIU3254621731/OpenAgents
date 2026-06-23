#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地知识库管理

该模块实现了本地知识库管理功能，包括：
- 上传本地文件
- 构建向量索引
- 用于RAG检索
- 配置哪些Agent可访问知识库

知识库模块与主逻辑解耦，作为可选能力注入。
"""

import os
from typing import List, Dict, Any, Set
from app.knowledge_base.vector_store import VectorStore
from app.mcp.file_mcp import FileMCP
from app.utils.logger import get_logger

logger = get_logger()


class KnowledgeBase:
    """本地知识库管理类
    
    负责本地知识库的管理，包括：
    - 文件上传和处理
    - 向量索引构建
    - RAG检索
    - 访问控制
    """
    
    def __init__(self, vector_store_path: str = None, enabled: bool = True):
        """初始化知识库
        
        Args:
            vector_store_path (str, optional): 向量索引存储路径，默认为None
            enabled (bool, optional): 是否启用知识库，默认为True
        """
        self.enabled = enabled
        self.vector_store = VectorStore(vector_store_path)
        self.allowed_agents: Set[str] = set()  # 允许访问知识库的智能体ID集合
        self.file_mcp = FileMCP()  # 文件读取工具
        
        logger.info("知识库初始化完成")
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """添加文档到知识库
        
        Args:
            content (str): 文档内容
            metadata (Dict[str, Any], optional): 文档元数据，默认为None
        
        Returns:
            int: 文档ID
        """
        if not self.enabled:
            logger.warning("知识库已禁用，无法添加文档")
            return -1
        
        return self.vector_store.add_document(content, metadata)
    
    def upload_file(self, file_path: str, agent_id: str = None) -> Dict[str, Any]:
        """上传文件到知识库
        
        Args:
            file_path (str): 文件路径
            agent_id (str, optional): 上传文件的智能体ID，默认为None
        
        Returns:
            Dict[str, Any]: 上传结果，包含status、result和message字段
        """
        if not self.enabled:
            return {
                "status": "error",
                "result": None,
                "message": "知识库已禁用"
            }
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "result": None,
                "message": f"文件不存在: {file_path}"
            }
        
        # 使用FileMCP读取文件内容
        result = self.file_mcp.execute(file_path=file_path)
        
        if result["status"] == "success":
            # 添加到知识库
            doc_id = self.add_document(
                content=result["result"]["content"],
                metadata={
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "uploaded_by": agent_id,
                    "file_size": result["result"]["file_size"]
                }
            )
            
            return {
                "status": "success",
                "result": {
                    "doc_id": doc_id,
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_size": result["result"]["file_size"]
                },
                "message": f"文件已成功上传到知识库，文档ID: {doc_id}"
            }
        else:
            return result
    
    def search(self, query: str, k: int = 5, agent_id: str = None) -> List[Dict[str, Any]]:
        """检索知识库
        
        Args:
            query (str): 检索查询
            k (int, optional): 返回的文档数量，默认为5
            agent_id (str, optional): 执行检索的智能体ID，默认为None
        
        Returns:
            List[Dict[str, Any]]: 检索结果列表
        """
        if not self.enabled:
            logger.warning("知识库已禁用，无法检索")
            return []
        
        # 检查智能体是否有权限访问知识库
        if agent_id and self.allowed_agents and agent_id not in self.allowed_agents:
            logger.warning(f"智能体 {agent_id} 没有权限访问知识库")
            return []
        
        # 执行检索
        results = self.vector_store.search(query, k)
        logger.debug(f"知识库检索完成，查询: {query}，返回 {len(results)} 个结果")
        return results
    
    def add_agent_access(self, agent_id: str):
        """允许智能体访问知识库
        
        Args:
            agent_id (str): 智能体ID
        """
        self.allowed_agents.add(agent_id)
        logger.debug(f"智能体 {agent_id} 已被允许访问知识库")
    
    def remove_agent_access(self, agent_id: str):
        """移除智能体的知识库访问权限
        
        Args:
            agent_id (str): 智能体ID
        """
        if agent_id in self.allowed_agents:
            self.allowed_agents.remove(agent_id)
            logger.debug(f"智能体 {agent_id} 的知识库访问权限已被移除")
    
    def clear_access_control(self):
        """清除所有访问控制，允许所有智能体访问知识库"""
        self.allowed_agents.clear()
        logger.debug("知识库访问控制已清除，允许所有智能体访问")
    
    def is_agent_allowed(self, agent_id: str) -> bool:
        """检查智能体是否允许访问知识库
        
        Args:
            agent_id (str): 智能体ID
        
        Returns:
            bool: 允许访问返回True，否则返回False
        """
        # 空集合表示允许所有智能体访问
        if not self.allowed_agents:
            return True
        
        return agent_id in self.allowed_agents
    
    def get_document_count(self) -> int:
        """获取知识库中的文档数量
        
        Returns:
            int: 文档数量
        """
        return self.vector_store.get_document_count()
    
    def clear(self):
        """清空知识库
        
        Returns:
            bool: 清空成功返回True，否则返回False
        """
        if not self.enabled:
            logger.warning("知识库已禁用，无法清空")
            return False
        
        self.vector_store.clear()
        logger.info("知识库已清空")
        return True
    
    def enable(self):
        """启用知识库"""
        self.enabled = True
        logger.info("知识库已启用")
    
    def disable(self):
        """禁用知识库"""
        self.enabled = False
        logger.info("知识库已禁用")
    
    def is_enabled(self) -> bool:
        """检查知识库是否启用
        
        Returns:
            bool: 启用返回True，否则返回False
        """
        return self.enabled
    
    def get_allowed_agents(self) -> Set[str]:
        """获取允许访问知识库的智能体ID集合
        
        Returns:
            Set[str]: 智能体ID集合
        """
        return self.allowed_agents.copy()
