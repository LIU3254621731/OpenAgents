# 多智能体讨论系统 Beta 版

## 📖 项目介绍

多智能体讨论系统是一个本地运行的桌面客户端，用于展示多模型、多角色AI协作讨论的能力。用户只需输入讨论主题和需求，系统即可驱动多个AI智能体像人类圆桌会议一样进行讨论、互相批判与补充，并在满足规则后自动终止讨论并输出结果。

## 🎯 功能特性

### 核心功能
- **多智能体协作讨论**：支持多个AI智能体按固定顺序进行讨论
- **轮次驱动机制**：每一轮中，多个Agent按流程顺序依次发言
- **控制字符串规则**：通过固定控制字符串（"NEXT_ROUND"、"END_DISCUSSION"）控制讨论流程
- **多种终止条件**：支持控制字符串触发终止、最大轮次限制、单轮/总时长超时、用户手动终止
- **本地知识库支持**：可上传本地文件，构建向量索引，用于RAG检索
- **插件化工具系统**：支持内置工具（文件读取、简单计算）和用户自定义工具

### 界面功能
- **软件图标与主窗口**：简洁美观的桌面应用界面
- **新建聊天**：支持创建多个讨论会话
- **聊天历史列表**：方便切换和管理历史讨论
- **主聊天窗口**：清晰展示多智能体对话流
- **多功能输入区**：支持输入讨论主题和需求
- **右侧讨论状态与流程控制区**：实时显示讨论状态、轮次信息和控制按钮
- **讨论流程设计界面**：可视化配置讨论流程，形式类似思维导图/流程图

## 🏗️ 技术栈

- **开发语言**：Python 3.10+
- **GUI框架**：Qt（PySide6）
- **并发模型**：QThread / QThreadPool
- **网络请求**：httpx
- **本地存储**：JSON
- **向量索引**：scikit-learn（TF-IDF）
- **API Key加密**：cryptography
- **日志记录**：Python标准库logging

## 🚀 安装说明

### 1. 克隆项目

```bash
git clone <repository-url>
cd agent_discussion_system
```

### 2. 安装依赖

使用pip安装项目依赖：

```bash
pip install -r requirements.txt
```

## ⚙️ 配置指南

### 1. 配置API Key

复制示例配置文件并修改API Key：

```bash
cp config/config.json.example config/config.json
```

编辑`config/config.json`文件，将`model.api_key`字段替换为您的OpenAI API Key：

```json
{
  "model": {
    "api_key": "sk-your-api-key-here"
  }
}
```

### 2. 其他配置项

- `app`：应用基本配置（版本、语言、主题）
- `model`：模型配置（默认模型、API基础URL、超时时间）
- `discussion`：讨论配置（最大轮次、每轮最大时间、总最大时间）
- `knowledge_base`：知识库配置（是否启用、向量索引路径）
- `mcp`：工具系统配置（是否启用、超时时间）

## 📱 使用方法

### 1. 启动应用

```bash
python main.py
```

### 2. 创建讨论

1. 在输入框中输入讨论主题和需求
2. 点击"开始讨论"按钮
3. 观察智能体之间的讨论过程
4. 讨论结束后查看总结结果

### 3. 管理讨论流程

- **暂停/恢复讨论**：点击"暂停讨论"/"恢复讨论"按钮
- **终止讨论**：点击"终止讨论"按钮
- **编辑讨论流程**：点击"编辑讨论流程"按钮，在弹出的界面中配置智能体和讨论顺序

### 4. 使用知识库

- 在设置中启用知识库
- 上传本地文件到知识库
- 智能体在讨论过程中会自动检索相关知识

## 📁 项目结构

```
agent_discussion_system/
├── app/                     # 主应用模块
│   ├── ui/                  # UI组件
│   │   ├── main_window.py    # 主窗口
│   │   ├── chat_widget.py    # 聊天对话流
│   │   ├── input_widget.py   # 多功能输入区
│   │   ├── status_panel.py   # 讨论状态与流程控制
│   │   └── workflow_editor.py # 讨论流程设计界面
│   ├── core/                # 核心逻辑
│   │   ├── agent.py          # 智能体类
│   │   ├── discussion_engine.py # 讨论引擎
│   │   └── workflow_manager.py # 讨论流程管理
│   ├── models/              # AI模型接入
│   │   ├── model_adapter.py   # 模型适配器基类
│   │   ├── openai_model.py    # OpenAI API接入
│   │   └── local_model.py     # 本地模型接入
│   ├── utils/               # 工具函数
│   │   ├── logger.py         # 日志记录
│   │   ├── json_handler.py    # JSON文件读写
│   │   └── encryption.py      # API Key加密
│   ├── config/              # 配置管理
│   │   └── app_config.py      # 应用配置
│   ├── mcp/                 # 插件化工具系统
│   │   ├── mcp_base.py        # 工具基类
│   │   ├── mcp_manager.py     # 工具管理
│   │   ├── file_mcp.py        # 文件读取工具
│   │   └── calculator_mcp.py  # 计算器工具
│   └── knowledge_base/      # 本地知识库
│       ├── knowledge_base.py  # 知识库管理
│       └── vector_store.py    # 向量索引实现
├── assets/                  # 资源文件
├── config/                  # 配置文件
│   ├── config.json.example   # 示例配置文件
│   └── config.json           # 实际配置文件（需用户创建）
├── logs/                    # 日志文件
├── main.py                  # 主启动脚本
├── requirements.txt         # 依赖列表
└── README.md               # 项目文档
```

## 🛠️ 开发说明

### 开发环境要求
- Python 3.10+
- PySide6 6.6.2+
- 其他依赖见requirements.txt

### 代码规范
- 严格遵循PEP 8编码规范
- 所有核心类和复杂逻辑必须写清晰中文注释，说明"为什么这么设计"
- UI与核心逻辑严格解耦
- 所有AI/MCP调用必须在后台线程执行
- UI仅通过signal/slot更新
- 所有用户输入需基础校验
- API Key不得出现在日志或UI中
- MCP执行需设置超时与异常保护

### 项目扩展

#### 添加新的AI模型
1. 继承`ModelAdapter`类
2. 实现`generate`、`get_model_info`、`list_models`方法
3. 在主应用中注册新模型

#### 添加新的MCP工具
1. 继承`MCPBase`类
2. 实现`execute`方法
3. 在MCPManager中注册新工具

#### 扩展UI组件
1. 继承相应的Qt Widget类
2. 实现所需功能
3. 在主窗口中集成

## 📄 许可证信息

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request，共同改进这个多智能体讨论系统！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues：<repository-url>/issues

## 📌 版本说明

### Beta 0.1.0
- 实现了多智能体讨论核心功能
- 支持OpenAI API接入
- 支持本地模型接入
- 实现了基本的UI界面
- 支持本地知识库
- 支持插件化工具系统

## 📝 待办事项

- [ ] 支持更多AI模型
- [ ] 优化讨论流程设计界面
- [ ] 增强知识库功能
- [ ] 支持更多MCP工具
- [ ] 优化UI界面和交互体验
- [ ] 添加单元测试
- [ ] 支持深色主题
- [ ] 支持导出讨论结果
