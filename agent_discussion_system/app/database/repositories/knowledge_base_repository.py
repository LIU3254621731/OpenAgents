#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库数据访问层

负责知识库相关的数据库操作，包括文档管理和向量索引管理等功能。
"""

import json
from typing import List, Dict, Optional

from app.database import db_manager
from app.utils.logger import get_logger

logger = get_logger()


class KnowledgeBaseRepository:
    """知识库数据访问类
    
    负责知识库相关的数据库操作，包括：
    - 添加文档到知识库
    - 获取知识库中的文档
    - 根据ID获取文档
    - 删除文档
    - 清空知识库
    - 添加向量索引
    - 获取向量索引
    """
    
    def __init__(self):
        """初始化知识库数据访问层
        
        使用全局数据库管理器实例。
        """
        self.db = db_manager
    
    def add_document(self, filename: str, content: str, file_type: str) -> str:
        """添加文档到知识库
        
        Args:
            filename: 文件名
            content: 文档内容
            file_type: 文件类型（如txt、md、pdf等）
        
        Returns:
            str: 创建的文档ID
        """
        try:
            import uuid
            doc_id = f"doc_{uuid.uuid4().hex[:12]}"
            
            query = """
            INSERT INTO knowledge_base (doc_id, filename, content, file_type)
            VALUES (?, ?, ?, ?)
            """
            
            self.db.execute(
                query, 
                (doc_id, filename, content, file_type)
            )
            
            self.db.commit()
            logger.info(f"文档添加成功：{filename} (ID: {doc_id})")
            return doc_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加文档失败：{e}")
            raise
    
    def get_all_documents(self) -> List[Dict[str, any]]:
        """获取知识库中的所有文档
        
        Returns:
            List[Dict[str, any]]: 文档列表，每个文档包含完整信息
        """
        try:
            query = """SELECT * FROM knowledge_base ORDER BY created_at"""
            documents = self.db.fetch_all(query)
            
            logger.debug(f"获取所有文档成功，共 {len(documents)} 个")
            return documents
            
        except Exception as e:
            logger.error(f"获取所有文档失败：{e}")
            raise
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, any]]:
        """根据ID获取文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            Optional[Dict[str, any]]: 文档信息，不存在则返回None
        """
        try:
            query = """SELECT * FROM knowledge_base WHERE doc_id = ?"""
            document = self.db.fetch_one(query, (doc_id,))
            
            if document:
                logger.debug(f"根据ID {doc_id} 获取文档成功")
            else:
                logger.debug(f"未找到ID为 {doc_id} 的文档")
            
            return document
            
        except Exception as e:
            logger.error(f"根据ID获取文档失败：{e}")
            raise
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 检查文档是否存在
            existing_doc = self.get_document_by_id(doc_id)
            if not existing_doc:
                logger.warning(f"删除文档失败：未找到ID为 {doc_id} 的文档")
                return False
            
            query = """DELETE FROM knowledge_base WHERE doc_id = ?"""
            self.db.execute(query, (doc_id,))
            self.db.commit()
            
            logger.info(f"文档删除成功：{doc_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除文档失败：{e}")
            raise
    
    def clear_knowledge_base(self) -> bool:
        """清空知识库
        
        删除所有文档和对应的向量索引。
        
        Returns:
            bool: 清空成功返回True，否则返回False
        """
        try:
            # 先删除向量索引
            vector_query = """DELETE FROM kb_vectors"""
            self.db.execute(vector_query)
            
            # 再删除文档
            doc_query = """DELETE FROM knowledge_base"""
            self.db.execute(doc_query)
            
            self.db.commit()
            logger.info("知识库已清空")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"清空知识库失败：{e}")
            raise
    
    def get_document_count(self) -> int:
        """获取知识库中文档数量
        
        Returns:
            int: 文档数量
        """
        try:
            query = """SELECT COUNT(*) as count FROM knowledge_base"""
            result = self.db.fetch_one(query)
            count = result['count'] if result else 0
            logger.debug(f"获取文档数量成功：{count}")
            return count
            
        except Exception as e:
            logger.error(f"获取文档数量失败：{e}")
            raise
    
    def add_vector(self, doc_id: str, vector: List[float]) -> str:
        """添加向量索引
        
        Args:
            doc_id: 文档ID
            vector: 向量数据
        
        Returns:
            str: 创建的向量ID
        """
        try:
            import uuid
            vector_id = f"vector_{uuid.uuid4().hex[:12]}"
            
            # 序列化向量为JSON字符串
            vector_json = json.dumps(vector)
            
            query = """
            INSERT INTO kb_vectors (vector_id, doc_id, vector)
            VALUES (?, ?, ?)
            """
            
            self.db.execute(
                query, 
                (vector_id, doc_id, vector_json)
            )
            
            self.db.commit()
            logger.debug(f"向量索引添加成功：{doc_id}")
            return vector_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加向量索引失败：{e}")
            raise
    
    def get_vectors_by_doc_id(self, doc_id: str) -> List[Dict[str, any]]:
        """根据文档ID获取向量索引
        
        Args:
            doc_id: 文档ID
        
        Returns:
            List[Dict[str, any]]: 向量索引列表
        """
        try:
            query = """SELECT * FROM kb_vectors WHERE doc_id = ?"""
            vectors = self.db.fetch_all(query, (doc_id,))
            
            # 解析JSON字段
            for vector in vectors:
                vector['vector'] = json.loads(vector['vector'])
            
            logger.debug(f"获取文档向量成功：{doc_id}，共 {len(vectors)} 个")
            return vectors
            
        except Exception as e:
            logger.error(f"获取向量索引失败：{e}")
            raise
    
    def get_all_vectors(self) -> List[Dict[str, any]]:
        """获取所有向量索引
        
        Returns:
            List[Dict[str, any]]: 向量索引列表
        """
        try:
            query = """SELECT * FROM kb_vectors"""
            vectors = self.db.fetch_all(query)
            
            # 解析JSON字段
            for vector in vectors:
                vector['vector'] = json.loads(vector['vector'])
            
            logger.debug(f"获取所有向量索引成功，共 {len(vectors)} 个")
            return vectors
            
        except Exception as e:
            logger.error(f"获取所有向量索引失败：{e}")
            raise
    
    def delete_vectors_by_doc_id(self, doc_id: str) -> bool:
        """根据文档ID删除向量索引
        
        Args:
            doc_id: 文档ID
        
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        try:
            query = """DELETE FROM kb_vectors WHERE doc_id = ?"""
            self.db.execute(query, (doc_id,))
            self.db.commit()
            
            logger.debug(f"文档向量已删除：{doc_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除向量索引失败：{e}")
            raise
    
    def get_vector_count(self) -> int:
        """获取向量索引数量
        
        Returns:
            int: 向量索引数量
        """
        try:
            query = """SELECT COUNT(*) as count FROM kb_vectors"""
            result = self.db.fetch_one(query)
            count = result['count'] if result else 0
            logger.debug(f"获取向量索引数量成功：{count}")
            return count
            
        except Exception as e:
            logger.error(f"获取向量索引数量失败：{e}")
            raise
