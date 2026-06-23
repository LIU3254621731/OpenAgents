#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地模型适配器

该模块实现了ModelAdapter接口，用于接入本地运行的模型，
例如通过HTTP API调用本地的Ollama或llama.cpp服务。
"""

import httpx
from typing import Dict, Any, List
from app.models.model_adapter import ModelAdapter
from app.utils.logger import get_logger

logger = get_logger()


class LocalModel(ModelAdapter):
    """本地模型适配器
    
    实现了ModelAdapter接口，用于接入本地运行的模型服务，
    支持通过HTTP API调用本地的Ollama、llama.cpp等模型服务。
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30):
        """初始化本地模型适配器
        
        Args:
            base_url (str, optional): 本地模型服务的基础URL，默认为"http://localhost:11434"（Ollama默认地址）
            timeout (int, optional): 请求超时时间，默认为30秒
        """
        self.base_url = base_url
        self.timeout = timeout
        self._default_model = "llama3"
        
        # 可用模型列表（简化版，实际可通过API获取）
        self._available_models = [
            {
                "id": "llama3",
                "name": "Llama 3",
                "description": "Meta的Llama 3模型，适合通用文本生成任务",
                "max_tokens": 8192
            },
            {
                "id": "mistral",
                "name": "Mistral",
                "description": "Mistral AI的开源模型，速度快，质量高",
                "max_tokens": 8192
            },
            {
                "id": "gemma",
                "name": "Gemma",
                "description": "Google的开源模型，适合多种文本任务",
                "max_tokens": 8192
            }
        ]
        
        # 创建HTTP客户端
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
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
        
        try:
            logger.debug(f"调用本地模型服务，模型: {model_id}")
            
            # 尝试调用Ollama API
            try:
                # Ollama API格式
                request_data = {
                    "model": model_id,
                    "prompt": prompt,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 1024),
                    "stream": False
                }
                
                response = self._client.post("/api/generate", json=request_data)
                response.raise_for_status()
                
                # 解析Ollama响应
                result = response.json()
                generated_text = result["response"].strip()
                
                logger.debug(f"本地模型服务调用成功（Ollama API），生成文本长度: {len(generated_text)}")
                return generated_text
                
            except Exception as e:
                logger.debug(f"Ollama API调用失败，尝试使用OpenAI兼容API格式: {str(e)}")
                
                # 尝试调用OpenAI兼容API
                request_data = {
                    "model": model_id,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 1024),
                    "stream": False
                }
                
                response = self._client.post("/v1/chat/completions", json=request_data)
                response.raise_for_status()
                
                # 解析OpenAI兼容响应
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"].strip()
                
                logger.debug(f"本地模型服务调用成功（OpenAI兼容API），生成文本长度: {len(generated_text)}")
                return generated_text
                
        except httpx.HTTPStatusError as e:
            logger.error(f"本地模型服务调用失败，HTTP错误: {e.response.status_code} - {e.response.text}")
            return ""
        except httpx.RequestError as e:
            logger.error(f"本地模型服务调用失败，请求错误: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"本地模型服务调用失败，未知错误: {str(e)}")
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
            "description": "未知本地模型",
            "max_tokens": 4096
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """列出可用模型
        
        Returns:
            List[Dict[str, Any]]: 可用模型列表
        """
        try:
            # 尝试从API获取模型列表
            response = self._client.get("/api/tags")
            response.raise_for_status()
            
            result = response.json()
            api_models = []
            
            if "models" in result:
                for model in result["models"]:
                    api_models.append({
                        "id": model["name"],
                        "name": model["name"],
                        "description": f"本地模型: {model['name']}",
                        "max_tokens": 8192
                    })
                
            logger.debug(f"从API获取到 {len(api_models)} 个本地模型")
            return api_models
            
        except Exception as e:
            logger.debug(f"获取本地模型列表失败，使用默认列表: {str(e)}")
            return self._available_models.copy()
    
    def update_base_url(self, base_url: str):
        """更新模型服务基础URL
        
        Args:
            base_url (str): 新的模型服务基础URL
        """
        self.base_url = base_url
        # 更新HTTP客户端的基础URL
        self._client.base_url = httpx.URL(self.base_url)
        logger.info(f"本地模型服务基础URL已更新为: {self.base_url}")
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, "_client"):
            self._client.close()
            logger.info("本地模型适配器HTTP客户端已关闭")
