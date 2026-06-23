#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件读取MCP工具

该模块实现了文件读取MCP工具，用于读取本地文件内容。
这是一个中等风险的工具，需要严格的安全控制，包括：
- 文件路径验证
- 读取权限检查
- 文件大小限制
- 异常捕获
"""

import os
from typing import Dict, Any
from app.mcp.mcp_base import MCPBase, MCPPermissionLevel
from app.utils.logger import get_logger

logger = get_logger()


class FileMCP(MCPBase):
    """文件读取MCP工具
    
    用于安全读取本地文件内容，支持以下功能：
    - 读取文本文件
    - 文件路径验证
    - 文件大小限制
    - 支持指定编码
    
    权限级别：MEDIUM
    """
    
    def __init__(self):
        """初始化文件读取MCP工具"""
        super().__init__(
            name="file_reader",
            description="读取本地文件内容",
            permission_level=MCPPermissionLevel.MEDIUM
        )
        
        self.max_file_size = 1024 * 1024  # 最大文件大小，默认为1MB
        self.allowed_extensions = [".txt", ".md", ".json", ".csv", ".py", ".yaml", ".yml"]  # 允许读取的文件扩展名
        self.allowed_directories = []  # 允许读取的目录列表，为空表示所有目录
    
    def execute(self, file_path: str, encoding: str = "utf-8", **kwargs) -> Dict[str, Any]:
        """执行文件读取
        
        Args:
            file_path (str): 文件路径
            encoding (str, optional): 文件编码，默认为utf-8
            **kwargs: 其他参数
        
        Returns:
            Dict[str, Any]: 执行结果，包含status、result和message字段
        """
        # 验证文件路径
        if not file_path:
            return {
                "status": "error",
                "result": None,
                "message": "文件路径不能为空"
            }
        
        # 规范化文件路径
        file_path = os.path.abspath(file_path)
        
        # 检查文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        if self.allowed_extensions and file_ext not in self.allowed_extensions:
            return {
                "status": "error",
                "result": None,
                "message": f"不允许读取 {file_ext} 类型的文件"
            }
        
        # 检查文件所在目录
        if self.allowed_directories:
            file_dir = os.path.dirname(file_path)
            is_allowed = False
            for allowed_dir in self.allowed_directories:
                if file_dir.startswith(os.path.abspath(allowed_dir)):
                    is_allowed = True
                    break
            
            if not is_allowed:
                return {
                    "status": "error",
                    "result": None,
                    "message": f"不允许读取 {file_dir} 目录下的文件"
                }
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "result": None,
                "message": f"文件不存在: {file_path}"
            }
        
        # 检查是否为文件
        if not os.path.isfile(file_path):
            return {
                "status": "error",
                "result": None,
                "message": f"路径不是文件: {file_path}"
            }
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            return {
                "status": "error",
                "result": None,
                "message": f"文件大小超过限制 ({file_size} > {self.max_file_size} bytes)"
            }
        
        # 读取文件内容
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            
            return {
                "status": "success",
                "result": {
                    "file_path": file_path,
                    "file_size": file_size,
                    "encoding": encoding,
                    "content": content
                },
                "message": f"文件读取成功: {file_path}"
            }
        except UnicodeDecodeError:
            return {
                "status": "error",
                "result": None,
                "message": f"文件编码错误，尝试使用其他编码: {encoding}"
            }
        except PermissionError:
            return {
                "status": "error",
                "result": None,
                "message": f"没有权限读取文件: {file_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "result": None,
                "message": f"读取文件失败: {str(e)}"
            }
    
    def set_max_file_size(self, max_size: int):
        """设置最大文件大小
        
        Args:
            max_size (int): 最大文件大小，单位字节
        """
        self.max_file_size = max(1, max_size)
        logger.debug(f"文件读取工具最大文件大小已设置为 {self.max_file_size} 字节")
    
    def set_allowed_extensions(self, extensions: list):
        """设置允许读取的文件扩展名
        
        Args:
            extensions (list): 文件扩展名列表，如[".txt", ".md"]
        """
        self.allowed_extensions = [ext.lower() for ext in extensions]
        logger.debug(f"文件读取工具允许的文件扩展名已设置为: {self.allowed_extensions}")
    
    def set_allowed_directories(self, directories: list):
        """设置允许读取的目录列表
        
        Args:
            directories (list): 目录列表
        """
        self.allowed_directories = [os.path.abspath(dir_path) for dir_path in directories]
        logger.debug(f"文件读取工具允许的目录已设置为: {self.allowed_directories}")
