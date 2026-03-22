#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis 跨会话记忆继承系统
让 Jarvis 启动时自动加载历史记忆
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 基础路径
SMART_DIR = Path(__file__).parent


class SessionInitializer:
    """会话初始化器 - 跨会话记忆继承"""
    
    def __init__(self):
        self.smart_dir = SMART_DIR
        self.loaded_memories = {
            "L1": [],
            "L2": [],
            "L3": [],
            "L4": [],
            "L5": []
        }
    
    def initialize(self) -> dict:
        """
        初始化会话 - 加载历史记忆
        返回加载的记忆摘要
        """
        print("[记忆继承] 开始加载历史记忆...")
        
        # 检查 MEMORY.md 是否需要压缩
        self._check_memory_md_compaction()
        
        # 加载各层记忆
        self._load_L1()
        self._load_L2()
        self._load_L3()
        self._load_L4()
        self._load_L5()
        
        summary = self.get_summary()
        print(f"[记忆继承] 加载完成: {summary['total']} 条记忆")
        
        return summary
    
    def _check_memory_md_compaction(self):
        """检查 MEMORY.md 大小，超过阈值时自动压缩"""
        try:
            sys.path.insert(0, str(self.smart_dir))
            from auto_compact import should_compact, compact_memory_md
            
            if should_compact():
                print("[记忆压缩] MEMORY.md 超限，开始压缩...")
                ok, msg = compact_memory_md()
                print(f"[记忆压缩] {msg}")
        except Exception as e:
            print(f"[记忆压缩] 检查失败: {e}")
    
    def _load_L1(self):
        """加载 L1 工作记忆"""
        l1_file = self.smart_dir / "L1_working" / "session.json"
        if l1_file.exists():
            try:
                with open(l1_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.loaded_memories["L1"] = data
            except:
                pass
    
    def _load_L2(self):
        """加载 L2 短期记忆"""
        l2_dir = self.smart_dir / "L2_short_term"
        if l2_dir.exists():
            for f in l2_dir.glob("*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        self.loaded_memories["L2"].extend(data.get("memories", []))
                except:
                    continue
    
    def _load_L3(self):
        """加载 L3 中期记忆"""
        l3_dir = self.smart_dir / "L3_mid_term" / "events"
        if l3_dir.exists():
            for f in l3_dir.glob("*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        self.loaded_memories["L3"].append(data)
                except:
                    continue
    
    def _load_L4(self):
        """加载 L4 长期记忆"""
        l4_file = self.smart_dir / "L4_long_term" / "memories.json"
        if l4_file.exists():
            try:
                with open(l4_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.loaded_memories["L4"] = data.get("memories", [])
            except:
                pass
    
    def _load_L5(self):
        """加载 L5 语义记忆"""
        l5_file = self.smart_dir / "L5_semantic" / "concepts.json"
        if l5_file.exists():
            try:
                with open(l5_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.loaded_memories["L5"] = {
                        "concepts": data.get("concepts", []),
                        "relations": data.get("relations", [])
                    }
            except:
                pass
    
    def get_summary(self) -> dict:
        """获取记忆摘要"""
        return {
            "L1": len(self.loaded_memories["L1"]),
            "L2": len(self.loaded_memories["L2"]),
            "L3": len(self.loaded_memories["L3"]),
            "L4": len(self.loaded_memories["L4"]),
            "L5_concepts": len(self.loaded_memories["L5"].get("concepts", [])),
            "L5_relations": len(self.loaded_memories["L5"].get("relations", [])),
            "total": sum([
                len(self.loaded_memories["L1"]),
                len(self.loaded_memories["L2"]),
                len(self.loaded_memories["L3"]),
                len(self.loaded_memories["L4"]),
                len(self.loaded_memories["L5"].get("concepts", []))
            ])
        }
    
    def get_key_memories(self) -> list:
        """获取关键记忆（用于快速上下文）"""
        key_memories = []
        
        # 从 L4 获取最重要的记忆
        for mem in self.loaded_memories["L4"][:5]:
            key_memories.append({
                "type": "long_term",
                "content": mem.get("content", "")[:100],
                "tags": mem.get("tags", [])
            })
        
        # 从 L3 获取重要事件
        for mem in self.loaded_memories["L3"][:3]:
            key_memories.append({
                "type": "important_event",
                "content": mem.get("original_content", "")[:100],
                "score": mem.get("importance_score", 0)
            })
        
        return key_memories
    
    def get_user_preferences(self) -> dict:
        """获取用户偏好记忆"""
        prefs = {
            "language": "中文",
            "design_preferences": [],
            "technical_preferences": [],
            "contact": None
        }
        
        # 从 L4 提取偏好
        for mem in self.loaded_memories["L4"]:
            content = mem.get("content", "")
            tags = mem.get("tags", [])
            
            if "偏好" in str(tags) or "喜欢" in content:
                prefs["design_preferences"].append(content)
            
            if "技术" in str(tags) or "配置" in content:
                prefs["technical_preferences"].append(content)
            
            if "邮箱" in content or "email" in content.lower():
                prefs["contact"] = content
        
        return prefs
    
    def get_recent_context(self, days: int = 3) -> list:
        """获取最近 N 天的上下文"""
        from datetime import timedelta
        
        context = []
        cutoff = datetime.now() - timedelta(days=days)
        
        # 从 L2 获取最近的记忆
        for mem in self.loaded_memories["L2"]:
            try:
                created = datetime.fromisoformat(mem.get("created_at", ""))
                if created >= cutoff:
                    context.append({
                        "type": "recent",
                        "content": mem.get("content", "")
                    })
            except:
                continue
        
        return context


def get_session_initializer() -> SessionInitializer:
    """获取会话初始化器"""
    return SessionInitializer()


def initialize_session() -> dict:
    """
    便捷函数：初始化会话并返回记忆摘要
    """
    initializer = get_session_initializer()
    return initializer.initialize()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=== 跨会话记忆继承测试 ===\n")
    
    # 初始化
    init = get_session_initializer()
    summary = init.initialize()
    
    print("\n[记忆摘要]")
    for layer, count in summary.items():
        if layer != "total":
            print(f"  {layer}: {count}")
    print(f"  总计: {summary['total']}")
    
    print("\n[用户偏好]")
    prefs = init.get_user_preferences()
    for k, v in prefs.items():
        print(f"  {k}: {v}")
    
    print("\n[关键记忆]")
    key = init.get_key_memories()
    for i, m in enumerate(key[:3]):
        print(f"  {i+1}. [{m['type']}] {m['content'][:50]}...")
