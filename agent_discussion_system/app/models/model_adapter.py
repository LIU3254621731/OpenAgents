#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型适配器基类

该模块定义了统一的模型接口，所有模型适配器都必须实现这个接口，
确保不同类型的模型（如OpenAI API、本地模型）可以无缝切换。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.utils.logger import get_logger

logger = get_logger()


class ModelAdapter(ABC):
    """模型适配器抽象基类
    
    定义了所有模型适配器都必须实现的接口，包括：
    - generate: 生成文本
    - get_model_info: 获取模型信息
    - list_models: 列出可用模型
    """
    
    @abstractmethod
    def generate(self, prompt: str, model_id: str = None, **kwargs) -> str:
        """生成文本
        
        Args:
            prompt (str): 提示词
            model_id (str, optional): 模型ID，默认为None（使用默认模型）
            **kwargs: 其他参数，如temperature、max_tokens等
        
        Returns:
            str: 生成的文本
        """
        pass
    
    @abstractmethod
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """获取模型信息
        
        Args:
            model_id (str): 模型ID
        
        Returns:
            Dict[str, Any]: 模型信息，包含name、description、max_tokens等
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """列出可用模型
        
        Returns:
            List[Dict[str, Any]]: 可用模型列表，每个模型包含id、name、description等信息
        """
        pass
    
    def set_default_model(self, model_id: str):
        """设置默认模型
        
        Args:
            model_id (str): 模型ID
        """
        self._default_model = model_id
        logger.info(f"默认模型已设置为: {model_id}")
    
    def get_default_model(self) -> str:
        """获取默认模型
        
        Returns:
            str: 默认模型ID
        """
        return getattr(self, "_default_model", None)
