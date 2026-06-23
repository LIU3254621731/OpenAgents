#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口组件

该模块实现了应用程序的主窗口，包含以下主要部分：
- 左侧聊天历史列表
- 中央聊天对话流
- 右侧讨论状态与流程控制区
- 底部多功能输入区

整体界面风格接近ChatGPT网页版，采用浅色主题，清晰的布局和流畅的交互。
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QFrame,
    QScrollArea, QSizePolicy, QMenuBar, QMenu, QMessageBox
)
from PySide6.QtGui import QFont, QIcon, QColor, QCursor
from PySide6.QtCore import Qt, QSize
from app.ui.chat_widget import ChatWidget
from app.ui.input_widget import InputWidget
from app.ui.status_panel import StatusPanel
from app.config.app_config import AppConfig
from app.core.workflow_manager import WorkflowManager
from app.core.discussion_engine import DiscussionEngine
from app.models.openai_model import OpenAIModel
from app.utils.logger import get_logger

logger = get_logger()


class MainWindow(QMainWindow):
    """主窗口类
    
    包含应用程序的主要布局和组件，管理各个UI组件之间的交互。
    """
    
    def __init__(self, config: AppConfig):
        """初始化主窗口
        
        Args:
            config (AppConfig): 应用配置实例
        """
        super().__init__()
        
        self.config = config
        self.is_discussion_running = False
        
        # 初始化核心组件
        self._init_core_components()
        
        # 设置窗口属性
        self.setWindowTitle("多智能体讨论系统")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建中央部件和布局
        self._create_central_widget()
        
        # 初始化UI状态
        self._init_ui_state()
        
        logger.info("主窗口初始化完成")
    
    def _init_core_components(self):
        """初始化核心组件"""
        # 初始化模型适配器
        model_config = self.config.get_model_config()
        model_type = model_config.get("type", "openai")
        
        if model_type == "openai":
            self.model_adapter = OpenAIModel(
                api_key=model_config["api_key"],
                base_url=model_config["api_base_url"],
                timeout=model_config["timeout"]
            )
        elif model_type == "local":
            from app.models.local_model import LocalModel
            self.model_adapter = LocalModel(
                base_url=model_config["api_base_url"],
                timeout=model_config["timeout"]
            )
        else:
            self.model_adapter = OpenAIModel(
                api_key=model_config["api_key"],
                base_url=model_config["api_base_url"],
                timeout=model_config["timeout"]
            )
        
        # 初始化工作流管理器
        self.workflow_manager = WorkflowManager()
        
        # 从数据库加载智能体
        self.workflow_manager.load_agents_from_database()
        
        # 如果数据库中没有智能体，添加默认智能体
        if not self.workflow_manager.get_agents():
            self._add_default_agents()
        
        # 初始化讨论引擎
        self.discussion_engine = DiscussionEngine(
            self.workflow_manager, self.model_adapter
        )
        
        # 连接讨论引擎信号
        self.discussion_engine.message_generated.connect(self._on_message_generated)
        self.discussion_engine.discussion_started.connect(self._on_discussion_started)
        self.discussion_engine.discussion_ended.connect(self._on_discussion_ended)
        self.discussion_engine.round_changed.connect(self._on_round_changed)
        self.discussion_engine.status_updated.connect(self._on_status_updated)
        
    def _add_default_agents(self):
        """添加默认智能体"""
        from app.core.agent import Agent, AgentPermission
        
        # 创建默认智能体
        agents = [
            {
                "agent_id": "agent_1",
                "name": "专家A",
                "model_id": self.config.get_model_config()["default_model"],
                "role_description": "你是一位领域专家，擅长深入分析问题，提供专业见解",
                "permissions": [AgentPermission.CAN_SPEAK, AgentPermission.CAN_START_NEXT_ROUND]
            },
            {
                "agent_id": "agent_2",
                "name": "专家B",
                "model_id": self.config.get_model_config()["default_model"],
                "role_description": "你是一位批判性思考者，擅长质疑和补充他人观点",
                "permissions": [AgentPermission.CAN_SPEAK]
            },
            {
                "agent_id": "agent_3",
                "name": "协调者",
                "model_id": self.config.get_model_config()["default_model"],
                "role_description": "你是一位协调者，擅长总结讨论，引导讨论方向",
                "permissions": [AgentPermission.CAN_SPEAK, AgentPermission.CAN_START_NEXT_ROUND, AgentPermission.CAN_TERMINATE_DISCUSSION]
            }
        ]
        
        # 添加智能体到工作流管理器
        for agent_data in agents:
            agent = Agent(
                agent_id=agent_data["agent_id"],
                name=agent_data["name"],
                model_id=agent_data["model_id"],
                role_description=agent_data["role_description"],
                permissions=agent_data["permissions"]
            )
            self.workflow_manager.add_agent(agent)
        
        # 设置默认讨论流程
        self.workflow_manager.set_workflow(["agent_1", "agent_2", "agent_3"])
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        new_chat_action = file_menu.addAction("新建讨论")
        new_chat_action.triggered.connect(self._new_discussion)
        
        file_menu.addSeparator()
        
        settings_action = file_menu.addAction("设置")
        settings_action.triggered.connect(self._open_settings)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("退出")
        exit_action.triggered.connect(self.close)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        workflow_action = edit_menu.addAction("编辑讨论流程")
        workflow_action.triggered.connect(self._open_workflow_editor)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self._open_about)
    
    def _create_central_widget(self):
        """创建中央部件和布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建左侧聊天历史面板
        self._create_chat_history_panel(main_layout)
        
        # 创建中央聊天面板
        self._create_chat_panel(main_layout)
        
        # 创建右侧状态面板
        self._create_status_panel(main_layout)
    
    def _create_chat_history_panel(self, parent_layout):
        """创建左侧聊天历史面板
        
        Args:
            parent_layout: 父布局
        """
        # 创建聊天历史框架
        chat_history_frame = QFrame()
        chat_history_frame.setFixedWidth(280)
        chat_history_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 1px solid #e1e4e8;
            }
        """)
        
        chat_history_layout = QVBoxLayout(chat_history_frame)
        chat_history_layout.setContentsMargins(16, 16, 16, 16)
        chat_history_layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("讨论历史")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        chat_history_layout.addWidget(title_label)
        
        # 新建讨论按钮
        new_chat_btn = QPushButton("+ 新建讨论")
        new_chat_btn.setFont(QFont("Arial", 14))
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        new_chat_btn.clicked.connect(self._new_discussion)
        chat_history_layout.addWidget(new_chat_btn)
        
        # 聊天历史列表
        self.chat_history_list = QListWidget()
        self.chat_history_list.setFont(QFont("Arial", 14))
        self.chat_history_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        chat_history_layout.addWidget(self.chat_history_list)
        
        parent_layout.addWidget(chat_history_frame)
    
    def _create_chat_panel(self, parent_layout):
        """创建中央聊天面板
        
        Args:
            parent_layout: 父布局
        """
        # 创建聊天面板框架
        chat_panel_frame = QFrame()
        chat_panel_frame.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        
        chat_panel_layout = QVBoxLayout(chat_panel_frame)
        chat_panel_layout.setContentsMargins(0, 0, 0, 0)
        chat_panel_layout.setSpacing(0)
        
        # 聊天窗口
        self.chat_widget = ChatWidget()
        chat_panel_layout.addWidget(self.chat_widget)
        
        # 输入窗口
        self.input_widget = InputWidget()
        self.input_widget.send_button.clicked.connect(self._start_discussion)
        chat_panel_layout.addWidget(self.input_widget)
        
        parent_layout.addWidget(chat_panel_frame)
    
    def _create_status_panel(self, parent_layout):
        """创建右侧状态面板
        
        Args:
            parent_layout: 父布局
        """
        # 创建状态面板框架
        status_panel_frame = QFrame()
        status_panel_frame.setFixedWidth(300)
        status_panel_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-left: 1px solid #e1e4e8;
            }
        """)
        
        status_panel_layout = QVBoxLayout(status_panel_frame)
        status_panel_layout.setContentsMargins(16, 16, 16, 16)
        status_panel_layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("讨论状态")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        status_panel_layout.addWidget(title_label)
        
        # 状态面板
        self.status_panel = StatusPanel()
        status_panel_layout.addWidget(self.status_panel)
        
        # 控制按钮
        control_layout = QVBoxLayout()
        control_layout.setSpacing(12)
        
        self.start_button = QPushButton("开始讨论")
        self.start_button.setFont(QFont("Arial", 14))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.start_button.clicked.connect(self._start_discussion)
        control_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("暂停讨论")
        self.pause_button.setFont(QFont("Arial", 14))
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: white;
            }
        """)
        self.pause_button.clicked.connect(self._pause_discussion)
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("终止讨论")
        self.stop_button.setFont(QFont("Arial", 14))
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.stop_button.clicked.connect(self._stop_discussion)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        status_panel_layout.addLayout(control_layout)
        
        parent_layout.addWidget(status_panel_frame)
    
    def _init_ui_state(self):
        """初始化UI状态"""
        # 设置默认讨论主题
        self.input_widget.text_edit.setPlaceholderText("输入讨论主题和需求...")
        
        # 初始化状态面板
        self.status_panel.set_topic("未设置")
        self.status_panel.set_round(0)
        self.status_panel.set_status("就绪")
    
    def _new_discussion(self):
        """新建讨论"""
        # 清空聊天窗口
        self.chat_widget.clear()
        
        # 清空输入框
        self.input_widget.text_edit.clear()
        
        # 重置状态面板
        self.status_panel.set_topic("未设置")
        self.status_panel.set_round(0)
        self.status_panel.set_status("就绪")
        
        # 重置讨论引擎
        self.discussion_engine.terminate()
        self._reset_controls()
        
        logger.info("新建讨论")
    
    def _start_discussion(self):
        """开始讨论"""
        # 获取讨论主题
        topic = self.input_widget.text_edit.toPlainText().strip()
        if not topic:
            QMessageBox.warning(self, "警告", "请输入讨论主题和需求")
            return
        
        # 设置讨论主题
        self.discussion_engine.set_topic(topic)
        self.status_panel.set_topic(topic)
        
        # 设置终止条件
        discussion_config = self.config.get_discussion_config()
        self.discussion_engine.set_termination_conditions(
            discussion_config["max_rounds"],
            discussion_config["max_time_per_round"],
            discussion_config["max_total_time"]
        )
        
        # 启动讨论引擎
        self.discussion_engine.start()
        
        logger.info(f"讨论开始，主题: {topic}")
    
    def _pause_discussion(self):
        """暂停讨论"""
        if self.discussion_engine.is_running:
            if self.discussion_engine.is_paused:
                self.discussion_engine.resume()
                self.pause_button.setText("暂停讨论")
                logger.info("讨论已恢复")
            else:
                self.discussion_engine.pause()
                self.pause_button.setText("恢复讨论")
                logger.info("讨论已暂停")
    
    def _stop_discussion(self):
        """终止讨论"""
        self.discussion_engine.terminate()
        logger.info("讨论已终止")
    
    def _reset_controls(self):
        """重置控制按钮状态"""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("暂停讨论")
        self.stop_button.setEnabled(False)
    
    def _on_message_generated(self, message):
        """处理智能体生成的消息
        
        Args:
            message (dict): 生成的消息，包含agent_id、name、content等
        """
        self.chat_widget.add_message(message)
    
    def _on_discussion_started(self):
        """处理讨论开始事件"""
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.status_panel.set_status("讨论中")
        
        logger.info("讨论开始")
    
    def _on_discussion_ended(self, result):
        """处理讨论结束事件
        
        Args:
            result (dict): 讨论结果，包含讨论历史、总结等
        """
        # 添加总结消息
        summary_message = {
            "agent_id": "system",
            "name": "系统",
            "role": "system",
            "content": result["summary"],
            "timestamp": result["duration"],
            "round": result["rounds"]
        }
        self.chat_widget.add_message(summary_message)
        
        # 重置控制按钮
        self._reset_controls()
        self.status_panel.set_status("讨论结束")
        
        logger.info(f"讨论结束，共 {result['rounds']} 轮，耗时 {result['duration']:.2f} 秒")
    
    def _on_round_changed(self, round_num):
        """处理轮次改变事件
        
        Args:
            round_num (int): 当前轮次
        """
        self.status_panel.set_round(round_num)
    
    def _on_status_updated(self, status):
        """处理状态更新事件
        
        Args:
            status (str): 状态描述
        """
        self.status_panel.set_status(status)
    
    def _open_settings(self):
        """打开设置对话框"""
        from app.ui.settings.settings_window import SettingsWindow
        settings_window = SettingsWindow(self.config)
        settings_window.show()
    
    def _open_workflow_editor(self):
        """打开讨论流程编辑器"""
        from app.ui.workflow_editor import WorkflowEditor
        workflow_editor = WorkflowEditor(self.workflow_manager, self)
        workflow_editor.exec()
        # 更新智能体列表
        self.workflow_manager.load_agents_from_database()
    
    def _open_about(self):
        """打开关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "多智能体讨论系统 Beta 版\n\n版本: 0.1.0\n\n一个本地运行的多智能体AI讨论系统桌面客户端"
        )
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 终止讨论引擎
        self.discussion_engine.terminate()
        
        # 等待线程结束
        self.discussion_engine.wait(1000)  # 等待1秒
        
        # 关闭HTTP客户端
        del self.model_adapter
        
        logger.info("应用程序已关闭")
        event.accept()
