#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态面板组件

该模块实现了右侧的讨论状态与流程控制区，包含以下功能：
- 显示讨论主题
- 显示终止条件（自然语言）
- 显示当前轮次/最大轮次
- 显示当前运行状态
- 提供编辑讨论流程和手动终止按钮

状态面板采用卡片式设计，清晰展示讨论的关键信息和控制选项。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QGroupBox, QGridLayout
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt
from app.utils.logger import get_logger

logger = get_logger()


class StatusPanel(QWidget):
    """状态面板类
    
    负责显示讨论状态和流程控制信息，包括讨论主题、当前轮次、运行状态等。
    """
    
    def __init__(self):
        """初始化状态面板"""
        super().__init__()
        
        self._init_ui()
        logger.info("状态面板组件初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 创建主题卡片
        self._create_topic_card(layout)
        
        # 创建轮次卡片
        self._create_round_card(layout)
        
        # 创建状态卡片
        self._create_status_card(layout)
        
        # 创建控制卡片
        self._create_control_card(layout)
    
    def _create_topic_card(self, parent_layout):
        """创建主题卡片
        
        Args:
            parent_layout: 父布局
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("讨论主题")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
            }
        """)
        layout.addWidget(title_label)
        
        # 主题内容
        self.topic_label = QLabel("未设置")
        self.topic_label.setFont(QFont("Arial", 14))
        self.topic_label.setStyleSheet("""
            QLabel {
                color: #212529;
            }
        """)
        self.topic_label.setWordWrap(True)
        layout.addWidget(self.topic_label)
        
        parent_layout.addWidget(card)
    
    def _create_round_card(self, parent_layout):
        """创建轮次卡片
        
        Args:
            parent_layout: 父布局
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("讨论轮次")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
            }
        """)
        layout.addWidget(title_label)
        
        # 轮次信息
        round_layout = QHBoxLayout()
        round_layout.setContentsMargins(0, 0, 0, 0)
        round_layout.setSpacing(8)
        
        self.current_round_label = QLabel("0")
        self.current_round_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.current_round_label.setStyleSheet("""
            QLabel {
                color: #007bff;
            }
        """)
        round_layout.addWidget(self.current_round_label)
        
        slash_label = QLabel("/")
        slash_label.setFont(QFont("Arial", 24))
        slash_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
            }
        """)
        round_layout.addWidget(slash_label)
        
        self.max_round_label = QLabel("10")
        self.max_round_label.setFont(QFont("Arial", 24))
        self.max_round_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
            }
        """)
        round_layout.addWidget(self.max_round_label)
        
        round_layout.addStretch()
        
        layout.addLayout(round_layout)
        
        parent_layout.addWidget(card)
    
    def _create_status_card(self, parent_layout):
        """创建状态卡片
        
        Args:
            parent_layout: 父布局
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("运行状态")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
            }
        """)
        layout.addWidget(title_label)
        
        # 状态内容
        self.status_label = QLabel("就绪")
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #28a745;
            }
        """)
        layout.addWidget(self.status_label)
        
        parent_layout.addWidget(card)
    
    def _create_control_card(self, parent_layout):
        """创建控制卡片
        
        Args:
            parent_layout: 父布局
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("流程控制")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
            }
        """)
        layout.addWidget(title_label)
        
        # 编辑流程按钮
        edit_button = QPushButton("编辑讨论流程")
        edit_button.setFont(QFont("Arial", 13))
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #495057;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        layout.addWidget(edit_button)
        
        # 终止讨论按钮
        terminate_button = QPushButton("手动终止")
        terminate_button.setFont(QFont("Arial", 13, QFont.Bold))
        terminate_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        terminate_button.setEnabled(False)
        layout.addWidget(terminate_button)
        
        parent_layout.addWidget(card)
    
    def set_topic(self, topic: str):
        """设置讨论主题
        
        Args:
            topic (str): 讨论主题
        """
        self.topic_label.setText(topic)
    
    def set_round(self, round_num: int):
        """设置当前轮次
        
        Args:
            round_num (int): 当前轮次
        """
        self.current_round_label.setText(str(round_num))
    
    def set_max_round(self, max_round: int):
        """设置最大轮次
        
        Args:
            max_round (int): 最大轮次
        """
        self.max_round_label.setText(str(max_round))
    
    def set_status(self, status: str):
        """设置运行状态
        
        Args:
            status (str): 运行状态
        """
        self.status_label.setText(status)
        
        # 根据状态设置不同的颜色
        if status == "就绪":
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-family: Arial;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
        elif status == "讨论中":
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #007bff;
                    font-family: Arial;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
        elif status == "讨论结束":
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-family: Arial;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
        elif status == "暂停":
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffc107;
                    font-family: Arial;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
        elif status == "错误":
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-family: Arial;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
