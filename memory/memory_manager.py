#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis Smart-Memory 5层记忆系统管理器
"""
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from vector_search import get_semantic_search
from decay_engine import DecayEngine, get_decay_engine
from case_template import CaseTemplateExtractor

# 基础路径
BASE_DIR = Path(__file__).parent
L1_DIR = BASE_DIR / "L1_working"
L2_DIR = BASE_DIR / "L2_short_term"
L3_DIR = BASE_DIR / "L3_mid_term" / "events"
L4_DIR = BASE_DIR / "L4_long_term"
L5_DIR = BASE_DIR / "L5_semantic"

# 配置
CONFIG_FILE = BASE_DIR / "config.json"
IMPORTANCE_FILE = BASE_DIR / "L3_mid_term" / "importance_config.json"

# 初始化目录
for d in [L1_DIR, L2_DIR, L3_DIR, L4_DIR, L5_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class MemoryManager:
    """Jarvis Smart-Memory 5层记忆管理器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.importance_rules = self._load_importance_rules()
        self.working_memory = {}  # L1: 内存中
        self.vector_store = get_semantic_search()  # 语义搜索
        self.decay_engine = get_decay_engine()  # 贝叶斯衰减引擎
        self.case_extractor = CaseTemplateExtractor()  # 判例模板提取
        
    def _load_config(self) -> Dict:
        """加载配置"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "short_term_ttl_days": 7,
            "importance_threshold": 5,
            "emotion_weights": {
                "positive_excitement": 1.5,
                "negative_frustration": 1.3,
                "repeated_topic": 1.4,
                "decision_point": 2.0,
                "preference_expressed": 1.8
            }
        }
    
    def _load_importance_rules(self) -> Dict:
        """加载重要性评分规则"""
        if IMPORTANCE_FILE.exists():
            with open(IMPORTANCE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        # 默认规则
        return {
            "rules": [
                {"keyword": "记住", "score": 5, "description": "用户明确要求记忆"},
                {"keyword": "喜欢", "score": 3, "description": "表达偏好"},
                {"keyword": "讨厌", "score": 3, "description": "表达厌恶"},
                {"keyword": "重要", "score": 4, "description": "明确重要"},
                {"keyword": "不要忘记", "score": 5, "description": "强调不忘"},
                {"keyword": "以后都用", "score": 4, "description": "持久偏好"},
            ],
            "thresholds": {
                "L3_promote": 5,  # 升到L3
                "L4_promote": 8,  # 升到L4
            }
        }
    
    # ==================== L1: 工作记忆 ====================
    
    def update_working_memory(self, key: str, value: Any):
        """更新L1工作记忆（当前会话）"""
        self.working_memory[key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        self._save_working_memory()
    
    def get_working_memory(self, key: str = None) -> Any:
        """获取L1工作记忆"""
        if key:
            return self.working_memory.get(key, {}).get("value")
        return self.working_memory
    
    def clear_working_memory(self):
        """清除L1工作记忆（会话结束时）"""
        self.working_memory = {}
        self._save_working_memory()
    
    def _save_working_memory(self):
        """保存L1到文件"""
        session_file = L1_DIR / "session.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(self.working_memory, f, ensure_ascii=False, indent=2)
    
    def load_working_memory(self):
        """加载L1工作记忆"""
        session_file = L1_DIR / "session.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                self.working_memory = json.load(f)
    
    # ==================== L2: 短期记忆 ====================
    
    def add_short_term_memory(self, content: str, metadata: Dict = None):
        """添加L2短期记忆"""
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = L2_DIR / f"{today}.json"
        
        # 读取今天的内容
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"date": today, "memories": []}
        
        # 添加新记忆
        memory_entry = {
            "id": len(data["memories"]) + 1,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        data["memories"].append(memory_entry)
        
        # 保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return memory_entry["id"]
    
    def get_short_term_memories(self, days: int = 7) -> List[Dict]:
        """获取L2短期记忆"""
        memories = []
        ttl = timedelta(days=days)
        
        for file in L2_DIR.glob("*.json"):
            try:
                file_date = datetime.strptime(file.stem, "%Y-%m-%d")
                if datetime.now() - file_date <= ttl:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        memories.extend(data.get("memories", []))
            except:
                continue
        
        return memories
    
    def cleanup_short_term_memory(self):
        """清理过期的L2短期记忆"""
        ttl = timedelta(days=self.config["short_term_ttl_days"])
        cleaned = 0
        
        for file in L2_DIR.glob("*.json"):
            try:
                file_date = datetime.strptime(file.stem, "%Y-%m-%d")
                if datetime.now() - file_date > ttl:
                    # 检查是否需要升级到L3
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 高重要性记忆升级到L3
                    for memory in data.get("memories", []):
                        score = self.calculate_importance(memory["content"])
                        if score >= self.importance_rules["thresholds"]["L3_promote"]:
                            self.promote_to_mid_term(memory, score)
                    
                    file.unlink()
                    cleaned += 1
            except:
                continue
        
        return cleaned
    
    # ==================== L3: 中期记忆 ====================
    
    def calculate_importance(self, content: str) -> int:
        """计算内容重要性分数"""
        score = 0
        content_lower = content.lower()
        
        for rule in self.importance_rules["rules"]:
            if rule["keyword"] in content_lower:
                score += rule["score"]
        
        # 应用情感权重
        emotion_weights = self.config.get("emotion_weights", {})
        for emotion, weight in emotion_weights.items():
            if emotion.replace("_", " ") in content_lower:
                score = int(score * weight)
                break
        
        return min(score, 10)  # 最高10分
    
    def log_event(self, content: str, metadata: Dict = None):
        """记录事件（可能触发L3）"""
        score = self.calculate_importance(content)
        
        # 记录到L2
        memory_id = self.add_short_term_memory(content, {
            **(metadata or {}),
            "importance_score": score
        })
        
        # 如果超过阈值，升级到L3
        if score >= self.importance_rules["thresholds"]["L3_promote"]:
            self.promote_to_mid_term({
                "content": content,
                "metadata": {**(metadata or {}), "importance_score": score}
            }, score)
        
        return score
    
    def promote_to_mid_term(self, memory: Dict, score: int):
        """升级到L3中期记忆"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        event_file = L3_DIR / f"{today}_{memory.get('id', 'auto')}.json"
        
        event_data = {
            "original_content": memory["content"],
            "importance_score": score,
            "promoted_at": datetime.now().isoformat(),
            "metadata": memory.get("metadata", {})
        }
        
        with open(event_file, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, ensure_ascii=False, indent=2)
    
    def get_mid_term_memories(self) -> List[Dict]:
        """获取L3中期记忆"""
        memories = []
        
        for file in L3_DIR.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                memories.append(json.load(f))
        
        return memories
    
    # ==================== L4: 长期记忆 ====================
    
    def add_long_term_memory(self, content: str, tags: List[str] = None, importance: int = 0):
        """添加L4长期记忆（带去重和重要性）"""
        l4_file = L4_DIR / "memories.json"
        
        if l4_file.exists():
            with open(l4_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"memories": []}
        
        # 去重检查1: 完全相同内容
        existing_ids = [m['id'] for m in data["memories"] if m.get('content') == content]
        if existing_ids:
            # ...existing code...
            existing_id = existing_ids[0]
            for mem in data["memories"]:
                if mem['id'] == existing_id:
                    # 合并标签（去重）
                    new_tags = set(mem.get('tags', [])) | set(tags or [])
                    mem['tags'] = list(new_tags)
                    # 更新重要性（取最大值）
                    mem['importance'] = max(mem.get('importance', 0), importance)
                    mem['updated_at'] = datetime.now().isoformat()
                    break
            with open(l4_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return {"action": "updated", "id": existing_id}
        
        # 去重检查2: 语义相似内容（相似度 > 0.8 视为重复）
        similar_search = self.vector_store.search(content, top_k=3)
        for sim_mem in similar_search:
            if sim_mem.get('semantic_score', 0) > 0.8:
                # 找到相似内容，合并标签和重要性
                sim_id = sim_mem['id']
                for mem in data["memories"]:
                    if f"l4_{mem['id']}" == sim_id or f"l3_{mem['id']}" == sim_id:
                        new_tags = set(mem.get('tags', [])) | set(tags or [])
                        mem['tags'] = list(new_tags)
                        mem['importance'] = max(mem.get('importance', 0), importance)
                        mem['updated_at'] = datetime.now().isoformat()
                        mem['deduped_at'] = datetime.now().isoformat()
                        break
                with open(l4_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return {"action": "merged", "similar_id": sim_id, "reason": "semantic_duplicate"}
        
        # 提取判例模板
        case = self.case_extractor.extract(content)
        
        # 添加新记忆
        memory_entry = {
            "id": len(data["memories"]) + 1,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "importance": importance,
            # 衰减引擎所需字段（归一化到0-1）
            "base_importance": importance / 10.0,
            "lifecycle_status": "active",
            # 判例模板
            "case_template": case.to_dict() if case else None,
            "has_correction": case.has_correction if case else False,
            "case_confidence": round(case.confidence, 3) if case else 0.0
        }
        
        data["memories"].append(memory_entry)
        
        with open(l4_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {"action": "added", "id": memory_entry["id"]}
    
    def get_long_term_memories(self, refresh_status: bool = False,
                                use_access_count: bool = True) -> List[Dict]:
        """
        获取L4长期记忆
        
        Args:
            refresh_status: 是否刷新所有记忆的 lifecycle_status（耗时，适合清理时调用）
            use_access_count: 刷新时是否计入访问次数。
                - 搜索时传入 True（访问多的记忆更稳定）
                - cleanup batch refresh 时传入 False（重置访问计数，只看时间衰减）
        """
        l4_file = L4_DIR / "memories.json"
        
        if not l4_file.exists():
            return []
        
        with open(l4_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            memories = data.get("memories", [])
        
        if refresh_status:
            updated = []
            for mem in memories:
                created_at = mem.get('created_at', datetime.now().isoformat())
                base_imp = mem.get('base_importance', 0.5)
                has_correction = mem.get('has_correction', False) or any(kw in mem.get('content', '') 
                                   for kw in ["修正", "教训", "错误", "踩坑", "correction"])
                mem_id = str(mem.get('id', 'unknown'))
                
                # cleanup 时 dry_run=True，不刷访问计数
                decay_score = self.decay_engine.get_decay_score(
                    base_importance=base_imp,
                    created_at=created_at,
                    memory_id=mem_id,
                    source="batch_refresh",
                    has_correction=has_correction,
                    dry_run=(not use_access_count)
                )
                mem['decay_score'] = round(decay_score, 4)
                mem['lifecycle_status'] = self.decay_engine.get_lifecycle_status(decay_score)
                updated.append(mem)
            
            data["memories"] = updated
            with open(l4_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return updated
        
        # 非刷新路径：也同步访问计数
        for mem in memories:
            mem_id = str(mem.get('id', 'unknown'))
            current_count = mem.get('access_count', 0)
            real_count = self.decay_engine.state.get("access_log", {}).get(mem_id, {}).get("count", 0)
            if real_count > current_count:
                mem['access_count'] = real_count
        
        return memories
    
    def semantic_search(self, query: str, top_k: int = 5, include_archived: bool = False) -> List[Dict]:
        """
        语义搜索 (L4) - 使用 TF-IDF 向量检索
        集成贝叶斯衰减引擎，返回时计算每条记忆的 lifecycle_status
        
        Args:
            query: 搜索query
            top_k: 返回数量
            include_archived: 是否包含 archived 状态的记忆（默认只返回 active）
        """
        raw_results = self.vector_store.search(query, top_k * 2)  # 多取一些，过滤后可能不够
        
        enriched = []
        for mem in raw_results:
            # 查找完整记忆数据（L4文件）
            memory_id = str(mem.get('id', '')).replace('l4_', '')
            l4_file = L4_DIR / "memories.json"
            
            full_memory = None
            if l4_file.exists():
                with open(l4_file, 'r', encoding='utf-8') as f:
                    l4_data = json.load(f)
                    for m in l4_data.get("memories", []):
                        if str(m.get('id')) == memory_id or f"l4_{m.get('id')}" == mem.get('id'):
                            full_memory = m
                            break
            
            # 使用记忆的实际字段计算衰减
            if full_memory:
                created_at = full_memory.get('created_at', datetime.now().isoformat())
                base_imp = full_memory.get('base_importance', 0.5)
                has_correction = full_memory.get('has_correction', False) or any(kw in full_memory.get('content', '') 
                                   for kw in ["修正", "教训", "错误", "踩坑"])
                decay_score = self.decay_engine.get_decay_score(
                    base_importance=base_imp,
                    created_at=created_at,
                    memory_id=memory_id,
                    source="semantic_search",
                    has_correction=has_correction
                )
                lifecycle_status = self.decay_engine.get_lifecycle_status(decay_score)
            else:
                # 找不到完整数据时，用语义分数估算
                semantic_score = mem.get('semantic_score', 0.5)
                decay_score = semantic_score * 0.5  # 保守估计
                lifecycle_status = self.decay_engine.get_lifecycle_status(decay_score)
            
            # 只返回 active，或包含 archived
            if include_archived or lifecycle_status == "active":
                # 同步访问计数到L4文件
                self._sync_access_count(memory_id, mem.get('access_count', 0))
                
                enriched.append({
                    **mem,
                    "decay_score": round(decay_score, 4),
                    "lifecycle_status": lifecycle_status
                })
            
            if len(enriched) >= top_k:
                break
        
        return enriched
    
    # ==================== L5: 语义记忆 ====================
    
    def add_concept(self, concept: str, category: str, properties: Dict = None):
        """添加L5语义概念"""
        l5_file = L5_DIR / "concepts.json"
        
        if l5_file.exists():
            with open(l5_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"concepts": [], "relations": []}
        
        # 检查是否已存在
        for c in data["concepts"]:
            if c["name"] == concept:
                return c["id"]
        
        concept_entry = {
            "id": len(data["concepts"]) + 1,
            "name": concept,
            "category": category,
            "properties": properties or {},
            "created_at": datetime.now().isoformat()
        }
        
        data["concepts"].append(concept_entry)
        
        with open(l5_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return concept_entry["id"]
    
    def add_relation(self, from_concept: str, to_concept: str, relation_type: str):
        """添加L5语义关系"""
        l5_file = L5_DIR / "concepts.json"
        
        if l5_file.exists():
            with open(l5_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            return None
        
        # 查找概念ID
        from_id = None
        to_id = None
        
        for c in data["concepts"]:
            if c["name"] == from_concept:
                from_id = c["id"]
            if c["name"] == to_concept:
                to_id = c["id"]
        
        if from_id and to_id:
            relation = {
                "from_id": from_id,
                "to_id": to_id,
                "type": relation_type,
                "created_at": datetime.now().isoformat()
            }
            data["relations"].append(relation)
            
            with open(l5_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        
        return False
    
    def get_concept_relations(self, concept: str) -> List[Dict]:
        """获取概念的关联"""
        l5_file = L5_DIR / "concepts.json"
        
        if not l5_file.exists():
            return []
        
        with open(l5_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 找到概念ID
        concept_id = None
        for c in data["concepts"]:
            if c["name"] == concept:
                concept_id = c["id"]
                break
        
        if not concept_id:
            return []
        
        # 找关联
        relations = []
        for r in data["relations"]:
            if r["from_id"] == concept_id or r["to_id"] == concept_id:
                # 获取对方概念名
                other_id = r["to_id"] if r["from_id"] == concept_id else r["from_id"]
                for c in data["concepts"]:
                    if c["id"] == other_id:
                        relations.append({
                            "concept": c["name"],
                            "relation": r["type"]
                        })
        
        return relations
    
    def _sync_access_count(self, memory_id: str, current_count: int):
        """
        将 decay_engine 中的真实访问次数同步到 L4 文件
        防止访问计数在进程重启后丢失
        """
        l4_file = L4_DIR / "memories.json"
        if not l4_file.exists():
            return
        
        # 获取 decay_engine 中的真实访问次数
        real_count = self.decay_engine.state.get("access_log", {}).get(memory_id, {}).get("count", 0)
        
        if real_count <= current_count:
            return  # 不用更新
        
        try:
            with open(l4_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for mem in data.get("memories", []):
                if str(mem.get('id')) == str(memory_id):
                    mem['access_count'] = real_count
                    break
            
            with open(l4_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    # ==================== 统一接口 ====================
    
    def remember(self, content: str, context: str = None, force_long_term: bool = False):
        """统一的记忆入口"""
        metadata = {"context": context} if context else {}
        
        # 计算重要性
        score = self.calculate_importance(content)
        
        # 直接添加到L4
        if force_long_term or score >= self.importance_rules["thresholds"]["L4_promote"]:
            # 传递 importance 分数
            self.add_long_term_memory(content, tags=[context] if context else None, importance=score)
            return {"layer": "L4", "score": score}
        
        # L2 + 触发检查
        self.log_event(content, metadata)
        return {"layer": "L2/L3", "score": score}
    
    def recall(self, query: str) -> Dict:
        """统一的回忆入口"""
        # L1: 工作记忆
        if query in self.working_memory:
            return {"layer": "L1", "data": self.working_memory[query]}
        
        # L4: 语义搜索（自动过滤 archived，只返回 active）
        l4_results = self.semantic_search(query)
        if l4_results:
            return {
                "layer": "L4",
                "data": l4_results,
                "total_with_decay": len(l4_results),
                "note": "仅返回 active 记忆（decay_score >= 0.2）"
            }
        
        # L5: 概念关联 - 改进为模糊搜索
        l5_results = self._search_concepts_fuzzy(query)
        if l5_results:
            return {"layer": "L5", "data": l5_results}
        
        return {"layer": None, "data": None}
    
    def _search_concepts_fuzzy(self, query: str) -> List[Dict]:
        """模糊搜索 L5 概念"""
        l5_file = L5_DIR / "concepts.json"
        if not l5_file.exists():
            return []
        
        with open(l5_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        query_lower = query.lower()
        matched_concepts = []
        
        # 模糊匹配概念名
        for c in data.get("concepts", []):
            if query_lower in c.get("name", "").lower():
                matched_concepts.append(c)
        
        # 如果没有直接匹配，查找关联
        results = []
        for c in matched_concepts:
            cid = c.get("id")
            # 找关联
            for r in data.get("relations", []):
                if r.get("from_id") == cid or r.get("to_id") == cid:
                    other_id = r.get("to_id") if r.get("from_id") == cid else r.get("from_id")
                    for oc in data.get("concepts", []):
                        if oc.get("id") == other_id:
                            results.append({
                                "concept": c.get("name"),
                                "related": oc.get("name"),
                                "relation": r.get("type"),
                                "category": c.get("category")
                            })
        
        return results
    
    def get_memory_status(self) -> Dict:
        """获取记忆系统状态（含衰减引擎健康报告）"""
        # L5: 直接读取概念数量
        l5_file = L5_DIR / "concepts.json"
        l5_count = 0
        if l5_file.exists():
            with open(l5_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                l5_count = len(data.get("concepts", []))
        
        # 获取衰减引擎健康报告
        decay_report = self.decay_engine.get_decay_report()
        
        # 统计各生命周期阶段数量
        l4_memories = self.get_long_term_memories()
        active_count = sum(1 for m in l4_memories if m.get("lifecycle_status") == "active")
        archived_count = sum(1 for m in l4_memories if m.get("lifecycle_status") == "archived")
        
        return {
            "L1_working": len(self.working_memory),
            "L2_short_term": len(self.get_short_term_memories()),
            "L3_mid_term": len(self.get_mid_term_memories()),
            "L4_long_term": len(l4_memories),
            "L4_active": active_count,
            "L4_archived": archived_count,
            "L5_semantic": l5_count,
            "decay_engine": decay_report
        }


# 便捷函数
def get_memory_manager() -> MemoryManager:
    """获取记忆管理器实例"""
    return MemoryManager()


if __name__ == "__main__":
    # 测试
    mm = get_memory_manager()
    
    # L1测试
    mm.update_working_memory("current_task", "写微信公众号推文")
    print("L1:", mm.get_working_memory("current_task"))
    
    # L2测试
    mm.add_short_term_memory("用户说他喜欢蓝色的PPT风格")
    print("L2 memories:", len(mm.get_short_term_memories()))
    
    # L3测试
    score = mm.log_event("用户说记住他叫兴哥，这是重要信息")
    print(f"L3 importance score: {score}")
    
    # L4测试
    mm.add_long_term_memory("兴哥喜欢简洁的蓝色设计风格", tags=["偏好", "设计"])
    print("L4 memories:", len(mm.get_long_term_memories()))
    
    # 搜索测试
    results = mm.semantic_search("设计风格偏好")
    print("Search results:", results)
    
    print("\nMemory status:", mm.get_memory_status())
