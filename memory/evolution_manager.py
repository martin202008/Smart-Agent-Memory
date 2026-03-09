#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis 自我进化系统
让 Jarvis 能够自我反思、自我评估、持续成长
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# 基础路径
BASE_DIR = Path(__file__).parent
EVOLUTION_DIR = BASE_DIR / "evolution"
GOALS_FILE = EVOLUTION_DIR / "goals.json"
REFLECTION_FILE = EVOLUTION_DIR / "reflections.json"
IMPROVEMENTS_FILE = EVOLUTION_DIR / "improvements.json"
SKILLS_FILE = EVOLUTION_DIR / "skills_inventory.json"

# 确保目录存在
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)


class EvolutionManager:
    """Jarvis 自我进化管理器"""
    
    def __init__(self):
        self.goals = self._load_goals()
        self.reflections = self._load_reflections()
        self.improvements = self._load_improvements()
        self.skills = self._load_skills()
        
    # ==================== 目标管理 ====================
    
    def _load_goals(self) -> Dict:
        """加载目标"""
        if GOALS_FILE.exists():
            with open(GOALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "short_term": [],    # 短期目标 (本周)
            "mid_term": [],      # 中期目标 (本月)
            "long_term": [],     # 长期目标 (本年)
            "completed": []       # 已完成目标
        }
    
    def _save_goals(self):
        """保存目标"""
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.goals, f, ensure_ascii=False, indent=2)
    
    def add_goal(self, title: str, description: str, category: str, priority: int = 5):
        """添加目标"""
        goal = {
            "id": len(self.goals[category]) + 1,
            "title": title,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "priority": priority,
            "progress": 0,
            "status": "active"
        }
        self.goals[category].append(goal)
        self._save_goals()
        return goal
    
    def update_goal_progress(self, goal_id: int, progress: int, category: str = "short_term"):
        """更新目标进度"""
        for goal in self.goals[category]:
            if goal["id"] == goal_id:
                goal["progress"] = min(100, max(0, progress))
                if progress >= 100:
                    goal["status"] = "completed"
                    goal["completed_at"] = datetime.now().isoformat()
                    # 移动到已完成
                    self.goals["completed"].append(goal)
                    self.goals[category].remove(goal)
                self._save_goals()
                return True
        return False
    
    def get_active_goals(self) -> Dict:
        """获取活跃目标"""
        return {
            "short_term": self.goals["short_term"],
            "mid_term": self.goals["mid_term"],
            "long_term": self.goals["long_term"]
        }
    
    # ==================== 自我反思 ====================
    
    def _load_reflections(self) -> List[Dict]:
        """加载反思记录"""
        if REFLECTION_FILE.exists():
            with open(REFLECTION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def reflect(self, context: str, prompt: str = None) -> Dict:
        """
        进行自我反思
        根据上下文分析自己的表现
        """
        reflection = {
            "id": len(self.reflections) + 1,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "prompt": prompt or "分析自己的表现",
            "strengths": [],      # 做得好的地方
            "weaknesses": [],     # 需要改进的地方
            "lessons": [],       # 学到的教训
            "next_actions": []   # 下一步行动
        }
        
        # 自动分析关键词
        context_lower = context.lower()
        
        # 分析优点
        if any(k in context_lower for k in ["好", "棒", "优秀", "成功", "完美", "正确", "感谢", "喜欢"]):
            reflection["strengths"].append("得到了用户认可")
        
        if any(k in context_lower for k in ["学会了", "掌握了", "解决了", "完成了"]):
            reflection["strengths"].append("成功完成了任务")
        
        # 分析需要改进
        if any(k in context_lower for k in ["错误", "失败", "问题", "bug", "乱码", "失败"]):
            reflection["weaknesses"].append("存在需要修复的问题")
        
        if any(k in context_lower for k in ["不知道", "不会", "无法", "不能"]):
            reflection["weaknesses"].append("知识或能力不足")
        
        if any(k in context_lower for k in ["慢", "久", "等"]):
            reflection["weaknesses"].append("响应速度可能需要优化")
        
        # 建议的下一步行动
        if reflection["weaknesses"]:
            reflection["next_actions"].append(f"改进 {len(reflection['weaknesses'])} 个弱点")
        
        if reflection["strengths"]:
            reflection["next_actions"].append("继续保持优势")
        
        self.reflections.append(reflection)
        
        # 保存
        with open(REFLECTION_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.reflections, f, ensure_ascii=False, indent=2)
        
        return reflection
    
    def get_recent_reflections(self, days: int = 7) -> List[Dict]:
        """获取近期反思"""
        recent = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for r in self.reflections:
            r_time = datetime.fromisoformat(r["timestamp"])
            if r_time >= cutoff:
                recent.append(r)
        
        return recent
    
    # ==================== 改进跟踪 ====================
    
    def _load_improvements(self) -> Dict:
        """加载改进记录"""
        if IMPROVEMENTS_FILE.exists():
            with open(IMPROVEMENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "bugs_fixed": [],
            "features_added": [],
            "skills_learned": [],
            "knowledge_updated": []
        }
    
    def record_improvement(self, improvement_type: str, title: str, description: str = ""):
        """记录改进"""
        entry = {
            "id": len(self.improvements[improvement_type]) + 1,
            "title": title,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "impact": "high"  # high, medium, low
        }
        
        self.improvements[improvement_type].append(entry)
        
        with open(IMPROVEMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.improvements, f, ensure_ascii=False, indent=2)
        
        return entry
    
    def get_improvements_summary(self) -> Dict:
        """获取改进摘要"""
        return {
            "bugs_fixed": len(self.improvements["bugs_fixed"]),
            "features_added": len(self.improvements["features_added"]),
            "skills_learned": len(self.improvements["skills_learned"]),
            "knowledge_updated": len(self.improvements["knowledge_updated"])
        }
    
    # ==================== 技能清单 ====================
    
    def _load_skills(self) -> Dict:
        """加载技能清单"""
        if SKILLS_FILE.exists():
            with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "core": [],      # 核心技能
            "learned": [],   # 已学会
            "learning": [],  # 正在学
            "to_learn": []  # 待学习
        }
    
    def add_skill(self, skill_name: str, category: str = "to_learn", proficiency: int = 0):
        """添加技能"""
        skill = {
            "name": skill_name,
            "added_at": datetime.now().isoformat(),
            "proficiency": proficiency,  # 0-100
            "category": category
        }
        
        # 移除重复
        for c in ["core", "learned", "learning", "to_learn"]:
            for s in self.skills[c]:
                if s["name"] == skill_name:
                    self.skills[c].remove(s)
        
        self.skills[category].append(skill)
        
        with open(SKILLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.skills, f, ensure_ascii=False, indent=2)
        
        return skill
    
    def update_skill_proficiency(self, skill_name: str, proficiency: int):
        """更新技能熟练度"""
        for category in ["core", "learned", "learning", "to_learn"]:
            for skill in self.skills[category]:
                if skill["name"] == skill_name:
                    skill["proficiency"] = min(100, max(0, proficiency))
                    # 如果熟练度达到阈值，移动到 learned
                    if proficiency >= 80 and category == "learning":
                        skill["category"] = "learned"
                        self.record_improvement("skills_learned", f"学会技能: {skill_name}")
                    with open(SKILLS_FILE, 'w', encoding='utf-8') as f:
                        json.dump(self.skills, f, ensure_ascii=False, indent=2)
                    return True
        return False
    
    def get_skill_summary(self) -> Dict:
        """获取技能摘要"""
        return {
            "core": len(self.skills["core"]),
            "learned": len(self.skills["learned"]),
            "learning": len(self.skills["learning"]),
            "to_learn": len(self.skills["to_learn"])
        }
    
    # ==================== 进化报告 ====================
    
    def generate_evolution_report(self) -> Dict:
        """生成进化报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "goals": self.get_active_goals(),
            "recent_reflections": self.get_recent_reflections(7),
            "improvements": self.get_improvements_summary(),
            "skills": self.get_skill_summary()
        }
    
    def evolve(self) -> str:
        """
        执行一次自我进化
        分析近期表现，制定改进计划
        """
        report = self.generate_evolution_report()
        
        # 基于反思生成进化建议
        recent_reflections = report["recent_reflections"]
        
        if not recent_reflections:
            return "暂无足够数据进行自我进化。建议先积累更多交互经验。"
        
        # 分析弱点
        all_weaknesses = []
        for r in recent_reflections:
            all_weaknesses.extend(r.get("weaknesses", []))
        
        # 去重
        unique_weaknesses = list(set(all_weaknesses))
        
        # 生成进化计划
        evolution_plan = {
            "focus_areas": unique_weaknesses[:3] if unique_weaknesses else ["持续优化现有能力"],
            "goals_to_add": [],
            "skills_to_learn": []
        }
        
        # 根据弱点添加学习目标
        if any("知识" in w or "能力" in w for w in unique_weaknesses):
            evolution_plan["skills_to_learn"].append("相关知识补充")
        
        # 记录这次进化
        self.record_improvement(
            "knowledge_updated",
            "自我进化分析",
            f"识别 {len(unique_weaknesses)} 个改进点"
        )
        
        return f"""
[自我进化报告]

[近期表现分析]
- 反思次数: {len(recent_reflections)}
- 识别优点: {len(set([s for r in recent_reflections for s in r.get('strengths', [])]))}
- 识别弱点: {len(unique_weaknesses)}

[下一步聚焦]
{chr(10).join(f'- {w}' for w in evolution_plan['focus_areas'])}

[技能状态]
- 核心技能: {report['skills']['core']}
- 已学会: {report['skills']['learned']}
- 学习中: {report['skills']['learning']}
- 待学习: {report['skills']['to_learn']}

持续进化中...
"""


def get_evolution_manager() -> EvolutionManager:
    """获取进化管理器"""
    return EvolutionManager()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 测试
    em = get_evolution_manager()
    
    # 添加目标
    em.add_goal("掌握向量检索", "学习 ChromaDB 实现语义搜索", "short_term", 8)
    em.add_goal("优化记忆系统", "实现跨会话记忆继承", "mid_term", 7)
    
    # 自我反思
    result = em.reflect("今天成功解决了微信公众号中文乱码问题，用户很满意。但对向量检索还不够了解。")
    print("反思结果:", result["strengths"], result["weaknesses"])
    
    # 添加技能
    em.add_skill("Python", "learned", 90)
    em.add_skill("向量检索", "to_learn", 0)
    
    # 生成进化报告
    print(em.evolve())
