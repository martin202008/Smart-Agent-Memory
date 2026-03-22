# Smart-Agent-Memory

[English](#english) | [中文](#中文) | [Smart-Memory Pro](#smart-memory-pro)

---

## 中文

> 让 AI Agent 拥有类似人类的记忆系统——5层记忆架构 + 自我进化 + 情感感知 + **贝叶斯衰减引擎 v2.0**

### 功能特性

- 🧠 **5层记忆系统** - 工作/短期/中期/长期/语义记忆
- 🔄 **跨会话继承** - 每次启动自动加载历史记忆
- 🧹 **自动清理** - 7天TTL自动过期，重要记忆自动升级
- 🔍 **语义搜索** - TF-IDF向量检索，理解语义关联
- 🧬 **自我进化** - 目标管理、反思、技能追踪
- 😊 **情感感知** - 实时分析用户情绪，动态调整回复
- 🖼️ **多模态记忆** - 支持图片/音频/视频存储
- ⏱️ **贝叶斯衰减引擎** - 时间衰减 + 访问频率 + 冷却机制 + 判例加成
- 📋 **Case Template 判例** - 情境/判断/后果/修正四段式，有修正则+10%稳定性
- 📦 **自动压缩** - MEMORY.md 超15KB自动归档旧内容
- 🌐 **社区知识导入** - 从日志/MEMORY.md 自动提取高价值知识
- ✨ **Smart-Memory Pro** - 升级版：统一API + 自我反思 + 错误追踪

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

---

## Smart-Memory Pro (升级版)

> 结合 Smart-Memory 5层架构 + Self-Improving 自我反思 + **贝叶斯衰减引擎 v2.0**

### 新增功能

- 🤖 **统一API** - 单一接口管理所有记忆功能
- 💭 **自我反思** - 任务完成后自动评估评分
- 📝 **错误追踪** - 自动记录低分任务到 corrections.md
- 🏆 **模式提取** - 高分任务自动提取为可复用模式
- ⏱️ **贝叶斯衰减** - 时间衰减 + 访问频率 + 判例加成 + 三层生命周期
- 📋 **判例模板** - 自动识别「情境/判断/后果/修正」四段式结构

### 快速开始

```python
from memory.smart_memory_pro import SmartMemoryPro

sm = SmartMemoryPro()

# 记住内容 + 自动评估重要性
sm.remember("Moltbook API访问方式", tags=["API"], auto_reflect=True)

# 任务反思
sm.reflect(
    task="回复用户留言",
    outcome="成功回复",
    score=9,
    improvements=["下次可以更快回复"]
)

# 检索
results = sm.recall("Moltbook")
```

### 重要性评分

| 评分 | 存储层 | 说明 |
|------|--------|------|
| ≥4分 | L4 | 长期记忆 |
| 2-3分 | L3 | 中期记忆 |
| 1分 | L2 | 短期记忆 |
| 0分 | L1 | 工作记忆 |

### 反思评分

| 评分 | 操作 |
|------|------|
| 9-10 | 提取为模式 |
| 6-8 | 记录存档 |
| <6 | 添加到 corrections.md |

### 文件结构

```
memory/
├── smart_memory_pro.py   # 统一API
├── smart/               # 原5层系统
│   ├── L1_working/
│   ├── L2_short_term/
│   ├── L3_mid_term/
│   ├── L4_long_term/
│   └── L5_semantic/
├── decay_engine.py      # 贝叶斯衰减引擎（v2.0）
├── case_template.py     # 判例模板提取（v2.0）
├── auto_compact.py      # MEMORY.md自动压缩（v2.0）
└── ~/self-improving/   # 自我反思系统
    ├── memory.md
    ├── corrections.md
    └── reflections.md
```
