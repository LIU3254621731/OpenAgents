#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块

负责SQLite数据库的连接管理、初始化和基本操作。
"""

import os
import sqlite3
import logging
from typing import Any, List, Dict, Optional

from app.utils.logger import get_logger

logger = get_logger()


class DatabaseManager:
    """数据库连接管理类
    
    单例模式设计，确保全局唯一数据库连接实例。
    负责数据库的连接、初始化、查询、更新和事务管理。
    """
    
    _instance = None
    _db_path = None
    _conn = None
    _cursor = None
    _initialized = False
    
    def __new__(cls, db_path: str = None):
        """创建单例实例
        
        Args:
            db_path: 数据库文件路径，默认为当前目录下的agent_discussion.db
        """
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        if db_path is not None:
            cls._db_path = db_path
        return cls._instance
    
    def __init__(self, db_path: str = None):
        """初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，默认为当前目录下的agent_discussion.db
        """
        if not self._initialized:
            if db_path is None:
                # 默认数据库路径：用户应用数据目录
                app_data_dir = os.path.join(os.path.expanduser("~"), ".agent_discussion_system")
                os.makedirs(app_data_dir, exist_ok=True)
                self._db_path = os.path.join(app_data_dir, "agent_discussion.db")
            else:
                self._db_path = db_path
            
            self._initialized = True
            logger.info(f"数据库管理器初始化完成，数据库路径：{self._db_path}")
    
    def connect(self):
        """建立数据库连接
        
        建立SQLite数据库连接，并执行初始化脚本（如果数据库不存在）。
        """
        try:
            # 检查数据库文件是否存在
            db_exists = os.path.exists(self._db_path)
            
            # 建立连接
            self._conn = sqlite3.connect(
                self._db_path,
                check_same_thread=False,  # 允许跨线程访问
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            
            # 设置行工厂，返回字典格式
            self._conn.row_factory = sqlite3.Row
            
            # 创建游标
            self._cursor = self._conn.cursor()
            
            logger.info(f"成功连接到数据库：{self._db_path}")
            
            # 如果数据库不存在，执行初始化脚本
            if not db_exists:
                self._initialize_database()
                logger.info("数据库初始化完成")
            
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败：{e}")
            raise
    
    def _initialize_database(self):
        """初始化数据库
        
        执行初始化SQL脚本，创建表结构和插入默认数据。
        """
        try:
            # 读取初始化脚本
            migration_dir = os.path.join(os.path.dirname(__file__), "migrations")
            initial_script_path = os.path.join(migration_dir, "001_initial.sql")
            
            with open(initial_script_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            
            # 执行脚本
            self._cursor.executescript(sql_script)
            self._conn.commit()
            logger.info("数据库初始化脚本执行成功")
            
        except Exception as e:
            logger.error(f"数据库初始化失败：{e}")
            self._conn.rollback()
            raise
    
    def disconnect(self):
        """关闭数据库连接
        
        关闭游标和连接，释放资源。
        """
        try:
            if self._cursor:
                self._cursor.close()
                self._cursor = None
            
            if self._conn:
                self._conn.close()
                self._conn = None
            
            logger.info("数据库连接已关闭")
            
        except sqlite3.Error as e:
            logger.error(f"关闭数据库连接失败：{e}")
    
    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """执行SQL语句
        
        Args:
            query: SQL查询语句
            params: 查询参数，默认为None
        
        Returns:
            sqlite3.Cursor: 游标对象，包含查询结果
        """
        try:
            if params:
                result = self._cursor.execute(query, params)
            else:
                result = self._cursor.execute(query)
            return result
        except sqlite3.Error as e:
            logger.error(f"执行SQL失败：{query}, params: {params}, error: {e}")
            raise
    
    def executemany(self, query: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """批量执行SQL语句
        
        Args:
            query: SQL查询语句
            params_list: 查询参数列表
        
        Returns:
            sqlite3.Cursor: 游标对象，包含查询结果
        """
        try:
            result = self._cursor.executemany(query, params_list)
            return result
        except sqlite3.Error as e:
            logger.error(f"批量执行SQL失败：{query}, error: {e}")
            raise
    
    def commit(self):
        """提交事务
        
        将当前事务的修改提交到数据库。
        """
        try:
            self._conn.commit()
            logger.debug("事务提交成功")
        except sqlite3.Error as e:
            logger.error(f"事务提交失败：{e}")
            raise
    
    def rollback(self):
        """回滚事务
        
        撤销当前事务的所有修改。
        """
        try:
            self._conn.rollback()
            logger.debug("事务回滚成功")
        except sqlite3.Error as e:
            logger.error(f"事务回滚失败：{e}")
            raise
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """获取单条查询结果
        
        Args:
            query: SQL查询语句
            params: 查询参数，默认为None
        
        Returns:
            Optional[Dict[str, Any]]: 查询结果字典，没有结果则返回None
        """
        self.execute(query, params)
        row = self._cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """获取所有查询结果
        
        Args:
            query: SQL查询语句
            params: 查询参数，默认为None
        
        Returns:
            List[Dict[str, Any]]: 查询结果字典列表
        """
        self.execute(query, params)
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_cursor(self) -> sqlite3.Cursor:
        """获取游标对象
        
        Returns:
            sqlite3.Cursor: 游标对象
        """
        return self._cursor
    
    def get_connection(self) -> sqlite3.Connection:
        """获取连接对象
        
        Returns:
            sqlite3.Connection: 连接对象
        """
        return self._conn


# 创建全局数据库管理器实例
db_manager = DatabaseManager()
