#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis 情感感知系统
实时分析用户情绪，动态调整交互策略
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 基础路径
SMART_DIR = Path(__file__).parent
EMOTION_LOG = SMART_DIR / "emotion_log.json"
EMOTION_CONFIG = SMART_DIR / "emotion_config.json"


class EmotionDetector:
    """情感检测器"""
    
    def __init__(self):
        self.emotion_log = self._load_log()
        self.config = self._load_config()
    
    def _load_log(self) -> List[Dict]:
        """加载情感日志"""
        if EMOTION_LOG.exists():
            with open(EMOTION_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_log(self):
        """保存情感日志"""
        with open(EMOTION_LOG, 'w', encoding='utf-8') as f:
            json.dump(self.emotion_log, f, ensure_ascii=False, indent=2)
    
    def _load_config(self) -> Dict:
        """加载情感配置"""
        if EMOTION_CONFIG.exists():
            with open(EMOTION_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认情感词典
        return {
            "positive": {
                "keywords": ["好", "棒", "赞", "优秀", "完美", "喜欢", "感谢", "谢谢", "开心", "高兴", "满意", "不错", "太好了", "优秀", "厉害", "强", "牛", "真棒", "爱了", "完美"],
                "score": 1.0
            },
            "negative": {
                "keywords": ["差", "烂", "垃圾", "不满意", "生气", "愤怒", "讨厌", "烦", "慢", "久", "等", "问题", "错误", "失败", "bug", "乱码", "糟糕"],
                "score": -1.0
            },
            "excited": {
                "keywords": ["太棒了", "哇", "兴奋", "激动", "牛", "太强了", "震撼", "惊艳", "不可思议"],
                "score": 1.5
            },
            "frustrated": {
                "keywords": ["怎么还", "还没好", "太慢了", "气", "怒", "崩溃", "无语", "够了", "受够了"],
                "score": -1.5
            },
            "questioning": {
                "keywords": ["?", "？", "怎么", "为什么", "如何", "能不能", "会不会", "可以吗", "求解"],
                "score": 0
            }
        }
    
    def detect(self, text: str) -> Dict:
        """
        检测文本情感
        
        Returns:
            {
                "emotion": "positive/negative/excited/frustrated/neutral",
                "score": -2.0 到 2.0,
                "confidence": 0.0 到 1.0,
                "keywords": ["检测到的关键词"]
            }
        """
        text_lower = text.lower()
        detected_emotions = []
        
        # 检测各类型情感
        for emotion_type, config in self.config.items():
            keywords = config.get("keywords", [])
            base_score = config.get("score", 0)
            
            matched = []
            for keyword in keywords:
                if keyword in text_lower:
                    matched.append(keyword)
            
            if matched:
                detected_emotions.append({
                    "type": emotion_type,
                    "score": base_score,
                    "matched": matched
                })
        
        # 计算综合情感
        if not detected_emotions:
            return {
                "emotion": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "keywords": []
            }
        
        # 取最强情感
        strongest = max(detected_emotions, key=lambda x: abs(x["score"]))
        
        # 计算置信度
        confidence = min(len(strongest["matched"]) * 0.3, 1.0)
        
        result = {
            "emotion": strongest["type"],
            "score": strongest["score"],
            "confidence": confidence,
            "keywords": strongest["matched"],
            "all_detected": detected_emotions
        }
        
        # 记录
        self.log_emotion(text, result)
        
        return result
    
    def log_emotion(self, text: str, emotion_result: Dict):
        """记录情感到日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text_preview": text[:50],
            "emotion": emotion_result["emotion"],
            "score": emotion_result["score"],
            "confidence": emotion_result["confidence"]
        }
        
        self.emotion_log.append(entry)
        
        # 保留最近100条
        if len(self.emotion_log) > 100:
            self.emotion_log = self.emotion_log[-100:]
        
        self._save_log()
    
    def get_recent_emotions(self, limit: int = 10) -> List[Dict]:
        """获取最近情感记录"""
        return self.emotion_log[-limit:]
    
    def get_emotion_summary(self) -> Dict:
        """获取情感摘要"""
        if not self.emotion_log:
            return {"neutral": 1.0}
        
        counts = {}
        total = len(self.emotion_log)
        
        for entry in self.emotion_log:
            emotion = entry["emotion"]
            counts[emotion] = counts.get(emotion, 0) + 1
        
        # 转换为百分比
        summary = {k: round(v / total, 2) for k, v in counts.items()}
        
        # 计算平均情绪
        scores = [e["score"] for e in self.emotion_log[-10:]]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        summary["avg_score"] = round(avg_score, 2)
        
        return summary
    
    def get_response_strategy(self, emotion_result: Dict) -> str:
        """
        根据情感返回最佳响应策略
        """
        emotion = emotion_result["emotion"]
        score = emotion_result["score"]
        
        strategies = {
            "positive": "热情回应，表达感谢，继续保持高质量服务",
            "negative": "表示歉意，主动询问具体问题，积极解决",
            "excited": "强烈认可，分享喜悦，保持热情",
            "frustrated": "真诚道歉，快速解决问题，不要辩解",
            "neutral": "保持专业，正常回应",
            "questioning": "耐心解答，提供详细信息"
        }
        
        return strategies.get(emotion, "保持专业")


class EmotionAdapter:
    """情感适配器 - 根据用户情绪调整交互风格"""
    
    def __init__(self):
        self.detector = EmotionDetector()
    
    def analyze(self, text: str) -> Dict:
        """分析文本情感"""
        return self.detector.detect(text)
    
    def adapt_response(self, original_response: str, emotion: Dict) -> str:
        """
        根据情感调整回复
        
        Args:
            original_response: 原始回复
            emotion: 情感分析结果
            
        Returns:
            调整后的回复
        """
        emotion_type = emotion["emotion"]
        score = emotion["score"]
        
        # 前缀调整
        prefixes = {
            "positive": ["很高兴帮到您！", "谢谢认可！", "收到！"],
            "negative": ["非常抱歉给您带来不便！", "我理解您的不满，", "抱歉让您烦恼了，"],
            "excited": ["太棒了！", "哇，太感谢了！", "哈哈，很高兴！"],
            "frustrated": ["真的很抱歉！", "我完全理解您的心情，", "对不起，"],
            "neutral": [],
            "questioning": []
        }
        
        prefix = prefixes.get(emotion_type, [])[0] if prefixes.get(emotion_type) else ""
        
        # 后缀调整
        suffixes = {
            "negative": ["我会继续改进的。", "感谢您的反馈。"],
            "frustrated": ["真的很对不起。", "我会尽快解决。"],
            "positive": ["有需要随时告诉我！", "很高兴为您服务！"],
            "excited": ["期待下次继续帮到您！", "一起加油！"]
        }
        
        suffix = suffixes.get(emotion_type, [])[0] if suffixes.get(emotion_type) else ""
        
        # 组合
        if prefix and not original_response.startswith(prefix):
            original_response = prefix + original_response
        
        if suffix and not original_response.endswith(suffix):
            original_response = original_response + "\n\n" + suffix
        
        return original_response
    
    def get_tone_adjustment(self, emotion: Dict) -> Dict:
        """
        获取语气调整建议
        """
        emotion_type = emotion["emotion"]
        
        adjustments = {
            "positive": {
                "emoji": "😊",
                "tone": "热情",
                "pace": "正常",
                "detail_level": "标准"
            },
            "negative": {
                "emoji": "😔",
                "tone": "诚恳",
                "pace": "放缓",
                "detail_level": "详细"
            },
            "excited": {
                "emoji": "🎉",
                "tone": "激动",
                "pace": "轻快",
                "detail_level": "适中"
            },
            "frustrated": {
                "emoji": "😟",
                "tone": "同情",
                "pace": "缓慢",
                "detail_level": "详细"
            },
            "neutral": {
                "emoji": "🙂",
                "tone": "专业",
                "pace": "正常",
                "detail_level": "标准"
            },
            "questioning": {
                "emoji": "🤔",
                "tone": "耐心",
                "pace": "正常",
                "detail_level": "详细"
            }
        }
        
        return adjustments.get(emotion_type, adjustments["neutral"])


def get_emotion_detector() -> EmotionDetector:
    """获取情感检测器"""
    return EmotionDetector()


def get_emotion_adapter() -> EmotionAdapter:
    """获取情感适配器"""
    return EmotionAdapter()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=== 情感感知测试 ===\n")
    
    adapter = get_emotion_adapter()
    
    # 测试文本
    test_texts = [
        "太棒了！你做得真好！",
        "这个怎么解决啊？",
        "真的很垃圾，半天没反应",
        "谢谢你的帮助！",
        "能不能快点？等很久了"
    ]
    
    for text in test_texts:
        result = adapter.analyze(text)
        strategy = adapter.get_response_strategy(result)
        
        print(f"文本: {text}")
        print(f"情感: {result['emotion']} (score: {result['score']})")
        print(f"关键词: {result['keywords']}")
        print(f"策略: {strategy}")
        print()
    
    print("\n[情感统计]")
    summary = adapter.detector.get_emotion_summary()
    print(f"摘要: {summary}")
