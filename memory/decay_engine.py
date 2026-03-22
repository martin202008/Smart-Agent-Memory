"""
Smart-Memory 贝叶斯衰减引擎
基于 Memory Guardian (pipi) 的设计思路

decay_score = base_importance × recency_factor × access_factor

阈值：
  score >= 0.2 → active（正常加载）
  0.05 <= score < 0.2 → archived（归档，可搜索但不自动加载）
  score < 0.05 → deleted（待确认删除）
"""

import os
import json
import math
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent

# 默认参数
DEFAULT_DECAY_LAMBDA = 0.01  # λ=0.01，约100天衰减到37%
DEFAULT_ACCESS_COUNT_CAP = 100
DEFAULT_COOLING_THRESHOLD = 5  # 同一来源连续>5次访问，触发冷却
DEFAULT_COOLING_PENALTY = 0.5  # 冷却期间access_factor上限降至0.5
DECAY_CONFIG_FILE = BASE_DIR / "decay_state.json"


class DecayEngine:
    """贝叶斯衰减引擎"""

    def __init__(self, lambda_decay: float = DEFAULT_DECAY_LAMBDA):
        self.lambda_decay = lambda_decay
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载衰减状态（访问计数、冷却记录等）"""
        if DECAY_CONFIG_FILE.exists():
            with open(DECAY_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "access_log": {},  # memory_id -> {"count": N, "last_access": timestamp, "sources": {src: count}}
            "cooling_log": {},  # source -> {"count": N, "penalty_applied": bool, "reset_at": timestamp}
            "violations": []   # 规则违反事件
        }

    def _save_state(self):
        """保存衰减状态"""
        with open(DECAY_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _get_recency_factor(self, created_at: str) -> float:
        """计算时间衰减因子: exp(-λ × days_since_creation)"""
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days = (datetime.now() - created.replace(tzinfo=None)).total_seconds() / 86400
            return math.exp(-self.lambda_decay * days)
        except:
            return 0.5  # 默认中等

    def _get_access_factor(self, memory_id: str, source: str = "default") -> float:
        """
        计算访问频率因子: 0.3 + 0.7 × log(1+count) / log(1+cap)
        冷却机制：同一来源连续>5次访问，access_factor上限降至0.5
        """
        # 检查冷却
        cooling = self.state["cooling_log"].get(source, {})
        if cooling.get("penalty_applied"):
            # 检查冷却是否过期（5分钟后恢复）
            reset_at = datetime.fromisoformat(cooling["reset_at"])
            if datetime.now() < reset_at:
                return DEFAULT_COOLING_PENALTY
            else:
                # 冷却过期，重置
                self.state["cooling_log"][source] = {}
        
        # 更新访问计数
        if memory_id not in self.state["access_log"]:
            self.state["access_log"][memory_id] = {
                "count": 0,
                "last_access": None,
                "sources": {}
            }
        
        log = self.state["access_log"][memory_id]
        log["count"] += 1
        log["last_access"] = datetime.now().isoformat()
        
        # 更新来源计数
        if source not in log["sources"]:
            log["sources"][source] = 0
        log["sources"][source] += 1
        
        # 检查是否触发冷却
        if log["sources"][source] > DEFAULT_COOLING_THRESHOLD:
            self.state["cooling_log"][source] = {
                "count": log["sources"][source],
                "penalty_applied": True,
                "reset_at": (datetime.now() + timedelta(minutes=5)).isoformat()
            }
            self.state["violations"].append({
                "type": "cooling_triggered",
                "memory_id": memory_id,
                "source": source,
                "count": log["sources"][source],
                "at": datetime.now().isoformat()
            })
        
        # 计算因子
        count = log["count"]
        cap = DEFAULT_ACCESS_COUNT_CAP
        factor = 0.3 + 0.7 * math.log(1 + count) / math.log(1 + cap)
        return min(factor, 1.0)

    def get_decay_score(self, base_importance: float, created_at: str, 
                       memory_id: str, source: str = "default",
                       has_correction: bool = False,
                       dry_run: bool = False) -> float:
        """
        计算最终衰减分数
        
        Args:
            base_importance: 基础重要性 (0-1)
            created_at: 记忆创建时间 ISO格式
            memory_id: 记忆唯一ID
            source: 调用来源（用于冷却机制）
            has_correction: 是否有「修正」结论（判例加成+10%）
            dry_run: True则不计入访问计数（用于cleanup时的批量刷新）
        
        Returns:
            float: 衰减后的综合分数 (0-1)
        """
        recency = self._get_recency_factor(created_at)
        if not dry_run:
            access = self._get_access_factor(memory_id, source)
        else:
            # dry_run: 不计访问次数，用基准衰减
            access = 0.3 + 0.7 * math.log(2) / math.log(101)  # count=1时的默认值
        
        score = base_importance * recency * access
        
        # 判例加成：有「修正」结论的记忆稳定性+10%
        if has_correction:
            score *= 1.1
        
        if not dry_run:
            self._save_state()
        return min(score, 1.0)

    def get_lifecycle_status(self, decay_score: float) -> str:
        """根据衰减分数判断所处生命周期阶段"""
        if decay_score >= 0.2:
            return "active"
        elif decay_score >= 0.05:
            return "archived"
        else:
            return "deleted"

    def get_all_memory_status(self, memories: List[Dict]) -> Dict[str, List[Dict]]:
        """
        对所有记忆进行生命周期分类
        
        Returns:
            {"active": [...], "archived": [...], "deleted": [...]}
        """
        result = {"active": [], "archived": [], "deleted": []}
        
        for mem in memories:
            mem_id = mem.get("id", mem.get("memory_id", str(hash(mem.get("content", "")))))
            created = mem.get("created_at", mem.get("promoted_at", datetime.now().isoformat()))
            base_imp = mem.get("normalized_importance", 0.5)  # 归一化到0-1
            
            has_correction = "修正" in mem.get("original_content", "") or "教训" in mem.get("original_content", "")
            score = self.get_decay_score(base_imp, created, mem_id, has_correction=has_correction)
            status = self.get_lifecycle_status(score)
            
            mem["decay_score"] = round(score, 4)
            mem["lifecycle_status"] = status
            
            result[status].append(mem)
        
        return result

    def get_decay_report(self) -> Dict:
        """获取衰减系统健康报告"""
        access_count = len(self.state["access_log"])
        cooling_active = sum(1 for c in self.state["cooling_log"].values() if c.get("penalty_applied"))
        violations = len(self.state["violations"])
        
        return {
            "total_accessed_memories": access_count,
            "active_coolings": cooling_active,
            "total_violations": violations,
            "recent_violations": self.state["violations"][-5:] if self.state["violations"] else []
        }


# 便捷函数
_engine = None

def get_decay_engine() -> DecayEngine:
    global _engine
    if _engine is None:
        _engine = DecayEngine()
    return _engine


def get_score(content: str, created_at: str, memory_id: str, 
              source: str = "default", base_importance: float = 0.5) -> float:
    """快速计算单条记忆的衰减分数"""
    engine = get_decay_engine()
    has_correction = "修正" in content or "教训" in content or "错误" in content
    return engine.get_decay_score(base_importance, created_at, memory_id, source, has_correction)


if __name__ == "__main__":
    # 测试
    engine = DecayEngine(lambda_decay=0.01)
    
    # 模拟：7天前创建的、重要度0.8的记忆，被访问了3次
    score = engine.get_decay_score(
        base_importance=0.8,
        created_at=(datetime.now() - timedelta(days=7)).isoformat(),
        memory_id="test_memory_1",
        source="chat_session",
        has_correction=False
    )
    print(f"7天前创建的记录，重要度0.8，访问3次")
    print(f"衰减分数: {score:.4f}")
    print(f"生命周期: {engine.get_lifecycle_status(score)}")
    
    print()
    report = engine.get_decay_report()
    print(f"衰减报告: {json.dumps(report, ensure_ascii=False, indent=2)}")
