#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis 向量语义检索系统 - 轻量版
使用 TF-IDF + 语义相似度 实现，无需下载大模型
"""
import os
import json
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter

# 基础路径
BASE_DIR = Path(__file__).parent
VECTOR_DIR = BASE_DIR / "vector_store"


class TFIDFVectorizer:
    """TF-IDF 向量化器 - 轻量级语义搜索"""
    
    def __init__(self):
        self.vocabulary = {}
        self.idf = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 简单中文分词
        text = text.lower()
        # 提取中文词和英文词
        chinese = re.findall(r'[\u4e00-\u9fff]+', text)
        english = re.findall(r'[a-z]+', text)
        # 简单处理：每个汉字作为特征 + 英文单词
        tokens = []
        for word in chinese:
            if len(word) >= 2:  # 2个字以上
                tokens.extend([word[i:i+2] for i in range(len(word)-1)])
        tokens.extend(english)
        return tokens
    
    def fit(self, documents: List[str]):
        """训练 TF-IDF 模型"""
        # 计算 IDF
        N = len(documents)
        df = Counter()
        
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                df[token] += 1
        
        # 计算 IDF
        for token, count in df.items():
            self.idf[token] = math.log(N / (count + 1)) + 1
        
        # 建立词汇表
        self.vocabulary = {token: i for i, token in enumerate(self.idf.keys())}
    
    def transform(self, text: str) -> List[float]:
        """转换为向量"""
        tokens = self._tokenize(text)
        tokens_counts = Counter(tokens)
        
        # 创建向量
        vector = [0.0] * len(self.vocabulary)
        
        for token, count in tokens_counts.items():
            if token in self.vocabulary:
                tf = count / max(len(tokens), 1)
                idx = self.vocabulary[token]
                vector[idx] = tf * self.idf.get(token, 1)
        
        return vector
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """余弦相似度"""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot / (norm1 * norm2)


class SemanticSearchManager:
    """语义搜索管理器"""
    
    def __init__(self):
        self.memories = []  # 所有记忆
        self.vectorizer = TFIDFVectorizer()
        self._load_memories()
    
    def _load_memories(self):
        """从文件加载已有记忆"""
        # 尝试从 L4 加载
        l4_file = BASE_DIR / "L4_long_term" / "memories.json"
        if l4_file.exists():
            try:
                with open(l4_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for mem in data.get('memories', []):
                        self.memories.append({
                            'id': f"l4_{mem.get('id', len(self.memories))}",
                            'content': mem.get('content', ''),
                            'tags': mem.get('tags', []),
                            'layer': 'L4'
                        })
            except:
                pass
        
        # 训练向量模型
        if self.memories:
            docs = [m['content'] for m in self.memories]
            self.vectorizer.fit(docs)
            print(f"Loaded {len(self.memories)} memories, vocabulary: {len(self.vectorizer.vocabulary)}")
    
    def add_memory(self, memory_id: str, content: str, tags: List[str] = None, layer: str = "L4"):
        """添加记忆"""
        # 重新训练（增量）
        self.memories.append({
            'id': memory_id,
            'content': content,
            'tags': tags or [],
            'layer': layer
        })
        
        # 增量更新
        docs = [m['content'] for m in self.memories]
        self.vectorizer.fit(docs)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """语义搜索"""
        if not self.memories:
            return []
        
        # 查询向量化
        query_vec = self.vectorizer.transform(query)
        
        # 计算相似度
        results = []
        for mem in self.memories:
            mem_vec = self.vectorizer.transform(mem['content'])
            similarity = self.vectorizer.cosine_similarity(query_vec, mem_vec)
            
            # 也考虑标签匹配
            query_keywords = set(query.lower().split())
            tag_match = 0
            for tag in mem.get('tags', []):
                if tag.lower() in query_keywords:
                    tag_match += 0.3
            
            total_score = similarity + tag_match
            
            results.append({
                **mem,
                'relevance_score': round(total_score, 4),
                'semantic_score': round(similarity, 4)
            })
        
        # 排序
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:n_results]
    
    def get_all_memories(self) -> List[Dict]:
        """获取所有记忆"""
        return self.memories
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "total_memories": len(self.memories),
            "vocabulary_size": len(self.vectorizer.vocabulary),
            "storage_type": "tfidf"
        }


# 便捷函数
def get_semantic_search() -> SemanticSearchManager:
    """获取语义搜索管理器"""
    return SemanticSearchManager()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=== 语义搜索测试 (TF-IDF) ===\n")
    
    ss = get_semantic_search()
    print("Status:", ss.get_status())
    print()
    
    # 添加测试记忆
    print("添加测试记忆...")
    ss.add_memory("mem_1", "兴哥喜欢简洁的蓝色PPT设计风格", ["偏好", "设计"])
    ss.add_memory("mem_2", "用户的主要邮箱是 martin202008@163.com", ["用户", "邮箱"])
    ss.add_memory("mem_3", "Jarvis 运行在 OpenClaw 平台，使用 MiniMax M2.5 模型", ["技术", "配置"])
    ss.add_memory("mem_4", "用户喜欢在早上讨论技术话题", ["习惯", "用户"])
    ss.add_memory("mem_5", "今天完成了微信公众号文章的发布", ["工作", "完成"])
    ss.add_memory("mem_6", "兴哥的配色偏好是蓝色和紫色", ["偏好", "颜色"])
    
    print(f"Total: {ss.get_status()['total_memories']}")
    print()
    
    # 测试语义搜索
    test_queries = [
        "用户的配色偏好",
        "兴哥的设计品味", 
        "技术配置信息",
        "今天的工作",
        "蓝色风格"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        results = ss.search(query, 3)
        for r in results:
            print(f"  - {r['content'][:40]}... [score: {r['relevance_score']}]")
        print()
