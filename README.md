<h1 align="center">🧠 OpenAgents</h1>

<p align="center">
  <strong>Multi-Agent Discussion System</strong> — AI-powered collaborative reasoning desktop app
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-Qt-41CD52?logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/OpenAI-API-412991?logo=openai" alt="OpenAI">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

---

## 📖 Overview

A local desktop application that simulates multi-agent round-table discussions. Input a topic, and multiple AI agents debate, critique, and refine ideas — similar to a human panel discussion — until consensus or termination conditions are met.

## ✨ Features

### 🤖 Multi-Agent Discussion
- Create multiple AI agents with distinct roles and personalities
- Round-robin discussion with configurable order
- Control-string based flow management (NEXT_ROUND / END_DISCUSSION)

### 📚 Local Knowledge Base
- Upload local documents for context
- TF-IDF vector indexing for RAG retrieval
- Knowledge-grounded agent responses

### 🔌 Plugin System
- Built-in tools: file reader, calculator
- User-defined custom tools
- Extensible MCP-like architecture

### 🎨 PySide6 Desktop UI
- Chat history with agent avatars
- Real-time discussion status panel
- Visual workflow editor for discussion flow design
- Multi-session management

## 🚀 Quick Start

```bash
cd agent_discussion_system
pip install -r requirements.txt
python main.py
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| GUI | PySide6 (Qt for Python) |
| LLM | OpenAI-compatible API |
| Knowledge Base | TF-IDF + scikit-learn |
| Concurrency | QThread / QThreadPool |
| Config | JSON-based |

## 📝 License

MIT
