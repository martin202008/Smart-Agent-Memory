# Smart-Agent-Memory

> 让 AI Agent 拥有类似人类的记忆系统——5层记忆架构 + 自我进化 + 情感感知

## 功能特性

- 🧠 **5层记忆系统** - 工作/短期/中期/长期/语义记忆
- 🔄 **跨会话继承** - 每次启动自动加载历史记忆
- 🧹 **自动清理** - 7天TTL自动过期，重要记忆自动升级
- 🔍 **语义搜索** - TF-IDF向量检索，理解语义关联
- 🧬 **自我进化** - 目标管理、反思、技能追踪
- 😊 **情感感知** - 实时分析用户情绪，动态调整回复
- 🖼️ **多模态记忆** - 支持图片/音频/视频存储

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/martin202008/Smart-Agent-Memory.git
cd Smart-Agent-Memory

# 或将 memory/ 目录复制到你的 AI Agent workspace
```

### 基本使用

```python
from memory.smart import init_smart_memory, remember, recall, semantic_search

# 初始化（会自动加载历史记忆）
init_smart_memory()

# 记住重要内容
remember("用户喜欢简洁的蓝色PPT风格")
remember("用户的邮箱是 test@example.com", force_long_term=True)

# 搜索记忆
results = semantic_search("用户的配色偏好")
# 返回: [{'content': '...', 'relevance_score': 0.51}]

# 情感分析
from memory.smart import analyze_emotion, adapt_response
emotion = analyze_emotion("太棒了！你做得真好！")
# → {'emotion': 'excited', 'score': 1.5, 'keywords': ['太棒了']}

# 自我进化
from memory.smart import reflect, evolve
reflect("今天完成了XXX任务")
print(evolve())
```

## 5层记忆架构

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

### L1 - 工作记忆
当前会话的实时上下文，会话结束时自动清除。

### L2 - 短期记忆
最近7天的对话历史，到期自动删除。可配置TTL。

### L3 - 中期记忆
重要性评分 ≥5分 的记忆自动从 L2 升级。

### L4 - 长期记忆
持久化存储，支持语义向量搜索。

### L5 - 语义记忆
概念和关系图谱，支持知识推理。

## 核心 API

### 记忆系统

| 函数 | 说明 |
|------|------|
| `init_smart_memory()` | 初始化全部系统 |
| `remember(content, context)` | 记忆内容（自动评分） |
| `recall(query)` | 统一回忆入口 |
| `semantic_search(query, top_k)` | 语义搜索 |

### 进化系统

| 函数 | 说明 |
|------|------|
| `reflect(context)` | 自我反思 |
| `evolve()` | 生成进化报告 |
| `get_evolution_manager()` | 获取进化管理器 |

### 情感系统

| 函数 | 说明 |
|------|------|
| `analyze_emotion(text)` | 分析情感 |
| `adapt_response(response, emotion)` | 调整回复风格 |
| `get_tone_suggestion(emotion)` | 获取语气建议 |

### 存储管理

| 函数 | 说明 |
|------|------|
| `cleanup(dry_run)` | 清理过期记忆 |
| `get_storage_stats()` | 获取存储统计 |
| `add_image(path, desc, tags)` | 添加图片 |

## 配置

配置文件: `memory/smart/config.json`

```json
{
  "short_term_ttl_days": 7,
  "importance_threshold": 5,
  "emotion_weights": {
    "positive_excitement": 1.5,
    "negative_frustration": 1.3
  }
}
```

## 重要性评分规则

自动触发升级的条件：

| 关键词 | 分数 |
|--------|------|
| "记住" | +5 |
| "喜欢"/"讨厌" | +3 |
| "重要" | +4 |
| "不要忘记" | +5 |
| "以后都用" | +4 |

## 情感类型

| 类型 | 关键词 | 分数 |
|------|--------|------|
| excited | 太棒了、哇 | +1.5 |
| positive | 好、赞 | +1.0 |
| neutral | (无) | 0 |
| negative | 差、慢 | -1.0 |
| frustrated | 气、无语 | -1.5 |

## 目录结构

```
Smart-Agent-Memory/
├── SKILL.md                 # 技能定义
├── README.md                 # 本文档
├── LICENSE                  # MIT 许可证
├── memory/
│   ├── __init__.py          # 统一入口
│   ├── memory_manager.py    # 5层记忆
│   ├── evolution_manager.py # 自我进化
│   ├── vector_search.py    # 语义搜索
│   ├── session_initializer.py # 跨会话
│   ├── cleanup.py          # 自动清理
│   ├── emotion.py         # 情感感知
│   ├── config.json         # 配置
│   ├── L1_working/       # L1 数据
│   ├── L2_short_term/    # L2 数据
│   ├── L3_mid_term/      # L3 数据
│   ├── L4_long_term/     # L4 数据
│   ├── L5_semantic/      # L5 数据
│   └── multimodal/        # 多媒体
└── examples/
    └── demo.py           # 示例代码
```

## 依赖

```
pip install chromadb  # 可选，向量搜索增强
```

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

MIT License - see LICENSE file
