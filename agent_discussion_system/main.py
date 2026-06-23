#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多智能体讨论系统 Beta 版 - 主启动脚本
版本: 0.1.0
描述: 启动多智能体AI讨论系统桌面客户端
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.ui.main_window import MainWindow
from app.config.app_config import AppConfig
from app.utils.logger import get_logger
from app.database import db_manager


def main():
    """主函数，启动应用程序"""
    # 初始化日志记录器
    logger = get_logger()
    logger.info("多智能体讨论系统 Beta 版启动")
    
    # 初始化配置
    config = AppConfig()
    config.load()
    
    # 初始化数据库连接
    try:
        db_manager.connect()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败：{e}")
        sys.exit(1)
    
    # 创建Qt应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("多智能体讨论系统")
    app.setApplicationVersion("0.1.0")
    
    # 设置应用图标
    # TODO: 添加应用图标
    
    # 创建主窗口
    main_window = MainWindow(config)
    main_window.show()
    
    # 启动事件循环
    logger.info("应用程序启动成功")
    result = app.exec()
    
    # 断开数据库连接
    db_manager.disconnect()
    logger.info("数据库连接已断开")
    
    sys.exit(result)


if __name__ == "__main__":
    main()
