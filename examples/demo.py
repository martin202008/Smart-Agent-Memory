#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart-Agent-Memory 示例代码
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'memory'))

def demo():
    print("=" * 50)
    print("Smart-Agent-Memory 示例演示")
    print("=" * 50)
    
    # 1. 初始化
    print("\n[1] 初始化系统...")
    from memory import init_smart_memory
    result = init_smart_memory()
    print(f"  状态: {result['status']}")
    print(f"  记忆总数: {result['session_summary']['total']}")
    
    # 2. 记忆
    print("\n[2] 测试记忆功能...")
    from memory import remember
    score1 = remember("用户说他喜欢蓝色和紫色的配色")
    print(f"  记忆1 重要性分数: {score1}")
    
    score2 = remember("记住我的邮箱是 test@example.com", force_long_term=True)
    print(f"  记忆2 重要性分数: {score2} (强制长期)")
    
    # 3. 语义搜索
    print("\n[3] 测试语义搜索...")
    from memory import semantic_search
    
    queries = ["用户的配色偏好", "技术配置"]
    for query in queries:
        results = semantic_search(query, 3)
        print(f"  Query: '{query}'")
        for r in results[:2]:
            print(f"    - {r['content'][:30]}... [score: {r.get('relevance_score', 0):.2f}]")
    
    # 4. 情感分析
    print("\n[4] 测试情感分析...")
    from memory import analyze_emotion, adapt_response
    
    test_texts = [
        "太棒了！你做得真好！",
        "这个怎么解决？",
        "真的很垃圾，等半天了"
    ]
    
    for text in test_texts:
        emotion = analyze_emotion(text)
        print(f"  文本: {text}")
        print(f"  情感: {emotion['emotion']} (score: {emotion['score']})")
        
        # 调整回复
        response = adapt_response("这是我的回复", emotion)
        print(f"  调整后: {response[:40]}...")
        print()
    
    # 5. 自我进化
    print("\n[5] 测试自我进化...")
    from memory import reflect, evolve
    
    reflect("今天完成了智能记忆系统的开发，用户很满意")
    report = evolve()
    print(f"  进化报告:\n{report[:200]}...")
    
    # 6. 存储统计
    print("\n[6] 存储统计...")
    from memory import get_storage_stats
    stats = get_storage_stats()
    print(f"  L2 短期记忆: {stats['L2_memories']} 条")
    print(f"  L4 长期记忆: {stats['L4_memories']} 条")
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("=" * 50)


if __name__ == "__main__":
    demo()
