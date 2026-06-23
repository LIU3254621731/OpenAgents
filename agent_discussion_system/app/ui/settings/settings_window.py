#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置窗口

现代化的设置界面，包含应用设置、模型设置、讨论设置等多个选项卡，支持设置项的增删改查功能。
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QLabel,
    QPushButton, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QGroupBox, QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize
from app.utils.logger import get_logger
from app.config.app_config import AppConfig

logger = get_logger()


class SettingsWindow(QMainWindow):
    """设置窗口类
    
    现代化的设置界面，包含多个选项卡，支持设置项的增删改查功能。
    """
    
    def __init__(self, config: AppConfig):
        """初始化设置窗口
        
        Args:
            config: 应用配置实例
        """
        super().__init__()
        self.config = config
        self._init_ui()
        self._load_config()
        
    def _init_ui(self):
        """初始化UI界面"""
        # 设置窗口属性
        self.setWindowTitle("设置")
        self.setMinimumSize(900, 600)
        self.setWindowIcon(QIcon())  # TODO: 添加应用图标
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                background-color: #f8f9fa;
                border: none;
            }
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                margin: 10px;
            }
            QTabBar {
                background-color: #f8f9fa;
                padding: 10px 10px 0 10px;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #6c757d;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                font-size: 14px;
                border: 1px solid transparent;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                color: #495057;
                background-color: #e9ecef;
            }
            QTabBar::tab:selected {
                color: #007bff;
                background-color: white;
                border-color: #e9ecef;
            }
        """)
        
        # 添加选项卡
        self.tab_widget.addTab(self._create_app_settings_tab(), "应用设置")
        self.tab_widget.addTab(self._create_model_settings_tab(), "模型设置")
        self.tab_widget.addTab(self._create_discussion_settings_tab(), "讨论设置")
        self.tab_widget.addTab(self._create_knowledge_base_settings_tab(), "知识库设置")
        
        main_layout.addWidget(self.tab_widget)
        
        # 底部按钮区域
        self._create_bottom_buttons(main_layout)
        
    def _create_app_settings_tab(self) -> QWidget:
        """创建应用设置选项卡
        
        Returns:
            QWidget: 应用设置选项卡
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 应用基本信息卡片
        app_info_card = self._create_card()
        app_info_layout = QVBoxLayout(app_info_card)
        app_info_layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("应用基本信息")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #212529;")
        app_info_layout.addWidget(title_label)
        
        # 应用名称
        app_name_layout = self._create_setting_row("应用名称", "多智能体讨论系统")
        app_info_layout.addLayout(app_name_layout)
        
        # 应用版本
        app_version_layout = self._create_setting_row("应用版本", "0.1.0")
        app_info_layout.addLayout(app_version_layout)
        
        # 语言设置
        language_layout = self._create_setting_row("语言", self._create_language_combo())
        app_info_layout.addLayout(language_layout)
        
        # 主题设置
        theme_layout = self._create_setting_row("主题", self._create_theme_combo())
        app_info_layout.addLayout(theme_layout)
        
        layout.addWidget(app_info_card)
        
        # 其他设置卡片
        other_settings_card = self._create_card()
        other_settings_layout = QVBoxLayout(other_settings_card)
        other_settings_layout.setSpacing(16)
        
        # 标题
        other_title_label = QLabel("其他设置")
        other_title_label.setFont(QFont("Arial", 16, QFont.Bold))
        other_title_label.setStyleSheet("color: #212529;")
        other_settings_layout.addWidget(other_title_label)
        
        # 自动更新
        auto_update_layout = self._create_setting_row("自动检查更新", self._create_auto_update_checkbox())
        other_settings_layout.addLayout(auto_update_layout)
        
        # 日志级别
        log_level_layout = self._create_setting_row("日志级别", self._create_log_level_combo())
        other_settings_layout.addLayout(log_level_layout)
        
        layout.addWidget(other_settings_card)
        
        layout.addStretch()
        
        return tab
    
    def _create_model_settings_tab(self) -> QWidget:
        """创建模型设置选项卡
        
        Returns:
            QWidget: 模型设置选项卡
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 模型类型选择卡片
        model_type_card = self._create_card()
        model_type_layout = QVBoxLayout(model_type_card)
        model_type_layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("模型类型")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #212529;")
        model_type_layout.addWidget(title_label)
        
        # 模型类型选择
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["OpenAI API", "本地模型"])
        self.model_type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                color: #212529;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #007bff;
            }
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        
        model_type_layout.addLayout(self._create_setting_row("模型类型", self.model_type_combo))
        
        layout.addWidget(model_type_card)
        
        # OpenAI API 设置卡片
        openai_card = self._create_card()
        self.openai_layout = QVBoxLayout(openai_card)
        self.openai_layout.setSpacing(16)
        
        # 标题
        openai_title_label = QLabel("OpenAI API 设置")
        openai_title_label.setFont(QFont("Arial", 16, QFont.Bold))
        openai_title_label.setStyleSheet("color: #212529;")
        self.openai_layout.addWidget(openai_title_label)
        
        # API 密钥
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("请输入OpenAI API密钥")
        self.api_key_input.setStyleSheet(self._get_line_edit_style())
        self.openai_layout.addLayout(self._create_setting_row("API 密钥", self.api_key_input))
        
        # API 基础 URL
        self.api_base_url_input = QLineEdit()
        self.api_base_url_input.setPlaceholderText("https://api.openai.com/v1")
        self.api_base_url_input.setStyleSheet(self._get_line_edit_style())
        self.openai_layout.addLayout(self._create_setting_row("API 基础 URL", self.api_base_url_input))
        
        # 默认模型
        self.default_model_combo = QComboBox()
        self.default_model_combo.addItems(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"])
        self.default_model_combo.setStyleSheet(self._get_combo_style())
        self.openai_layout.addLayout(self._create_setting_row("默认模型", self.default_model_combo))
        
        layout.addWidget(openai_card)
        
        # 本地模型设置卡片
        local_model_card = self._create_card()
        self.local_model_layout = QVBoxLayout(local_model_card)
        self.local_model_layout.setSpacing(16)
        
        # 标题
        local_model_title_label = QLabel("本地模型设置")
        local_model_title_label.setFont(QFont("Arial", 16, QFont.Bold))
        local_model_title_label.setStyleSheet("color: #212529;")
        self.local_model_layout.addWidget(local_model_title_label)
        
        # 本地模型 API URL
        self.local_model_url_input = QLineEdit()
        self.local_model_url_input.setPlaceholderText("http://localhost:11434")
        self.local_model_url_input.setStyleSheet(self._get_line_edit_style())
        self.local_model_layout.addLayout(self._create_setting_row("本地模型 API URL", self.local_model_url_input))
        
        # 本地模型名称
        self.local_model_name_input = QLineEdit()
        self.local_model_name_input.setPlaceholderText("例如: llama3")
        self.local_model_name_input.setStyleSheet(self._get_line_edit_style())
        self.local_model_layout.addLayout(self._create_setting_row("本地模型名称", self.local_model_name_input))
        
        layout.addWidget(local_model_card)
        
        # 模型通用设置卡片
        model_common_card = self._create_card()
        model_common_layout = QVBoxLayout(model_common_card)
        model_common_layout.setSpacing(16)
        
        # 标题
        model_common_title_label = QLabel("模型通用设置")
        model_common_title_label.setFont(QFont("Arial", 16, QFont.Bold))
        model_common_title_label.setStyleSheet("color: #212529;")
        model_common_layout.addWidget(model_common_title_label)
        
        # 超时时间
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 300)
        self.timeout_spinbox.setSuffix(" 秒")
        self.timeout_spinbox.setStyleSheet(self._get_spinbox_style())
        model_common_layout.addLayout(self._create_setting_row("请求超时时间", self.timeout_spinbox))
        
        layout.addWidget(model_common_card)
        
        layout.addStretch()
        
        return tab
    
    def _create_discussion_settings_tab(self) -> QWidget:
        """创建讨论设置选项卡
        
        Returns:
            QWidget: 讨论设置选项卡
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 讨论终止条件卡片
        termination_card = self._create_card()
        termination_layout = QVBoxLayout(termination_card)
        termination_layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("讨论终止条件")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #212529;")
        termination_layout.addWidget(title_label)
        
        # 最大轮次
        self.max_rounds_spinbox = QSpinBox()
        self.max_rounds_spinbox.setRange(1, 100)
        self.max_rounds_spinbox.setStyleSheet(self._get_spinbox_style())
        termination_layout.addLayout(self._create_setting_row("最大轮次", self.max_rounds_spinbox))
        
        # 每轮最大时间
        self.max_time_per_round_spinbox = QSpinBox()
        self.max_time_per_round_spinbox.setRange(30, 3600)
        self.max_time_per_round_spinbox.setSuffix(" 秒")
        self.max_time_per_round_spinbox.setStyleSheet(self._get_spinbox_style())
        termination_layout.addLayout(self._create_setting_row("每轮最大时间", self.max_time_per_round_spinbox))
        
        # 总最大时间
        self.max_total_time_spinbox = QSpinBox()
        self.max_total_time_spinbox.setRange(60, 7200)
        self.max_total_time_spinbox.setSuffix(" 秒")
        self.max_total_time_spinbox.setStyleSheet(self._get_spinbox_style())
        termination_layout.addLayout(self._create_setting_row("总最大时间", self.max_total_time_spinbox))
        
        layout.addWidget(termination_card)
        
        layout.addStretch()
        
        return tab
    
    def _create_knowledge_base_settings_tab(self) -> QWidget:
        """创建知识库设置选项卡
        
        Returns:
            QWidget: 知识库设置选项卡
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 知识库基本设置卡片
        kb_base_card = self._create_card()
        kb_base_layout = QVBoxLayout(kb_base_card)
        kb_base_layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("知识库基本设置")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #212529;")
        kb_base_layout.addWidget(title_label)
        
        # 启用知识库
        self.enable_kb_checkbox = QCheckBox()
        self.enable_kb_checkbox.setStyleSheet(self._get_checkbox_style())
        kb_base_layout.addLayout(self._create_setting_row("启用知识库", self.enable_kb_checkbox))
        
        layout.addWidget(kb_base_card)
        
        layout.addStretch()
        
        return tab
    
    def _create_card(self) -> QFrame:
        """创建卡片组件
        
        Returns:
            QFrame: 卡片组件
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e9ecef;
            }
        """)
        return card
    
    def _create_setting_row(self, label_text: str, widget_or_text: object) -> QHBoxLayout:
        """创建设置项行
        
        Args:
            label_text: 设置项标签文本
            widget_or_text: 设置项控件或文本
        
        Returns:
            QHBoxLayout: 设置项行布局
        """
        layout = QHBoxLayout()
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 标签
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 14))
        label.setStyleSheet("color: #495057;")
        label.setFixedWidth(150)
        layout.addWidget(label)
        
        # 控件或文本
        if isinstance(widget_or_text, str):
            # 如果是文本，创建QLabel
            text_label = QLabel(widget_or_text)
            text_label.setFont(QFont("Arial", 14))
            text_label.setStyleSheet("color: #6c757d;")
            text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout.addWidget(text_label)
        else:
            # 如果是控件，直接添加
            widget_or_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout.addWidget(widget_or_text)
        
        return layout
    
    def _create_language_combo(self) -> QComboBox:
        """创建语言选择下拉框
        
        Returns:
            QComboBox: 语言选择下拉框
        """
        combo = QComboBox()
        combo.addItems(["中文", "English"])
        combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                color: #212529;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #007bff;
            }
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        return combo
    
    def _create_theme_combo(self) -> QComboBox:
        """创建主题选择下拉框
        
        Returns:
            QComboBox: 主题选择下拉框
        """
        combo = QComboBox()
        combo.addItems(["浅色主题", "深色主题"])
        combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                color: #212529;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #007bff;
            }
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        return combo
    
    def _create_auto_update_checkbox(self) -> QCheckBox:
        """创建自动更新复选框
        
        Returns:
            QCheckBox: 自动更新复选框
        """
        checkbox = QCheckBox()
        checkbox.setStyleSheet("""
            QCheckBox {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #007bff;
            }
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
                image: url(:/icons/checkmark.svg);
            }
        """)
        return checkbox
    
    def _create_log_level_combo(self) -> QComboBox:
        """创建日志级别下拉框
        
        Returns:
            QComboBox: 日志级别下拉框
        """
        combo = QComboBox()
        combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                color: #212529;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #007bff;
            }
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        return combo
    
    def _create_bottom_buttons(self, parent_layout: QVBoxLayout):
        """创建底部按钮区域
        
        Args:
            parent_layout: 父布局
        """
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #e9ecef;
                padding: 16px 20px;
            }
        """)
        
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        button_layout.setAlignment(Qt.AlignRight)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                color: #495057;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:focus {
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
                border: 1px solid #007bff;
                border-radius: 8px;
                background-color: #007bff;
                color: white;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            QPushButton:focus {
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(save_button)
        
        parent_layout.addWidget(button_container)
    
    def _load_config(self):
        """加载配置到界面"""
        config = self.config.get_config()
        
        # 模型设置
        model_config = config.get("model", {})
        model_type = model_config.get("type", "openai")
        self.model_type_combo.setCurrentIndex(0 if model_type == "openai" else 1)
        
        self.api_key_input.setText(model_config.get("api_key", ""))
        self.api_base_url_input.setText(model_config.get("api_base_url", "https://api.openai.com/v1"))
        self.default_model_combo.setCurrentText(model_config.get("default_model", "gpt-4o-mini"))
        self.local_model_url_input.setText(model_config.get("api_base_url", "http://localhost:11434"))
        self.local_model_name_input.setText(model_config.get("default_model", ""))
        self.timeout_spinbox.setValue(model_config.get("timeout", 30))
        
        # 讨论设置
        discussion_config = config.get("discussion", {})
        self.max_rounds_spinbox.setValue(discussion_config.get("max_rounds", 10))
        self.max_time_per_round_spinbox.setValue(discussion_config.get("max_time_per_round", 60))
        self.max_total_time_spinbox.setValue(discussion_config.get("max_total_time", 300))
        
        # 知识库设置
        kb_config = config.get("knowledge_base", {})
        self.enable_kb_checkbox.setChecked(kb_config.get("enabled", True))
    
    def _save_settings(self):
        """保存设置"""
        config = self.config.get_config()
        
        # 模型设置
        model_config = config.get("model", {})
        model_config["type"] = "openai" if self.model_type_combo.currentIndex() == 0 else "local"
        model_config["api_key"] = self.api_key_input.text()
        model_config["api_base_url"] = self.api_base_url_input.text()
        model_config["default_model"] = self.default_model_combo.currentText()
        model_config["timeout"] = self.timeout_spinbox.value()
        
        # 讨论设置
        discussion_config = config.get("discussion", {})
        discussion_config["max_rounds"] = self.max_rounds_spinbox.value()
        discussion_config["max_time_per_round"] = self.max_time_per_round_spinbox.value()
        discussion_config["max_total_time"] = self.max_total_time_spinbox.value()
        
        # 知识库设置
        kb_config = config.get("knowledge_base", {})
        kb_config["enabled"] = self.enable_kb_checkbox.isChecked()
        
        # 保存配置
        self.config.set_config(config)
        self.config.save()
        
        logger.info("设置已保存")
        self.close()
    
    def _get_line_edit_style(self) -> str:
        """获取行编辑框样式
        
        Returns:
            str: 行编辑框样式
        """
        return """
            QLineEdit {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                color: #212529;
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #007bff;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """
    
    def _get_combo_style(self) -> str:
        """获取下拉框样式
        
        Returns:
            str: 下拉框样式
        """
        return """
            QComboBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                color: #212529;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #007bff;
            }
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """
    
    def _get_spinbox_style(self) -> str:
        """获取数值输入框样式
        
        Returns:
            str: 数值输入框样式
        """
        return """
            QSpinBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                color: #212529;
                background-color: white;
            }
            QSpinBox:hover {
                border-color: #007bff;
            }
            QSpinBox:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """
    
    def _get_checkbox_style(self) -> str:
        """获取复选框样式
        
        Returns:
            str: 复选框样式
        """
        return """
            QCheckBox {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #007bff;
            }
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
            }
        """
