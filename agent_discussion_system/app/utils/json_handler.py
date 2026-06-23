#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON文件处理工具

该模块提供了JSON文件的读写功能，用于配置管理和数据存储。
"""

import json
import os
from .logger import get_logger

logger = get_logger()


def save_json(file_path: str, data: dict, ensure_ascii: bool = False) -> bool:
    """保存数据到JSON文件
    
    Args:
        file_path (str): JSON文件路径
        data (dict): 要保存的数据
        ensure_ascii (bool): 是否确保ASCII编码，默认为False（支持中文）
    
    Returns:
        bool: 保存成功返回True，失败返回False
    """
    try:
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        # 写入JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=ensure_ascii)
        
        logger.debug(f"数据成功保存到文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败: {file_path}, 错误: {str(e)}")
        return False


def load_json(file_path: str) -> dict:
    """从JSON文件加载数据
    
    Args:
        file_path (str): JSON文件路径
    
    Returns:
        dict: 加载的数据，如果文件不存在或加载失败返回空字典
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"JSON文件不存在: {file_path}")
            return {}
        
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.debug(f"成功从文件加载数据: {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON文件格式错误: {file_path}, 错误: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"加载JSON文件失败: {file_path}, 错误: {str(e)}")
        return {}
