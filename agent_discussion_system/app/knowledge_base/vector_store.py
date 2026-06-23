#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量索引实现

该模块实现了简化版的向量索引，用于存储和检索文本向量。
在Beta版本中，我们使用简单的基于相似度的检索算法，
不依赖外部向量数据库，方便部署和测试。
"""

import os
import json
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.utils.logger import get_logger

logger = get_logger()


class VectorStore:
    """向量索引类
    
    实现了简化版的向量索引，支持以下功能：
    - 添加文本到索引
    - 检索相似文本
    - 保存和加载索引
    - 清空索引
    
    使用TF-IDF算法将文本转换为向量，使用余弦相似度进行检索。
    """
    
    def __init__(self, store_path: str = None):
        """初始化向量索引
        
        Args:
            store_path (str, optional): 索引存储路径，默认为None
        """
        self.store_path = store_path
        self.documents = []  # 存储文档列表
        self.vectorizer = TfidfVectorizer()  # TF-IDF向量化器
        self.tfidf_matrix = None  # TF-IDF矩阵
        
        # 如果指定了存储路径，尝试加载索引
        if self.store_path:
            self.load()
        
        logger.info("向量索引初始化完成")
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """添加文档到索引
        
        Args:
            content (str): 文档内容
            metadata (Dict[str, Any], optional): 文档元数据，默认为None
        
        Returns:
            int: 文档ID
        """
        # 创建文档对象
        document = {
            "id": len(self.documents),
            "content": content,
            "metadata": metadata or {}
        }
        
        # 添加到文档列表
        self.documents.append(document)
        
        # 重新计算TF-IDF矩阵
        self._recompute_tfidf()
        
        # 保存索引
        if self.store_path:
            self.save()
        
        logger.debug(f"文档已添加到向量索引，ID: {document['id']}")
        return document["id"]
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[int]:
        """批量添加文档到索引
        
        Args:
            documents (List[Dict[str, Any]]): 文档列表，每个文档包含content和可选的metadata字段
        
        Returns:
            List[int]: 文档ID列表
        """
        doc_ids = []
        for doc in documents:
            if "content" in doc:
                doc_id = self.add_document(doc["content"], doc.get("metadata"))
                doc_ids.append(doc_id)
        return doc_ids
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """检索相似文档
        
        Args:
            query (str): 检索查询
            k (int, optional): 返回的文档数量，默认为5
        
        Returns:
            List[Dict[str, Any]]: 相似文档列表，按相似度降序排列
        """
        if not query:
            return []
        
        if len(self.documents) == 0:
            return []
        
        # 将查询转换为向量
        query_vector = self.vectorizer.transform([query])
        
        # 计算余弦相似度
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # 获取相似度最高的k个文档
        top_indices = similarities.argsort()[-k:][::-1]
        
        # 构建结果列表
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                document = self.documents[idx].copy()
                document["similarity"] = similarities[idx]
                results.append(document)
        
        return results
    
    def _recompute_tfidf(self):
        """重新计算TF-IDF矩阵"""
        if len(self.documents) == 0:
            self.tfidf_matrix = None
            return
        
        # 提取所有文档内容
        contents = [doc["content"] for doc in self.documents]
        
        # 重新拟合向量化器并生成TF-IDF矩阵
        self.tfidf_matrix = self.vectorizer.fit_transform(contents)
    
    def save(self):
        """保存索引到文件"""
        if not self.store_path:
            logger.warning("未指定存储路径，无法保存索引")
            return False
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            
            # 保存文档和向量器参数
            data = {
                "documents": self.documents,
                "vectorizer_params": {
                    "vocabulary": self.vectorizer.vocabulary_ if hasattr(self.vectorizer, "vocabulary_") else {},
                    "idf": self.vectorizer.idf_.tolist() if hasattr(self.vectorizer, "idf_") else []
                }
            }
            
            # 保存到JSON文件
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"向量索引已保存到: {self.store_path}")
            return True
        except Exception as e:
            logger.error(f"保存向量索引失败: {str(e)}")
            return False
    
    def load(self):
        """从文件加载索引"""
        if not self.store_path or not os.path.exists(self.store_path):
            logger.warning(f"索引文件不存在: {self.store_path}")
            return False
        
        try:
            # 从JSON文件加载数据
            with open(self.store_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 加载文档
            self.documents = data.get("documents", [])
            
            # 加载向量器参数
            vectorizer_params = data.get("vectorizer_params", {})
            if vectorizer_params and vectorizer_params["vocabulary"]:
                # 重新创建向量化器
                self.vectorizer = TfidfVectorizer(vocabulary=vectorizer_params["vocabulary"])
                self.vectorizer.idf_ = np.array(vectorizer_params["idf"])
                
                # 重新生成TF-IDF矩阵
                if self.documents:
                    contents = [doc["content"] for doc in self.documents]
                    self.tfidf_matrix = self.vectorizer.transform(contents)
            else:
                # 重新计算TF-IDF
                self._recompute_tfidf()
            
            logger.info(f"向量索引已从 {self.store_path} 加载，包含 {len(self.documents)} 个文档")
            return True
        except Exception as e:
            logger.error(f"加载向量索引失败: {str(e)}")
            return False
    
    def clear(self):
        """清空索引"""
        self.documents.clear()
        self.tfidf_matrix = None
        self.vectorizer = TfidfVectorizer()
        
        # 保存清空后的索引
        if self.store_path:
            self.save()
        
        logger.info("向量索引已清空")
    
    def get_document(self, doc_id: int) -> Dict[str, Any]:
        """获取文档
        
        Args:
            doc_id (int): 文档ID
        
        Returns:
            Dict[str, Any]: 文档对象，如果不存在返回None
        """
        if 0 <= doc_id < len(self.documents):
            return self.documents[doc_id]
        else:
            logger.warning(f"文档不存在，ID: {doc_id}")
            return None
    
    def delete_document(self, doc_id: int) -> bool:
        """删除文档
        
        Args:
            doc_id (int): 文档ID
        
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        if 0 <= doc_id < len(self.documents):
            del self.documents[doc_id]
            
            # 更新剩余文档的ID
            for i, doc in enumerate(self.documents):
                doc["id"] = i
            
            # 重新计算TF-IDF矩阵
            self._recompute_tfidf()
            
            # 保存索引
            if self.store_path:
                self.save()
            
            logger.info(f"文档已删除，ID: {doc_id}")
            return True
        else:
            logger.warning(f"删除失败：文档不存在，ID: {doc_id}")
            return False
    
    def get_document_count(self) -> int:
        """获取文档数量
        
        Returns:
            int: 文档数量
        """
        return len(self.documents)
