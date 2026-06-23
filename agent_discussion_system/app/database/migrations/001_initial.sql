-- SQLite数据库初始化脚本
-- 创建时间：2026-01-07
-- 版本：1.0.0

-- 创建智能体表
CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    model_id TEXT NOT NULL,
    role_description TEXT NOT NULL,
    permissions TEXT NOT NULL, -- JSON格式存储权限列表
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建讨论表
CREATE TABLE IF NOT EXISTS discussions (
    discussion_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'in_progress', -- in_progress/ended
    current_round INTEGER DEFAULT 1,
    total_rounds INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME
);

-- 创建讨论消息表
CREATE TABLE IF NOT EXISTS discussion_messages (
    message_id TEXT PRIMARY KEY,
    discussion_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    round_number INTEGER NOT NULL DEFAULT 1,
    content TEXT NOT NULL,
    message_type TEXT NOT NULL DEFAULT 'normal', -- normal/system
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discussion_id) REFERENCES discussions(discussion_id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

-- 创建知识库表
CREATE TABLE IF NOT EXISTS knowledge_base (
    doc_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    file_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建知识库向量表
CREATE TABLE IF NOT EXISTS kb_vectors (
    vector_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    vector TEXT NOT NULL, -- JSON格式存储向量数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES knowledge_base(doc_id) ON DELETE CASCADE
);

-- 创建配置表
CREATE TABLE IF NOT EXISTS config (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_discussions_status ON discussions(status);
CREATE INDEX IF NOT EXISTS idx_discussion_messages_discussion_id ON discussion_messages(discussion_id);
CREATE INDEX IF NOT EXISTS idx_discussion_messages_round_number ON discussion_messages(round_number);
CREATE INDEX IF NOT EXISTS idx_kb_vectors_doc_id ON kb_vectors(doc_id);
CREATE INDEX IF NOT EXISTS idx_config_key ON config(key);

-- 插入默认数据
-- 插入默认智能体
INSERT OR IGNORE INTO agents (agent_id, name, model_id, role_description, permissions) VALUES
('agent_1', '专家A', 'gpt-4o-mini', '你是一位领域专家，擅长深入分析问题，提供专业见解', '["CAN_SPEAK", "CAN_START_NEXT_ROUND"]'),
('agent_2', '专家B', 'gpt-4o-mini', '你是一位领域专家，擅长从不同角度思考问题，提供独特视角', '["CAN_SPEAK", "CAN_START_NEXT_ROUND"]'),
('agent_3', '协调者', 'gpt-4o-mini', '你是一位协调者，负责引导讨论方向，总结讨论内容，确保讨论高效进行', '["CAN_SPEAK", "CAN_START_NEXT_ROUND", "CAN_TERMINATE_DISCUSSION"]');

-- 插入默认配置
INSERT OR IGNORE INTO config (key, value) VALUES
('app_version', '1.0.0'),
('default_model', 'gpt-4o-mini'),
('max_rounds', '10'),
('round_timeout', '300'),
('total_timeout', '3600'),
('knowledge_base_enabled', 'true');
