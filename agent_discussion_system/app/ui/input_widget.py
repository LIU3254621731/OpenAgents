#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入组件

该模块实现了用户输入区，包含以下功能：
- 多行文本输入框，支持基本的文本编辑
- 发送按钮，用于提交讨论主题和需求
- 简洁的样式设计，与整体UI风格保持一致

输入区采用圆角设计，带有阴影效果，提供良好的视觉反馈和交互体验。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QSizePolicy
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize, QEvent
from app.utils.logger import get_logger

logger = get_logger()


class InputWidget(QWidget):
    """输入组件类
    
    负责用户输入讨论主题和需求，包含文本输入框和发送按钮。
    """
    
    def __init__(self):
        """初始化输入组件"""
        super().__init__()
        
        # 初始化UI
        self._init_ui()
        
        logger.info("输入组件初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(10)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        
        # 创建输入容器
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 16px;
            }
        """)
        
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(16, 16, 16, 10)
        input_layout.setSpacing(10)
        
        # 创建文本输入框
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Arial", 14))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                outline: none;
                color: #212529;
                placeholder-text-color: #6c757d;
            }
        """)
        self.text_edit.setPlaceholderText("输入讨论主题和需求...")
        self.text_edit.setMinimumHeight(100)
        self.text_edit.setMaximumHeight(200)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # 连接回车键发送信号
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.installEventFilter(self)
        
        input_layout.addWidget(self.text_edit)
        
        # 创建按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignRight)
        
        # 创建发送按钮
        self.send_button = QPushButton("开始讨论")
        self.send_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        button_layout.addWidget(self.send_button)
        
        input_layout.addWidget(button_container)
        
        layout.addWidget(input_container)
    
    def _on_text_changed(self):
        """文本变化事件处理"""
        # 启用或禁用发送按钮
        text = self.text_edit.toPlainText().strip()
        self.send_button.setEnabled(len(text) > 0)
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于处理回车键发送消息"""
        if obj == self.text_edit and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
                # Shift+Enter 换行
                return False
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Enter 发送消息
                if self.send_button.isEnabled():
                    self.send_button.click()
                return True
        return super().eventFilter(obj, event)
    
    def clear(self):
        """清空输入框"""
        self.text_edit.clear()
        self.send_button.setEnabled(False)
        logger.debug("输入框已清空")
