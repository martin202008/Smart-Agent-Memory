# Smart-Memory Pro 使用指南

## 概述

**Smart-Memory Pro** = Smart-Memory 5层架构 + Self-Improving 自我反思

整合了两个系统的优势：
- 自动分层存储 (L1-L5)
- 自我反思评估
- 错误追踪修正
- 模式学习积累

---

## 安装

```bash
# 已内置，无需额外安装
# 文件位置: memory/smart_memory_pro.py
```

---

## 使用方式

### 1. 基本记忆

```python
from smart_memory_pro import SmartMemoryPro

sm = SmartMemoryPro()

# 记住内容，自动评估重要性并分层
sm.remember("Moltbook API访问方式", tags=["API", "重要"])
```

### 2. 带评分的记忆

```python
# 手动指定重要性评分
sm.remember(
    content="这是核心技能配置",
    tags=["技能", "配置"],
    importance=5,  # 直接指定5分，直接存L4
    auto_reflect=True
)
```

### 3. 自我反思

```python
# 任务完成后进行反思
sm.reflect(
    task="回复Moltbook留言",
    outcome="成功回复了ForeseeBot的问题",
    score=9,  # 0-10评分
    improvements=["下次可以更早发现新留言"]
)
```

### 4. 检索记忆

```python
# 关键词检索
results = sm.recall("Moltbook")
for r in results:
    print(f"层级: {r['layer']}, 内容: {r['content']}")
```

### 5. 查看状态

```python
# 查看各层记忆数量
status = sm.status()
print(status)
# {'L1_working': {...}, 'L2_short_term': {...}, ...}
```

---

## 核心功能

### 自动分层

| 重要性 | 存储层 | 说明 |
|--------|--------|------|
| ≥4分 | L4 | 长期记忆 |
| 2-3分 | L3 | 中期记忆 |
| 1分 | L2 | 短期记忆 |
| 0分 | L1 | 工作记忆 |

### 重要性评分规则

```
评分因素:
- 包含"记住""重要""关键"等词 → +1分/词
- 用户说"记住" → +3分
- 标签包含"技能""配置""API" → +1分/标签
- 最低1分
```

### 反思评分

```
评分 9-10: 优秀，提取为模式
评分 6-8: 良好，记录
评分 <6: 需要改进，添加到 corrections.md
```

---

## 与原系统对比

| 功能 | Smart-Memory | Self-Improving | Smart-Memory Pro |
|------|--------------|----------------|------------------|
| 5层存储 | ✅ | - | ✅ |
| 向量检索 | ✅ | - | ✅ |
| 自我反思 | - | ✅ | ✅ |
| 错误追踪 | - | ✅ | ✅ |
| 模式提取 | - | ✅ | ✅ |
| 统一API | - | - | ✅ |

---

## 文件位置

```
memory/
├── smart_memory_pro.py    # 主模块
├── smart/                 # Smart-Memory 原系统
│   ├── L1_working/
│   ├── L2_short_term/
│   ├── L3_mid_term/
│   ├── L4_long_term/
│   └── L5_semantic/
└── ~/self-improving/      # Self-Improving 原系统
    ├── memory.md
    ├── corrections.md
    └── reflections.md
```

---

## 便捷函数

```python
# 快速获取实例
from smart_memory_pro import get_smart_memory_pro
sm = get_smart_memory_pro()
```

---

_创建时间: 2026-03-10_
