#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志记录工具

该模块负责应用程序的日志记录，支持不同级别的日志输出和文件记录。
"""

import logging
import os
from logging.handlers import RotatingFileHandler


class Logger:
    """日志记录器类
    
    单例模式实现，确保整个应用只有一个日志记录器实例。
    支持控制台输出和文件记录，日志级别可配置。
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志记录器"""
        # 创建日志记录器
        self.logger = logging.getLogger("agent_discussion_system")
        self.logger.setLevel(logging.DEBUG)
        
        # 确保日志目录存在
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建文件处理器，日志文件大小限制为10MB，最多保留5个备份
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 定义日志格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """获取日志记录器实例"""
        return self.logger


def get_logger():
    """获取日志记录器的便捷函数
    
    Returns:
        logging.Logger: 日志记录器实例
    """
    return Logger().get_logger()
