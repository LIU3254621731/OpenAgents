#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天对话流组件

该模块实现了聊天对话流的展示，支持多智能体对话，每个智能体的消息有不同的样式和颜色。
整体设计简洁清晰，支持滚动、复制等功能。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QTextBrowser, QSizePolicy, QPushButton
)
from PySide6.QtGui import QFont, QColor, QPalette, QTextCursor
from PySide6.QtCore import Qt, QSize
from app.utils.logger import get_logger

logger = get_logger()


class MessageBubble(QFrame):
    """消息气泡组件
    
    用于展示单条消息，包含发送者名称、头像占位符和消息内容。
    """
    
    def __init__(self, message: dict):
        """初始化消息气泡
        
        Args:
            message (dict): 消息内容，包含name、content、role等字段
        """
        super().__init__()
        
        self.message = message
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(8)
        
        # 设置样式
        self.setStyleSheet("""
            QFrame {
                border-radius: 12px;
            }
        """)
        
        # 根据角色设置不同的样式
        if self.message["role"] == "user":
            self.setStyleSheet("""
                QFrame {
                    background-color: #e9ecef;
                    border-radius: 12px;
                    margin-left: 40px;
                }
            """)
        elif self.message["role"] == "system":
            self.setStyleSheet("""
                QFrame {
                    background-color: #d1ecf1;
                    border-radius: 12px;
                    margin: 0 40px;
                }
            """)
        else:  # agent
            self.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 12px;
                    margin-right: 40px;
                }
            """)
        
        # 发送者名称
        name_label = QLabel(self.message["name"])
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet("""
            QLabel {
                color: #495057;
            }
        """)
        layout.addWidget(name_label)
        
        # 消息内容
        content_browser = QTextBrowser()
        content_browser.setHtml(self._format_content(self.message["content"]))
        content_browser.setFont(QFont("Arial", 14))
        content_browser.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                border: none;
                padding: 0;
                color: #212529;
            }
        """)
        content_browser.setOpenExternalLinks(True)
        content_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_browser.setMaximumHeight(500)
        content_browser.setMinimumHeight(50)
        layout.addWidget(content_browser)
        
        # 轮次信息
        round_label = QLabel(f"第 {self.message['round']} 轮")
        round_label.setFont(QFont("Arial", 12))
        round_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
            }
        """)
        round_label.setAlignment(Qt.AlignRight)
        layout.addWidget(round_label)
    
    def _format_content(self, content: str) -> str:
        """格式化消息内容
        
        Args:
            content (str): 原始消息内容
        
        Returns:
            str: 格式化后的HTML内容
        """
        # 简单的Markdown支持
        content = content.replace("\n", "<br>")
        content = content.replace("**", "<strong>")
        content = content.replace("**", "</strong>")
        content = content.replace("*", "<em>")
        content = content.replace("*", "</em>")
        return content


class ChatWidget(QWidget):
    """聊天对话流组件
    
    用于展示多智能体的聊天对话流，支持滚动、复制等功能。
    """
    
    def __init__(self):
        """初始化聊天对话流组件"""
        super().__init__()
        
        self._init_ui()
        logger.info("聊天对话流组件初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar {
                width: 8px;
            }
            QScrollBar::handle {
                background-color: #dee2e6;
                border-radius: 4px;
            }
            QScrollBar::handle:hover {
                background-color: #adb5bd;
            }
        """)
        
        # 创建内容容器
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 20, 0, 20)
        self.content_layout.setSpacing(0)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        # 添加初始欢迎消息
        welcome_message = {
            "name": "系统",
            "content": "欢迎使用多智能体讨论系统！请在下方输入讨论主题和需求，然后点击开始讨论按钮。",
            "role": "system",
            "round": 0
        }
        self.add_message(welcome_message)
        
        # 将内容容器添加到滚动区域
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
    
    def add_message(self, message: dict):
        """添加消息到聊天对话流
        
        Args:
            message (dict): 消息内容，包含name、content、role、round等字段
        """
        # 创建消息气泡
        message_bubble = MessageBubble(message)
        self.content_layout.addWidget(message_bubble)
        
        # 自动滚动到底部
        self._scroll_to_bottom()
        
        logger.debug(f"添加消息，发送者: {message['name']}")
    
    def clear(self):
        """清空聊天对话流"""
        # 清空所有消息，保留欢迎消息
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        logger.info("聊天对话流已清空")
    
    def _scroll_to_bottom(self):
        """自动滚动到底部"""
        # 获取父级滚动区域
        scroll_area = self.parentWidget()
        if scroll_area and hasattr(scroll_area, "verticalScrollBar"):
            # 延迟滚动，确保UI已更新
            scroll_bar = scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
