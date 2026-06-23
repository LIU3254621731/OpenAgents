#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI模型适配器

该模块实现了ModelAdapter接口，用于接入OpenAI API和兼容OpenAI API的其他模型服务。
使用httpx库进行网络请求，支持流式输出和错误处理。
"""

import httpx
from typing import Dict, Any, List, Optional
from app.models.model_adapter import ModelAdapter
from app.utils.logger import get_logger

logger = get_logger()


class OpenAIModel(ModelAdapter):
    """OpenAI模型适配器
    
    实现了ModelAdapter接口，用于接入OpenAI API和兼容OpenAI API的其他模型服务。
    支持多种OpenAI模型，如gpt-4o-mini、gpt-4o、gpt-3.5-turbo等。
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", timeout: int = 30):
        """初始化OpenAI模型适配器
        
        Args:
            api_key (str): OpenAI API密钥
            base_url (str, optional): API基础URL，默认为"https://api.openai.com/v1"
            timeout (int, optional): 请求超时时间，默认为30秒
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._default_model = "gpt-4o-mini"
        
        # 可用模型列表（简化版，实际可通过API获取）
        self._available_models = [
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o mini",
                "description": "OpenAI的小型多模态模型，价格便宜，速度快",
                "max_tokens": 16384
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "description": "OpenAI的最新多模态模型，功能强大，支持图像和音频",
                "max_tokens": 128000
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "OpenAI的快速语言模型，适合大多数文本生成任务",
                "max_tokens": 16384
            }
        ]
        
        # 创建HTTP客户端
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )
    
    def generate(self, prompt: str, model_id: str = None, **kwargs) -> str:
        """生成文本
        
        Args:
            prompt (str): 提示词
            model_id (str, optional): 模型ID，默认为None（使用默认模型）
            **kwargs: 其他参数，如temperature、max_tokens等
        
        Returns:
            str: 生成的文本
        """
        if not prompt:
            logger.warning("提示词为空，无法生成文本")
            return ""
        
        # 使用默认模型如果没有指定
        model_id = model_id or self._default_model
        
        # 准备请求参数
        request_data = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "stream": False
        }
        
        try:
            logger.debug(f"调用OpenAI API，模型: {model_id}")
            
            # 发送请求
            response = self._client.post("/chat/completions", json=request_data)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"].strip()
            
            logger.debug(f"OpenAI API调用成功，生成文本长度: {len(generated_text)}")
            return generated_text
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API调用失败，HTTP错误: {e.response.status_code} - {e.response.text}")
            return ""
        except httpx.RequestError as e:
            logger.error(f"OpenAI API调用失败，请求错误: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"OpenAI API调用失败，未知错误: {str(e)}")
            return ""
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """获取模型信息
        
        Args:
            model_id (str): 模型ID
        
        Returns:
            Dict[str, Any]: 模型信息，包含name、description、max_tokens等
        """
        for model in self._available_models:
            if model["id"] == model_id:
                return model.copy()
        
        logger.warning(f"模型 {model_id} 不存在")
        return {
            "id": model_id,
            "name": model_id,
            "description": "未知模型",
            "max_tokens": 4096
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """列出可用模型
        
        Returns:
            List[Dict[str, Any]]: 可用模型列表
        """
        # 简化实现，实际可通过API获取
        return self._available_models.copy()
    
    def update_api_key(self, api_key: str):
        """更新API密钥
        
        Args:
            api_key (str): 新的API密钥
        """
        self.api_key = api_key
        # 更新HTTP客户端的授权头
        self._client.headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })
        logger.info("OpenAI API密钥已更新")
    
    def update_base_url(self, base_url: str):
        """更新API基础URL
        
        Args:
            base_url (str): 新的API基础URL
        """
        self.base_url = base_url
        # 更新HTTP客户端的基础URL
        self._client.base_url = httpx.URL(self.base_url)
        logger.info(f"OpenAI API基础URL已更新为: {self.base_url}")
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, "_client"):
            self._client.close()
            logger.info("OpenAI模型适配器HTTP客户端已关闭")
