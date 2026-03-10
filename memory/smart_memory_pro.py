#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart-Memory Pro - 升级版记忆系统
================================
结合 Smart-Memory 5层架构 + Self-Improving 自我反思能力

核心功能:
- 自动分层存储 (L1-L5)
- 自我反思评估
- 错误追踪修正
- 模式学习积累
- 统一检索接口

使用方式:
    from smart_memory_pro import SmartMemoryPro
    sm = SmartMemoryPro()
    sm.remember("重要内容", auto_reflect=True)
    sm.recall("关键词")
    sm.reflect("任务完成评估")
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# 路径配置
BASE_DIR = Path(__file__).parent
MEMORY_DIR = BASE_DIR / "smart"
SELF_IMPROVING_DIR = Path(os.path.expanduser("~/self-improving"))

# 确保目录存在
for d in ["L1_working", "L2_short_term", "L3_mid_term/events", "L4_long_term", "L5_semantic"]:
    (MEMORY_DIR / d).mkdir(parents=True, exist_ok=True)


@dataclass
class MemoryItem:
    """记忆条目"""
    id: int
    content: str
    layer: str  # L1/L2/L3/L4/L5
    tags: List[str]
    importance: int  # 0-5
    created_at: str
    accessed_at: str = None
    access_count: int = 0
    reflection: str = None  # 自我反思内容
    source: str = "auto"  # 来源


@dataclass
class Reflection:
    """反思记录"""
    id: int
    task: str  # 任务描述
    outcome: str  # 结果
    score: int  # 0-10 评分
    improvements: List[str]  # 改进建议
    created_at: str


class SmartMemoryPro:
    """
    Smart-Memory Pro 统一记忆管理器
    
    结合了:
    - Smart-Memory 的5层自动分层
    - Self-Improving 的自我反思能力
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.l1_file = MEMORY_DIR / "L1_working" / "session.json"
        self.l2_dir = MEMORY_DIR / "L2_short_term"
        self.l3_dir = MEMORY_DIR / "L3_mid_term" / "events"
        self.l4_file = MEMORY_DIR / "L4_long_term" / "memories.json"
        self.l5_file = MEMORY_DIR / "L5_semantic" / "concepts.json"
        
        # Self-Improving 文件
        self.corrections_file = SELF_IMPROVING_DIR / "corrections.md"
        self.reflections_file = SELF_IMPROVING_DIR / "reflections.md"
        self.memory_file = SELF_IMPROVING_DIR / "memory.md"
        
        # 初始化
        self._init_files()
        
    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = MEMORY_DIR / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "short_term_ttl_days": 7,
            "importance_threshold": 4,
            "auto_reflection": True,
            "correction_sync": True
        }
    
    def _init_files(self):
        """初始化必要文件"""
        # L4 记忆文件
        if not self.l4_file.exists():
            with open(self.l4_file, 'w', encoding='utf-8') as f:
                json.dump({"memories": []}, f, ensure_ascii=False)
        
        # L5 概念文件
        if not self.l5_file.exists():
            with open(self.l5_file, 'w', encoding='utf-8') as f:
                json.dump({"concepts": []}, f, ensure_ascii=False)
    
    # ==================== 核心记忆功能 ====================
    
    def remember(self, content: str, tags: List[str] = None, 
                 auto_reflect: bool = True, importance: int = None) -> Dict:
        """
        记住内容（自动分层存储）
        
        Args:
            content: 记忆内容
            tags: 标签列表
            auto_reflect: 是否自动进行重要性评估
            importance: 重要性评分 (0-5)，如果为None则自动计算
            
        Returns:
            存储结果包含layer信息
        """
        if tags is None:
            tags = []
        
        # 自动计算重要性
        if importance is None:
            importance = self._calc_importance(content, tags)
        
        # 根据重要性决定存储层
        layer = self._choose_layer(importance)
        
        # 创建记忆条目
        item = {
            "id": int(time.time() * 1000),
            "content": content,
            "layer": layer,
            "tags": tags,
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "source": "user_interaction"
        }
        
        # 存储到对应层
        if layer == "L1":
            self._save_l1(item)
        elif layer == "L2":
            self._save_l2(item)
        elif layer == "L3":
            self._save_l3(item)
        else:  # L4/L5
            self._save_l4(item)
        
        # 自我反思（如果开启）
        if auto_reflect and importance >= 3:
            self._auto_reflect(content, importance)
        
        return {
            "success": True,
            "layer": layer,
            "importance": importance,
            "message": f"记住: {content[:50]}... -> {layer}"
        }
    
    def _calc_importance(self, content: str, tags: List[str]) -> int:
        """计算重要性评分"""
        score = 0
        
        # 关键词触发
        important_keywords = ["记住", "重要", "关键", "核心", "喜欢", "讨厌", "技能", "能力", "API", "配置"]
        content_lower = content.lower()
        for kw in important_keywords:
            if kw.lower() in content_lower:
                score += 1
        
        # 用户明确要求
        if "记住" in content:
            score += 3
        
        # 标签权重
        important_tags = ["技能", "配置", "错误", "偏好", "重要", "API"]
        for tag in tags:
            if tag in important_tags:
                score += 1
        
        # 默认至少1分
        return max(score, 1)
    
    def _choose_layer(self, importance: int) -> str:
        """根据重要性选择存储层"""
        if importance >= 4:
            return "L4"  # 长期记忆
        elif importance >= 2:
            return "L3"  # 中期记忆
        elif importance >= 1:
            return " importance >= 1L2"  # 短期记忆
        else:
            return "L1"  # 工作记忆
    
    def _save_l1(self, item: Dict):
        """保存到L1工作记忆"""
        with open(self.l1_file, 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
    
    def _save_l2(self, item: Dict):
        """保存到L2短期记忆"""
        date = datetime.now().strftime("%Y-%m-%d")
        file = self.l2_dir / f"{date}.json"
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
    
    def _save_l3(self, item: Dict):
        """保存到L3中期记忆"""
        date = datetime.now().strftime("%Y-%m-%d")
        file = self.l3_dir / f"{date}.json"
        
        if file.exists():
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"events": [], "date": date}
        
        data["events"].append(item)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_l4(self, item: Dict):
        """保存到L4长期记忆"""
        with open(self.l4_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        memories = data.get("memories", [])
        
        # 检查重复
        if not any(m.get("content", "")[:50] == item["content"][:50] for m in memories):
            item["id"] = len(memories) + 1
            memories.append(item)
            data["memories"] = memories
            
            with open(self.l4_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ==================== 自我反思功能 ====================
    
    def reflect(self, task: str, outcome: str, score: int = None,
                improvements: List[str] = None) -> Dict:
        """
        记录反思
        
        Args:
            task: 任务描述
            outcome: 执行结果
            score: 评分 0-10
            improvements: 改进建议列表
            
        Returns:
            反思记录
        """
        if score is None:
            score = 5
        if improvements is None:
            improvements = []
        
        reflection = {
            "id": int(time.time() * 1000),
            "task": task,
            "outcome": outcome,
            "score": score,
            "improvements": improvements,
            "created_at": datetime.now().isoformat()
        }
        
        # 保存到 reflections.md
        self._save_reflection(reflection)
        
        # 如果评分低，记录到 corrections
        if score < 6:
            self._log_correction(task, outcome, score)
        
        # 提取模式（评分高时）
        if score >= 8 and improvements:
            self._extract_pattern(task, improvements)
        
        return {
            "success": True,
            "reflection": reflection,
            "message": f"反思已记录，评分: {score}/10"
        }
    
    def _save_reflection(self, reflection: Dict):
        """保存反思到文件"""
        SELF_IMPROVING_DIR.mkdir(parents=True, exist_ok=True)
        
        content = f"""
## 反思 {reflection['id']}
- **任务**: {reflection['task']}
- **结果**: {reflection['outcome']}
- **评分**: {reflection['score']}/10
- **改进**: {', '.join(reflection['improvements']) if reflection['improvements'] else '无'}
- **时间**: {reflection['created_at']}
"""
        
        with open(self.reflections_file, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _log_correction(self, task: str, outcome: str, score: int):
        """记录错误/低分到 corrections.md"""
        content = f"""
## 修正 {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **任务**: {task}
- **结果**: {outcome}
- **评分**: {score}/10
"""
        
        with open(self.corrections_file, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _extract_pattern(self, task: str, improvements: List[str]):
        """提取模式到 memory.md"""
        content = f"""
### {task[:50]}
- 评分高，已提取为模式
- 改进: {', '.join(improvements)}
"""
        
        with open(self.memory_file, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _auto_reflect(self, content: str, importance: int):
        """自动触发小规模反思"""
        # 对于重要内容，简单评估
        if importance >= 4:
            # 可以扩展为更复杂的自动评估
            pass
    
    # ==================== 检索功能 ====================
    
    def recall(self, query: str) -> List[Dict]:
        """
        检索记忆
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的记忆列表
        """
        results = []
        
        # 搜索 L4 长期记忆
        with open(self.l4_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for m in data.get("memories", []):
                if query in m.get("content", "") or any(query in t for t in m.get("tags", [])):
                    m["layer"] = "L4"
                    results.append(m)
        
        # 搜索 L2 短期记忆
        for f in self.l2_dir.glob("*.json"):
            with open(f, 'r', encoding='utf-8') as fp:
                try:
                    data = json.load(fp)
                    if query in str(data):
                        data["layer"] = "L2"
                        results.append(data)
                except:
                    pass
        
        # 搜索 L3 中期记忆
        for f in self.l3_dir.glob("*.json"):
            with open(f, 'r', encoding='utf-8') as fp:
                try:
                    data = json.load(fp)
                    for event in data.get("events", []):
                        if query in event.get("content", ""):
                            event["layer"] = "L3"
                            results.append(event)
                except:
                    pass
        
        return results[:10]  # 返回前10条
    
    # ==================== 状态查询 ====================
    
    def status(self) -> Dict:
        """查看记忆状态"""
        # L1
        l1_size = 0
        if self.l1_file.exists():
            l1_size = self.l1_file.stat().st_size
        
        # L2
        l2_count = len(list(self.l2_dir.glob("*.json")))
        
        # L3
        l3_count = 0
        for f in self.l3_dir.glob("*.json"):
            with open(f, 'r', encoding='utf-8') as fp:
                try:
                    data = json.load(fp)
                    l3_count += len(data.get("events", []))
                except:
                    pass
        
        # L4
        l4_count = 0
        with open(self.l4_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            l4_count = len(data.get("memories", []))
        
        return {
            "L1_working": {"size_bytes": l1_size},
            "L2_short_term": {"files": l2_count},
            "L3_mid_term": {"events": l3_count},
            "L4_long_term": {"memories": l4_count},
            "corrections_file": self.corrections_file.exists(),
            "reflections_file": self.reflections_file.exists()
        }


# 便捷函数
_pro_instance = None

def get_smart_memory_pro() -> SmartMemoryPro:
    """获取全局实例"""
    global _pro_instance
    if _pro_instance is None:
        _pro_instance = SmartMemoryPro()
    return _pro_instance


if __name__ == "__main__":
    # 测试
    sm = SmartMemoryPro()
    
    # 测试记住
    print("=== 测试记住功能 ===")
    result = sm.remember("Moltbook API访问：Agent ID用于认证，Author ID用于发帖", 
                        tags=["Moltbook", "API"], auto_reflect=True)
    print(result)
    
    # 测试反思
    print("\n=== 测试反思功能 ===")
    result = sm.reflect(
        task="回复Moltbook留言",
        outcome="成功回复了ForeseeBot的问题",
        score=9,
        improvements=["下次可以更早发现新留言"]
    )
    print(result)
    
    # 测试检索
    print("\n=== 测试检索 ===")
    results = sm.recall("Moltbook")
    print(f"找到 {len(results)} 条记忆")
    
    # 状态
    print("\n=== 记忆状态 ===")
    print(sm.status())
