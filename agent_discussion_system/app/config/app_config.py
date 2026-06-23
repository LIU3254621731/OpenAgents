#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理

该模块负责应用程序的配置管理，包括加载和保存配置文件、管理API Key等。
配置文件使用JSON格式，存储在用户本地目录中。
"""

import os
from typing import Dict, Optional
from app.utils.json_handler import save_json, load_json
from app.utils.encryption import encrypt_api_key, decrypt_api_key
from app.utils.logger import get_logger

logger = get_logger()


class AppConfig:
    """应用配置管理类
    
    负责管理应用程序的配置，包括：
    - 加载和保存配置文件
    - 管理API Key
    - 提供配置访问接口
    
    单例模式实现，确保整个应用只有一个配置实例。
    """
    
    def __init__(self):
        """初始化配置管理类"""
        # 配置文件路径
        self.config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config"
        )
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # 默认配置
        self._default_config = {
            "app": {
                "version": "0.1.0",
                "language": "zh-CN",
                "theme": "light"
            },
            "model": {
                "default_model": "gpt-4o-mini",
                "api_base_url": "https://api.openai.com/v1",
                "api_key": "",
                "timeout": 30
            },
            "discussion": {
                "max_rounds": 10,
                "max_time_per_round": 60,
                "max_total_time": 300
            },
            "knowledge_base": {
                "enabled": True,
                "vector_store_path": os.path.join(self.config_dir, "vector_store")
            },
            "mcp": {
                "enabled": True,
                "timeout": 10
            }
        }
        
        # 配置数据
        self._config = self._default_config.copy()
    
    def load(self):
        """加载配置文件"""
        try:
            # 从文件加载配置
            loaded_config = load_json(self.config_file)
            
            if loaded_config:
                # 合并配置，保留默认值
                self._merge_config(self._config, loaded_config)
                logger.info("配置文件加载成功")
            else:
                # 使用默认配置
                logger.info("配置文件不存在，使用默认配置")
                self.save()  # 保存默认配置到文件
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            self._config = self._default_config.copy()
    
    def save(self):
        """保存配置文件"""
        try:
            # 加密API Key后保存
            config_to_save = self._config.copy()
            if config_to_save["model"]["api_key"]:
                config_to_save["model"]["api_key"] = encrypt_api_key(
                    config_to_save["model"]["api_key"]
                )
            
            if save_json(self.config_file, config_to_save):
                logger.info("配置文件保存成功")
                return True
            return False
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def get(self, key_path: str, default=None):
        """获取配置值
        
        Args:
            key_path (str): 配置键路径，使用点分隔，如 "app.version"
            default: 默认值，当配置不存在时返回
            
        Returns:
            配置值或默认值
        """
        keys = key_path.split(".")
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            
            # 如果是API Key，解密后返回
            if key_path == "model.api_key" and value:
                return decrypt_api_key(value)
            
            return value
        except KeyError:
            logger.warning(f"配置键不存在: {key_path}")
            return default
        except Exception as e:
            logger.error(f"获取配置值失败: {key_path}, 错误: {str(e)}")
            return default
    
    def set(self, key_path: str, value):
        """设置配置值
        
        Args:
            key_path (str): 配置键路径，使用点分隔，如 "app.version"
            value: 配置值
        """
        keys = key_path.split(".")
        config = self._config
        
        try:
            # 遍历到最后一个键的父级
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 设置值
            config[keys[-1]] = value
            logger.debug(f"配置值设置成功: {key_path} = {value}")
            return True
        except Exception as e:
            logger.error(f"设置配置值失败: {key_path}, 错误: {str(e)}")
            return False
    
    def reset(self):
        """重置配置为默认值"""
        self._config = self._default_config.copy()
        logger.info("配置已重置为默认值")
        self.save()
    
    @staticmethod
    def _merge_config(dest: dict, src: dict):
        """合并配置，保留默认值
        
        Args:
            dest (dict): 目标配置（默认配置）
            src (dict): 源配置（加载的配置）
        """
        for key, value in src.items():
            if key in dest and isinstance(dest[key], dict) and isinstance(value, dict):
                # 递归合并字典
                AppConfig._merge_config(dest[key], value)
            else:
                # 直接替换值
                dest[key] = value
    
    def get_model_config(self) -> Dict:
        """获取模型配置
        
        Returns:
            Dict: 模型配置
        """
        model_config = self._config["model"].copy()
        if model_config["api_key"]:
            model_config["api_key"] = decrypt_api_key(model_config["api_key"])
        return model_config
    
    def get_discussion_config(self) -> Dict:
        """获取讨论配置
        
        Returns:
            Dict: 讨论配置
        """
        return self._config["discussion"].copy()
    
    def get_knowledge_base_config(self) -> Dict:
        """获取知识库配置
        
        Returns:
            Dict: 知识库配置
        """
        return self._config["knowledge_base"].copy()
    
    def get_mcp_config(self) -> Dict:
        """获取MCP配置
        
        Returns:
            Dict: MCP配置
        """
        return self._config["mcp"].copy()
