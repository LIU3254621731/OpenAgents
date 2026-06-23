#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讨论流程设计界面

该模块实现了讨论流程设计界面，用于可视化配置讨论流程，形式类似思维导图/流程图：
- 节点代表Agent
- 连线代表发言顺序
- 点击节点可配置：使用的模型、角色描述、权限、控制字符串

该配置直接驱动后台调度逻辑。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QListWidget, QListWidgetItem, QMenu, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsLineItem
)
from PySide6.QtGui import QFont, QColor, QPen, QBrush, QCursor, QPainter
from PySide6.QtCore import Qt, QPointF, QSize
from app.core.agent import Agent, AgentPermission
from app.utils.logger import get_logger

logger = get_logger()


class BaseNode(QGraphicsRectItem):
    """基础节点类
    
    所有流程图节点的基类，提供公共功能。
    """
    
    def __init__(self, parent=None):
        """初始化基础节点
        
        Args:
            parent: 父图形项
        """
        super().__init__(parent)
        self.is_selected = False
        
        # 设置基础样式和标志
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
    
    def itemChange(self, change, value):
        """处理节点变化事件"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # 通知场景更新连线
            scene = self.scene()
            if scene and hasattr(scene, "update_connections"):
                scene.update_connections()
                # 保存节点位置
                if scene and hasattr(scene, "save_workflow"):
                    scene.save_workflow()
        return super().itemChange(change, value)


class AgentNode(BaseNode):
    """智能体节点类
    
    表示流程图中的智能体节点，包含智能体信息和可视化样式。
    """
    
    def __init__(self, agent: Agent, parent=None):
        """初始化智能体节点
        
        Args:
            agent (Agent): 智能体实例
            parent: 父图形项
        """
        super().__init__(parent)
        
        self.agent = agent
        
        # 设置节点样式
        self.setRect(0, 0, 200, 120)
        self.setBrush(QBrush(QColor(248, 249, 250)))
        self.setPen(QPen(QColor(222, 226, 230), 2))
        
        # 创建文本项
        self._create_text_items()
    
    def _create_text_items(self):
        """创建节点中的文本项"""
        # 智能体名称
        name_text = QGraphicsTextItem(self.agent.name, self)
        name_text.setFont(QFont("Arial", 12, QFont.Bold))
        name_text.setDefaultTextColor(QColor(73, 80, 87))
        name_text.setPos(10, 10)
        
        # 模型ID
        model_text = QGraphicsTextItem(f"模型: {self.agent.model_id}", self)
        model_text.setFont(QFont("Arial", 10))
        model_text.setDefaultTextColor(QColor(108, 117, 125))
        model_text.setPos(10, 40)
        
        # 权限信息
        permissions = ", ".join([p.value for p in self.agent.permissions])
        perm_text = QGraphicsTextItem(f"权限: {permissions}", self)
        perm_text.setFont(QFont("Arial", 10))
        perm_text.setDefaultTextColor(QColor(108, 117, 125))
        perm_text.setPos(10, 70)
        
        # 节点ID
        id_text = QGraphicsTextItem(f"ID: {self.agent.agent_id[:8]}...", self)
        id_text.setFont(QFont("Arial", 9))
        id_text.setDefaultTextColor(QColor(173, 181, 189))
        id_text.setPos(10, 100)


class ConditionNode(BaseNode):
    """条件分支节点类
    
    表示流程图中的条件判断节点，用于实现条件分支逻辑。
    """
    
    def __init__(self, condition_id: str, condition_text: str = "条件判断", parent=None):
        """初始化条件分支节点
        
        Args:
            condition_id (str): 条件ID
            condition_text (str): 条件文本描述
            parent: 父图形项
        """
        super().__init__(parent)
        
        self.condition_id = condition_id
        self.condition_text = condition_text
        self.conditions = []  # 存储条件列表
        
        # 设置节点样式
        self.setRect(0, 0, 200, 100)
        self.setBrush(QBrush(QColor(255, 248, 225)))
        self.setPen(QPen(QColor(255, 215, 0), 2))
        
        # 创建文本项
        self._create_text_items()
    
    def _create_text_items(self):
        """创建节点中的文本项"""
        # 条件名称
        name_text = QGraphicsTextItem("条件分支", self)
        name_text.setFont(QFont("Arial", 12, QFont.Bold))
        name_text.setDefaultTextColor(QColor(139, 69, 19))
        name_text.setPos(10, 10)
        
        # 条件描述
        desc_text = QGraphicsTextItem(self.condition_text, self)
        desc_text.setFont(QFont("Arial", 10))
        desc_text.setDefaultTextColor(QColor(139, 69, 19))
        desc_text.setPos(10, 40)
        
        # 条件ID
        id_text = QGraphicsTextItem(f"ID: {self.condition_id[:8]}...", self)
        id_text.setFont(QFont("Arial", 9))
        id_text.setDefaultTextColor(QColor(160, 82, 45))
        id_text.setPos(10, 70)
    
    def add_condition(self, condition: dict):
        """添加条件
        
        Args:
            condition (dict): 条件配置，包含condition和next_agent_id字段
        """
        self.conditions.append(condition)
    
    def update_condition_text(self, text: str):
        """更新条件文本描述
        
        Args:
            text (str): 新的条件文本描述
        """
        self.condition_text = text
        # 重新创建文本项
        self._clear_text_items()
        self._create_text_items()
    
    def _clear_text_items(self):
        """清除节点中的文本项"""
        for item in self.childItems():
            if isinstance(item, QGraphicsTextItem):
                self.scene().removeItem(item)
                item.deleteLater()


class WorkflowScene(QGraphicsScene):
    """工作流场景类
    
    管理智能体节点和连线的可视化场景。
    """
    
    def __init__(self, workflow_manager):
        """初始化工作流场景
        
        Args:
            workflow_manager: 工作流管理器实例
        """
        super().__init__()
        
        self.workflow_manager = workflow_manager
        self.nodes = []
        self.connections = []
        
        # 设置场景背景
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        
        # 加载智能体节点
        self.load_agents()
    
    def load_agents(self):
        """加载智能体节点"""
        # 清空现有节点和连线
        self.clear()
        self.nodes.clear()
        self.connections.clear()
        
        # 从配置中加载节点位置
        from app.config.app_config import AppConfig
        app_config = AppConfig()
        app_config.load()
        workflow_config = app_config.get("workflow", {})
        node_positions = workflow_config.get("node_positions", {})
        
        # 添加智能体节点
        agents = self.workflow_manager.get_agents()
        for i, agent in enumerate(agents.values()):
            node = AgentNode(agent)
            # 从配置中获取位置，否则使用默认位置
            if agent.agent_id in node_positions:
                pos = node_positions[agent.agent_id]
                node.setPos(pos["x"], pos["y"])
            else:
                node.setPos(100 + i * 250, 100)
            self.addItem(node)
            self.nodes.append(node)
        
        # 从配置中加载条件分支节点
        conditions = workflow_config.get("conditions", [])
        for condition in conditions:
            node = ConditionNode(condition["id"], condition["text"])
            if condition["id"] in node_positions:
                pos = node_positions[condition["id"]]
                node.setPos(pos["x"], pos["y"])
            else:
                node.setPos(100 + len(self.nodes) * 250, 300)
            # 添加条件规则
            for cond_rule in condition.get("rules", []):
                node.add_condition(cond_rule)
            self.addItem(node)
            self.nodes.append(node)
        
        # 创建连线
        self.create_connections()
    
    def create_connections(self):
        """创建智能体节点之间的连线"""
        # 清空现有连线
        for connection in self.connections:
            self.removeItem(connection)
        self.connections.clear()
        
        # 创建新连线
        for i in range(len(self.nodes) - 1):
            start_node = self.nodes[i]
            end_node = self.nodes[i + 1]
            
            connection = QGraphicsLineItem()
            connection.setPen(QPen(QColor(0, 123, 255), 2, Qt.DashLine))
            self.addItem(connection)
            self.connections.append(connection)
        
        # 更新连线位置
        self.update_connections()
    
    def update_connections(self):
        """更新连线位置"""
        for i, connection in enumerate(self.connections):
            if i < len(self.nodes) - 1:
                start_node = self.nodes[i]
                end_node = self.nodes[i + 1]
                
                start_point = QPointF(
                    start_node.rect().right(),
                    start_node.rect().center().y()
                )
                end_point = QPointF(
                    end_node.rect().left(),
                    end_node.rect().center().y()
                )
                
                start_global = start_node.mapToScene(start_point)
                end_global = end_node.mapToScene(end_point)
                
                connection.setLine(start_global.x(), start_global.y(), end_global.x(), end_global.y())
    
    def reorder_nodes(self):
        """根据节点的X坐标重新排序节点列表"""
        # 根据节点的X坐标排序
        self.nodes.sort(key=lambda node: node.scenePos().x())
        
        # 更新连线
        self.create_connections()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件，用于检测节点拖拽结束"""
        super().mouseReleaseEvent(event)
        
        # 检查是否有节点被移动
        moved = False
        for item in self.items():
            if isinstance(item, AgentNode) and item.isSelected():
                moved = True
                break
        
        if moved:
            # 重新排序节点
            self.reorder_nodes()
    
    def contextMenuEvent(self, event):
        """上下文菜单事件"""
        menu = QMenu()
        
        # 添加智能体节点
        add_agent_action = menu.addAction("添加智能体")
        add_agent_action.triggered.connect(self._add_agent)
        
        # 添加条件分支节点
        add_condition_action = menu.addAction("添加条件分支")
        add_condition_action.triggered.connect(self._add_condition)
        
        # 删除选中节点
        if len(self.selectedItems()) > 0:
            delete_action = menu.addAction("删除节点")
            delete_action.triggered.connect(self._delete_selected)
        
        # 编辑选中节点
        if len(self.selectedItems()) == 1:
            if isinstance(self.selectedItems()[0], AgentNode):
                edit_action = menu.addAction("编辑智能体")
                edit_action.triggered.connect(self._edit_selected)
            elif isinstance(self.selectedItems()[0], ConditionNode):
                edit_action = menu.addAction("编辑条件分支")
                edit_action.triggered.connect(self._edit_condition)
        
        menu.exec_(event.screenPos())
    
    def _add_agent(self):
        """添加智能体"""
        # 简化实现，实际应打开对话框让用户配置
        from uuid import uuid4
        
        agent_id = str(uuid4())
        new_agent = Agent(
            agent_id=agent_id,
            name=f"智能体 {len(self.nodes) + 1}",
            model_id="gpt-4o-mini",
            role_description="一个通用智能体",
            permissions=[AgentPermission.CAN_SPEAK]
        )
        
        # 添加到工作流管理器
        self.workflow_manager.add_agent(new_agent)
        
        # 重新加载节点
        self.load_agents()
    
    def _add_condition(self):
        """添加条件分支节点"""
        from uuid import uuid4
        
        condition_id = str(uuid4())
        condition_node = ConditionNode(condition_id, "条件判断")
        
        # 添加到场景
        condition_node.setPos(100 + len(self.nodes) * 250, 300)
        self.addItem(condition_node)
        self.nodes.append(condition_node)
        
        # 创建连线
        self.create_connections()
    
    def _delete_selected(self):
        """删除选中节点"""
        for item in self.selectedItems():
            if isinstance(item, AgentNode):
                # 从工作流管理器中删除
                self.workflow_manager.remove_agent(item.agent.agent_id)
            elif isinstance(item, ConditionNode):
                # 从节点列表中移除
                if item in self.nodes:
                    self.nodes.remove(item)
                # 从场景中移除
                self.removeItem(item)
        
        # 重新加载节点
        self.load_agents()
    
    def _edit_selected(self):
        """编辑智能体节点"""
        if len(self.selectedItems()) == 1 and isinstance(self.selectedItems()[0], AgentNode):
            node = self.selectedItems()[0]
            # 打开编辑对话框
            dialog = AgentEditDialog(node.agent)
            if dialog.exec() == QDialog.Accepted:
                # 更新节点显示
                self.load_agents()
                logger.info(f"编辑智能体: {node.agent.name}")
    
    def _edit_condition(self):
        """编辑条件分支节点"""
        if len(self.selectedItems()) == 1 and isinstance(self.selectedItems()[0], ConditionNode):
            node = self.selectedItems()[0]
            # 打开编辑对话框
            dialog = ConditionEditDialog(node, self.workflow_manager)
            if dialog.exec() == QDialog.Accepted:
                # 保存工作流配置
                self.save_workflow()
                logger.info(f"编辑条件分支: {node.condition_id}")
    
    def save_workflow(self):
        """保存工作流配置到文件"""
        from app.config.app_config import AppConfig
        app_config = AppConfig()
        app_config.load()
        
        # 构建节点位置配置
        node_positions = {}
        conditions = []
        
        for node in self.nodes:
            pos = node.pos()
            if isinstance(node, AgentNode):
                # 智能体节点
                node_positions[node.agent.agent_id] = {
                    "x": pos.x(),
                    "y": pos.y()
                }
            elif isinstance(node, ConditionNode):
                # 条件分支节点
                node_positions[node.condition_id] = {
                    "x": pos.x(),
                    "y": pos.y()
                }
                # 保存条件配置
                conditions.append({
                    "id": node.condition_id,
                    "text": node.condition_text,
                    "rules": node.conditions
                })
        
        # 构建工作流配置
        workflow_config = {
            "node_positions": node_positions,
            "conditions": conditions
        }
        
        # 保存到配置文件
        app_config.set("workflow", workflow_config)
        app_config.save()
        logger.info("工作流配置保存成功")


class AgentEditDialog(QDialog):
    """智能体编辑对话框
    
    用于编辑智能体节点的详细信息，包括名称、模型、角色描述和权限等。
    """
    
    def __init__(self, agent: Agent, parent=None):
        """初始化智能体编辑对话框
        
        Args:
            agent (Agent): 要编辑的智能体实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.agent = agent
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑智能体")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # 智能体名称
        self.name_input = QLineEdit(self.agent.name)
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        form_layout.addRow("名称:", self.name_input)
        
        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "local-model"])
        self.model_combo.setCurrentText(self.agent.model_id)
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
            }
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        form_layout.addRow("模型:", self.model_combo)
        
        # 角色描述
        self.role_input = QTextEdit(self.agent.role_description)
        self.role_input.setMinimumHeight(100)
        self.role_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        form_layout.addRow("角色描述:", self.role_input)
        
        # 权限选择
        permissions_group = QGroupBox("权限")
        perm_layout = QVBoxLayout(permissions_group)
        
        self.can_speak_check = QCheckBox("可以发言")
        self.can_speak_check.setChecked(AgentPermission.CAN_SPEAK in self.agent.permissions)
        self.can_speak_check.setStyleSheet("""
            QCheckBox {
                margin: 8px 0;
            }
        """)
        perm_layout.addWidget(self.can_speak_check)
        
        self.can_listen_check = QCheckBox("可以监听")
        self.can_listen_check.setChecked(AgentPermission.CAN_LISTEN in self.agent.permissions)
        self.can_listen_check.setStyleSheet("""
            QCheckBox {
                margin: 8px 0;
            }
        """)
        perm_layout.addWidget(self.can_listen_check)
        
        self.can_vote_check = QCheckBox("可以投票")
        self.can_vote_check.setChecked(AgentPermission.CAN_VOTE in self.agent.permissions)
        self.can_vote_check.setStyleSheet("""
            QCheckBox {
                margin: 8px 0;
            }
        """)
        perm_layout.addWidget(self.can_vote_check)
        
        layout.addWidget(permissions_group)
        
        # 按钮框
        button_box = QDialogButtonBox()
        button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def accept(self):
        """接受对话框并保存编辑"""
        # 更新智能体信息
        self.agent.name = self.name_input.text()
        self.agent.model_id = self.model_combo.currentText()
        self.agent.role_description = self.role_input.toPlainText()
        
        # 更新权限
        permissions = []
        if self.can_speak_check.isChecked():
            permissions.append(AgentPermission.CAN_SPEAK)
        if self.can_listen_check.isChecked():
            permissions.append(AgentPermission.CAN_LISTEN)
        if self.can_vote_check.isChecked():
            permissions.append(AgentPermission.CAN_VOTE)
        self.agent.permissions = permissions
        
        super().accept()


class ConditionEditDialog(QDialog):
    """条件分支编辑对话框
    
    用于编辑条件分支节点的详细信息，包括条件文本和条件规则。
    """
    
    def __init__(self, condition_node: ConditionNode, workflow_manager, parent=None):
        """初始化条件分支编辑对话框
        
        Args:
            condition_node (ConditionNode): 要编辑的条件分支节点
            workflow_manager: 工作流管理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.condition_node = condition_node
        self.workflow_manager = workflow_manager
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑条件分支")
        self.setMinimumWidth(600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 条件文本描述
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.condition_text = QLineEdit(self.condition_node.condition_text)
        self.condition_text.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
        """)
        form_layout.addRow("条件描述:", self.condition_text)
        layout.addLayout(form_layout)
        
        # 条件规则列表
        self.conditions_group = QGroupBox("条件规则")
        conditions_layout = QVBoxLayout(self.conditions_group)
        
        # 条件规则表单
        self.condition_input = QLineEdit()
        self.condition_input.setPlaceholderText("输入条件表达式")
        self.condition_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        conditions_layout.addWidget(self.condition_input)
        
        # 下一个智能体选择
        self.next_agent_combo = QComboBox()
        agents = self.workflow_manager.get_agents()
        for agent in agents.values():
            self.next_agent_combo.addItem(agent.name, agent.agent_id)
        self.next_agent_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        conditions_layout.addWidget(self.next_agent_combo)
        
        # 添加条件按钮
        add_condition_btn = QPushButton("添加条件")
        add_condition_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                margin-top: 8px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        add_condition_btn.clicked.connect(self._add_condition)
        conditions_layout.addWidget(add_condition_btn)
        
        layout.addWidget(self.conditions_group)
        
        # 按钮框
        button_box = QDialogButtonBox()
        button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def _add_condition(self):
        """添加条件规则"""
        condition = self.condition_input.text()
        next_agent_id = self.next_agent_combo.currentData()
        
        if condition and next_agent_id:
            # 添加条件
            self.condition_node.add_condition({
                "condition": condition,
                "next_agent_id": next_agent_id
            })
            
            # 清空输入
            self.condition_input.clear()
    
    def accept(self):
        """接受对话框并保存编辑"""
        # 更新条件文本
        self.condition_node.update_condition_text(self.condition_text.text())
        
        super().accept()


class WorkflowEditor(QDialog):
    """讨论流程设计界面"""
    
    def __init__(self, workflow_manager, parent=None):
        """初始化讨论流程设计界面
        
        Args:
            workflow_manager: 工作流管理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.workflow_manager = workflow_manager
        
        self.setWindowTitle("讨论流程设计")
        self.setMinimumSize(900, 700)
        self.resize(1100, 800)
        
        self._init_ui()
        logger.info("讨论流程设计界面初始化完成")
    
    def _init_ui(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建顶部标题栏
        self._create_title_bar(layout)
        
        # 创建主内容区域
        main_content = QWidget()
        main_layout = QHBoxLayout(main_content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建左侧面板
        self._create_left_panel(main_layout)
        
        # 创建流程图视图
        self._create_workflow_view(main_layout)
        
        layout.addWidget(main_content)
        
        # 创建底部按钮区域
        self._create_bottom_buttons(layout)
    
    def _create_title_bar(self, parent_layout):
        """创建顶部标题栏"""
        title_bar = QFrame()
        title_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e9ecef;
                padding: 16px 20px;
            }
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("讨论流程设计")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #212529;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 工具栏按钮
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)
        
        # 添加智能体按钮
        add_button = QPushButton("添加智能体")
        add_button.setFont(QFont("Arial", 14, QFont.Medium))
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        toolbar_layout.addWidget(add_button)
        
        # 保存流程按钮
        save_button = QPushButton("保存流程")
        save_button.setFont(QFont("Arial", 14, QFont.Medium))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_button.clicked.connect(self._save_workflow)
        toolbar_layout.addWidget(save_button)
        
        layout.addLayout(toolbar_layout)
        
        parent_layout.addWidget(title_bar)
    
    def _create_left_panel(self, parent_layout):
        """创建左侧面板"""
        left_panel = QFrame()
        left_panel.setFixedWidth(240)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 1px solid #e9ecef;
            }
        """)
        
        layout = QVBoxLayout(left_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("智能体列表")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #212529;")
        layout.addWidget(title_label)
        
        # 智能体列表
        self.agent_list = QListWidget()
        self.agent_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 4px;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        layout.addWidget(self.agent_list)
        
        # 加载智能体列表
        self._load_agent_list()
        
        parent_layout.addWidget(left_panel)
    
    def _create_workflow_view(self, parent_layout):
        """创建流程图视图"""
        view_container = QWidget()
        view_layout = QVBoxLayout(view_container)
        view_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建图形视图
        self.view = QGraphicsView()
        self.view.setScene(WorkflowScene(self.workflow_manager))
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setStyleSheet("""
            QGraphicsView {
                background-color: #f5f5f5;
                border: none;
            }
        """)
        view_layout.addWidget(self.view)
        
        parent_layout.addWidget(view_container)
    
    def _create_bottom_buttons(self, parent_layout):
        """创建底部按钮区域"""
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
        cancel_button.setFont(QFont("Arial", 14, QFont.Medium))
        cancel_button.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                color: #495057;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.setFont(QFont("Arial", 14, QFont.Medium))
        ok_button.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                border: none;
                border-radius: 8px;
                background-color: #007bff;
                color: white;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        parent_layout.addWidget(button_container)
    
    def _load_agent_list(self):
        """加载智能体列表"""
        self.agent_list.clear()
        agents = self.workflow_manager.get_agents()
        for agent in agents.values():
            item = QListWidgetItem(agent.name)
            item.setData(Qt.UserRole, agent.agent_id)
            self.agent_list.addItem(item)
    
    def _save_workflow(self):
        """保存工作流配置"""
        # 调用场景的保存方法
        self.view.scene().save_workflow()
        logger.info("保存讨论流程配置")
    
    def accept(self):
        """接受对话框"""
        self._save_workflow()
        super().accept()
