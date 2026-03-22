"""
Case Template 判例提取器
识别并提取记忆中的「情境/判断/后果/修正」四段式结构

来自 Memory Guardian 的设计思路：
- 判例 = 曾经做过的决策 + 结果验证
- 判例加成：带「修正」结论的记忆稳定性+10%

使用方式:
  from case_template import CaseTemplateExtractor
  extractor = CaseTemplateExtractor()
  result = extractor.extract("用户之前做XXX，后来发现YYY，改成ZZZ了")
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class CaseTemplate:
    """四段式判例结构"""
    # 情境：什么背景下发生的
    situation: str = ""
    # 判断：当时做了什么决定
    decision: str = ""
    # 后果：结果是什么
    consequence: str = ""
    # 修正：后来怎么改进的
    correction: str = ""
    # 元数据
    raw_text: str = ""
    confidence: float = 0.0  # 匹配置信度 (0-1)
    has_correction: bool = False  # 是否有修正部分
    
    def to_dict(self) -> Dict:
        return {
            "situation": self.situation,
            "decision": self.decision,
            "consequence": self.consequence,
            "correction": self.correction,
            "confidence": self.confidence,
            "has_correction": self.has_correction
        }
    
    def get_bonus_factor(self) -> float:
        """判例加成因子"""
        if self.has_correction and self.confidence > 0.5:
            return 1.1  # 有修正且置信度高，+10%稳定性
        return 1.0


class CaseTemplateExtractor:
    """
    判例模板自动识别
    检测「情境/判断/后果/修正」四段式结构
    
    模式识别策略：
    1. 显式标记：关键词直接标注各段
    2. 隐式推断：根据连接词推断结构
    3. 混合：部分显式 + 部分推断
    """
    
    # 各段关键词（显式标记）
    SITUATION_MARKERS = [
        r"情境[：:]", r"背景[：:]", r"情况[：:]", r"当时[，,]",
        r"之前[，,]", r"曾经[，,]", r"有一次[，,]", r"原来[，,]",
        r"本来[，,]", r"起初[，,]"
    ]
    
    DECISION_MARKERS = [
        r"决定[：:]", r"判断[：:]", r"于是[，,]", r"所以[，,]",
        r"就[把用让把]", r"选择[了去]", r"用了?(.+?)方案",
        r"采用[了]?(.+?)", r"做了?(.+?)决定", r"采用(.+?)方法",
        r"结果[是用了]?(.+?)"
    ]
    
    CONSEQUENCE_MARKERS = [
        r"结果[是发]", r"后果[是]", r"后来[发]", r"最后[是]",
        r"导致[了]", r"造成[了]", r"引起[了]",
        r"没想到[，]", r"但是[，]",
        r"发现[了是]", r"出来[了]",
        r"实际[上][是]", r"问题[是出在]"
    ]
    
    CORRECTION_MARKERS = [
        r"修正[为是成]", r"改成[了]?(.+?)", r"改为[了]?(.+?)",
        r"后来[改成换成改用]", r"改用[了]?(.+?)",
        r"换成[了]?(.+?)", r"改为[了]?(.+?)",
        r"纠正[为是]", r"调整[为是]",
        r"改进[为是]", r"优化[为是成]",
        r"后来发现[，]?(应该|要|得)",
        r"吸取?教训[，]?(?:以后|下次|今后)"
    ]
    
    # 全角转半角
    PUNCT_MAP = str.maketrans("：", ":")
    
    def __init__(self):
        self._compile_regexes()
    
    def _compile_regexes(self):
        """预编译正则表达式"""
        self._sit_re = re.compile("|".join(self.SITUATION_MARKERS), re.MULTILINE)
        self._dec_re = re.compile("|".join(self.DECISION_MARKERS), re.MULTILINE)
        self._con_re = re.compile("|".join(self.CONSEQUENCE_MARKERS), re.MULTILINE)
        self._cor_re = re.compile("|".join(self.CORRECTION_MARKERS), re.MULTILINE)
        
        # 隐式结构：常见句式模式
        # 格式: "原本X → 结果Y → 修正Z"
        self._implicit_re = re.compile(
            r"(.{5,20}?)"        # 情境部分
            r"[，,]?"             # 逗号
            r"(.{5,20}?)"        # 决策/结果
            r"[，,]?(?:发现|结果|后来|但是)[，,]?"
            r"(.+)",             # 修正/后果
            re.MULTILINE
        )
    
    def extract(self, text: str) -> Optional[CaseTemplate]:
        """
        从文本中提取判例模板
        
        Returns:
            CaseTemplate 或 None（如果文本不符合判例结构）
        """
        if not text or len(text) < 20:
            return None
        
        text = text.translate(self.PUNCT_MAP)
        
        # 策略1: 显式四段式
        template = self._extract_explicit(text)
        if template and template.confidence > 0.6:
            return template
        
        # 策略2: 隐式推断
        template = self._extract_implicit(text)
        if template and template.confidence > 0.4:
            return template
        
        # 策略3: 单段判例（只有修正部分）
        template = self._extract_correction_only(text)
        if template:
            return template
        
        return None
    
    def _extract_explicit(self, text: str) -> Optional[CaseTemplate]:
        """策略1: 显式标记的判例"""
        template = CaseTemplate(raw_text=text)
        
        # 找各段
        sit_match = self._sit_re.search(text)
        dec_match = self._dec_re.search(text)
        con_match = self._con_re.search(text)
        cor_match = self._cor_re.search(text)
        
        if not (dec_match or con_match):
            return None
        
        matches = []
        for label, m in [("sit", sit_match), ("dec", dec_match), ("con", con_match), ("cor", cor_match)]:
            if m:
                pos = m.start()
                matches.append((label, pos, m.group()))
        
        if len(matches) < 2:
            return None
        
        # 按位置排序
        matches.sort(key=lambda x: x[1])
        
        # 提取各段内容
        parts = {}
        for i, (label, pos, matched_text) in enumerate(matches):
            start = pos + len(matched_text)
            if i + 1 < len(matches):
                end = matches[i + 1][1]
            else:
                end = len(text)
            content = text[start:end].strip().rstrip("，,。.")
            if label == "sit":
                template.situation = content
            elif label == "dec":
                template.decision = content
            elif label == "con":
                template.consequence = content
            elif label == "cor":
                template.correction = content
        
        # 计算置信度
        covered = sum(len(getattr(template, f)) for f in ["situation", "decision", "consequence", "correction"])
        template.confidence = min(covered / 40.0, 1.0)  # 每段内容约10字符
        template.has_correction = bool(template.correction)
        
        return template if template.confidence > 0.3 else None
    
    def _extract_implicit(self, text: str) -> Optional[CaseTemplate]:
        """策略2: 从连接词推断结构"""
        template = CaseTemplate(raw_text=text)
        
        # "原本X，结果Y，改成Z" 模式
        patterns = [
            # 原本X → 结果Y → 修正Z
            (r"原本(.+?)[，,]结果(.+?)[，,]改成(.+?)[。$]", "sit", "dec", "cor"),
            (r"原本(.+?)[，,]结果(.+?)[，,]改为(.+?)[。$]", "sit", "dec", "cor"),
            # X → 结果Y → 修正Z
            (r"^(.{3,15}?)，结果(.+?)，后来(.+?)[。$]", "sit", "con", "cor"),
            (r"^(.{3,15}?)，结果(.+?)，改成(.+?)[。$]", "sit", "con", "cor"),
            # X，Y，于是Z
            (r"(.+?)，(.+?)，于是(.+?)[。$]", "sit", "con", "dec"),
            # 发现X问题，改成Y
            (r"发现(.+?)[，,]?(?:于是)?改成(.+?)[。$]", "con", "cor"),
            (r"发现(.+?)[，,]?(?:于是)?改为(.+?)[。$]", "con", "cor"),
        ]
        
        for item in patterns:
            if len(item) == 4:
                pattern, f1, f2, f3 = item
            else:
                pattern, f1, f2 = item
                f3 = None
            m = re.search(pattern, text)
            if m:
                groups = m.groups()
                if f1 == "sit": template.situation = groups[0]
                elif f1 == "con": template.consequence = groups[0]
                if f2 == "dec": template.decision = groups[1]
                elif f2 == "con": template.consequence = groups[1]
                elif f2 == "cor": template.correction = groups[1]
                if f3 and len(groups) >= 3:
                    if f3 == "dec": template.decision = groups[2]
                    elif f3 == "cor": template.correction = groups[2]
                
                template.has_correction = bool(template.correction)
                template.confidence = 0.5 if template.has_correction else 0.4
                return template
        
        return None
    
    def _extract_correction_only(self, text: str) -> Optional[CaseTemplate]:
        """策略3: 只有修正部分（单段判例）"""
        template = CaseTemplate(raw_text=text)
        
        # 检测修正关键词
        cor_m = self._cor_re.search(text)
        if cor_m:
            start = cor_m.end()
            template.correction = text[start:].strip().rstrip("，,。.")
            template.confidence = 0.4
            template.has_correction = True
            return template
        
        # 检测「教训」类关键词
        lesson_re = re.compile(r"(教训|经验|注意)[：:](.+?)[。$]")
        les_m = lesson_re.search(text)
        if les_m:
            template.consequence = les_m.group(2)
            template.decision = "从教训中学习"
            template.confidence = 0.35
            template.has_correction = True
            return template
        
        return None
    
    def batch_extract(self, texts: List[str]) -> List[Tuple[str, Optional[CaseTemplate]]]:
        """
        批量提取判例
        
        Returns:
            [(原始文本, CaseTemplate或None), ...]
        """
        return [(text, self.extract(text)) for text in texts]


# 便捷函数
_extractor = None

def get_extractor() -> CaseTemplateExtractor:
    global _extractor
    if _extractor is None:
        _extractor = CaseTemplateExtractor()
    return _extractor


def extract_case(text: str) -> Optional[CaseTemplate]:
    """快速提取判例"""
    return get_extractor().extract(text)


if __name__ == "__main__":
    # 测试用例
    extractor = CaseTemplateExtractor()
    
    tests = [
        # 显式四段式
        "情境：兴哥用微信扫码登录，结果二维码扫不出来，修正：后来用浏览器打开二维码URL然后截图给兴哥扫",
        
        # 隐式
        "原本想用curl下载二维码，结果扫不出来，后来改成用浏览器打开页面截图",
        
        # 只有修正
        "后来改成了在桌面生成PNG图片，方便用微信扫",
        
        # 普通句子（非判例）
        "今天天气很好，兴哥让我去逛Moltbook社区",
        
        # 带教训
        "教训：微信登录时不要用ASCII二维码，必须生成PNG图片",
        
        # 长句
        "背景是今天配置微信插件，二维码在终端显示不出来，后来我查了API文档，发现qrcode_img_content实际上是URL不是base64，修正：改用Playwright截图",
    ]
    
    print("=== Case Template 提取测试 ===\n")
    for text in tests:
        result = extractor.extract(text)
        if result:
            print(f"原始: {text[:60]}...")
            print(f"  置信度: {result.confidence:.2f}")
            print(f"  有修正: {result.has_correction}")
            print(f"  情境: {result.situation[:40] if result.situation else '-'}")
            print(f"  决策: {result.decision[:40] if result.decision else '-'}")
            print(f"  后果: {result.consequence[:40] if result.consequence else '-'}")
            print(f"  修正: {result.correction[:40] if result.correction else '-'}")
            print(f"  加成: {result.get_bonus_factor():.2f}")
        else:
            print(f"非判例: {text[:50]}...")
        print()
