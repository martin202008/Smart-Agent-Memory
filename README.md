# Smart-Agent-Memory

[English](#english) | [中文](#中文)

---

## 中文

> 让 AI Agent 拥有类似人类的记忆系统——5层记忆架构 + 自我进化 + 情感感知

### 功能特性

- 🧠 **5层记忆系统** - 工作/短期/中期/长期/语义记忆
- 🔄 **跨会话继承** - 每次启动自动加载历史记忆
- 🧹 **自动清理** - 7天TTL自动过期，重要记忆自动升级
- 🔍 **语义搜索** - TF-IDF向量检索，理解语义关联
- 🧬 **自我进化** - 目标管理、反思、技能追踪
- 😊 **情感感知** - 实时分析用户情绪，动态调整回复
- 🖼️ **多模态记忆** - 支持图片/音频/视频存储

### 快速开始

```python
from memory.smart import init_smart_memory, remember, semantic_search

# 初始化（会自动加载历史记忆）
init_smart_memory()

# 记住重要内容
remember("用户喜欢简洁的蓝色PPT风格")

# 语义搜索
results = semantic_search("用户的配色偏好")
# 返回: [{'content': '...', 'relevance_score': 0.51}]
```

### 5层记忆架构

```
┌─────────────────────────────────────────┐
│           Smart-Agent-Memory             │
├─────────────────────────────────────────┤
│ L1 工作记忆   │ 当前会话上下文           │
│ L2 短期记忆  │ 7天自动过期 (TTL)       │
│ L3 中期记忆  │ 重要性评分触发          │
│ L4 长期记忆  │ 语义向量检索            │
│ L5 语义记忆  │ 概念关系图谱           │
└─────────────────────────────────────────┘
```

### 安装

```bash
git clone https://github.com/martin202008/Smart-Agent-Memory.git
```

### 目录结构

```
Smart-Agent-Memory/
├── memory/
│   ├── __init__.py          # 统一入口
│   ├── memory_manager.py    # 5层记忆
│   ├── evolution_manager.py # 自我进化
│   ├── vector_search.py    # 语义搜索
│   ├── session_initializer.py # 跨会话
│   ├── cleanup.py          # 自动清理
│   ├── emotion.py         # 情感感知
│   └── multimodal/        # 多媒体
└── examples/
    └── demo.py           # 示例
```

### API 概览

| 模块 | 函数 | 说明 |
|------|------|------|
| 记忆 | `remember()` | 记忆内容 |
| 搜索 | `semantic_search()` | 语义搜索 |
| 进化 | `reflect()`, `evolve()` | 自我进化 |
| 情感 | `analyze_emotion()` | 情感分析 |
| 存储 | `cleanup()`, `get_storage_stats()` | 管理 |

### 许可证

MIT License

---

## English

> Give your AI Agent a human-like memory system - 5-layer memory + self-evolution + emotion sensing

### Features

- 🧠 **5-Layer Memory** - Working/Short/Medium/Long-term/Semantic
- 🔄 **Session Inheritance** - Auto-load history on startup
- 🧹 **Auto Cleanup** - 7-day TTL, auto-promote important memories
- 🔍 **Semantic Search** - TF-IDF vector search
- 🧬 **Self-Evolution** - Goals, reflection, skill tracking
- 😊 **Emotion Sensing** - Real-time emotion analysis
- 🖼️ **Multimodal** - Image/Audio/Video storage

### Quick Start

```python
from memory.smart import init_smart_memory, remember, semantic_search

init_smart_memory()
remember("User prefers blue color scheme")
results = semantic_search("user color preference")
```

### License

MIT License
