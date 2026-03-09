#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis Smart-Memory 统一入口
一行代码初始化所有记忆系统
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 延迟导入避免循环依赖
_memory_manager = None
_evolution_manager = None
_session_initializer = None
_vector_search = None


def init_smart_memory():
    """
    初始化 Jarvis Smart-Memory 5层记忆系统
    应该在每次会话开始时调用
    
    Returns:
        dict: 包含所有子系统的初始化状态
    """
    global _memory_manager, _evolution_manager, _session_initializer, _vector_search
    
    status = {
        "memory": False,
        "evolution": False,
        "session": False,
        "vector": False
    }
    
    # 1. 加载会话记忆（跨会话继承）
    from session_initializer import get_session_initializer
    _session_initializer = get_session_initializer()
    session_summary = _session_initializer.initialize()
    status["session"] = True
    
    # 2. 初始化记忆管理器
    from memory_manager import get_memory_manager
    _memory_manager = get_memory_manager()
    status["memory"] = True
    
    # 3. 初始化进化管理器
    from evolution_manager import get_evolution_manager
    _evolution_manager = get_evolution_manager()
    status["evolution"] = True
    
    # 4. 向量搜索已在 memory_manager 中初始化
    status["vector"] = True
    
    return {
        "status": status,
        "session_summary": session_summary,
        "memory_status": _memory_manager.get_memory_status(),
        "evolution_summary": _evolution_manager.get_skill_summary(),
        "user_preferences": _session_initializer.get_user_preferences()
    }


def get_memory_manager():
    """获取记忆管理器"""
    global _memory_manager
    if _memory_manager is None:
        from memory_manager import get_memory_manager as _gm
        _memory_manager = _gm()
    return _memory_manager


def get_evolution_manager():
    """获取进化管理器"""
    global _evolution_manager
    if _evolution_manager is None:
        from evolution_manager import get_evolution_manager as _ge
        _evolution_manager = _ge()
    return _evolution_manager


def get_session_initializer():
    """获取会话初始化器"""
    global _session_initializer
    if _session_initializer is None:
        from session_initializer import get_session_initializer as _gs
        _session_initializer = _gs()
    return _session_initializer


def remember(content: str, context: str = None, force_long_term: bool = False):
    """
    统一的记忆入口
    """
    mm = get_memory_manager()
    return mm.remember(content, context, force_long_term)


def recall(query: str) -> dict:
    """
    统一的回忆入口
    """
    mm = get_memory_manager()
    return mm.recall(query)


def semantic_search(query: str, top_k: int = 5):
    """
    语义搜索
    """
    mm = get_memory_manager()
    return mm.semantic_search(query, top_k)


def reflect(context: str):
    """
    自我反思
    """
    em = get_evolution_manager()
    return em.reflect(context)


def evolve() -> str:
    """
    自我进化
    """
    em = get_evolution_manager()
    return em.evolve()


def cleanup(dry_run: bool = True):
    """
    清理过期记忆
    
    Args:
        dry_run: True 则只报告不删除
    """
    from cleanup import get_cleanup_manager
    cleanup = get_cleanup_manager()
    return cleanup.cleanup(dry_run=dry_run)


def get_storage_stats() -> dict:
    """获取存储统计"""
    from cleanup import get_cleanup_manager
    cleanup = get_cleanup_manager()
    return cleanup.get_storage_stats()


def add_image(image_path: str, description: str = "", tags: list = None):
    """添加图片记忆"""
    from multimodal import get_multimodal_memory
    mm = get_multimodal_memory()
    return mm.add_image(image_path, description, tags)


def add_audio(audio_path: str, transcript: str = "", tags: list = None):
    """添加语音记忆"""
    from multimodal import get_multimodal_memory
    mm = get_multimodal_memory()
    return mm.add_audio(audio_path, transcript, tags)


def add_video(video_path: str, description: str = "", tags: list = None):
    """添加视频记忆"""
    from multimodal import get_multimodal_memory
    mm = get_multimodal_memory()
    return mm.add_video(video_path, description, tags)


def search_multimedia(tag: str):
    """搜索多媒体记忆"""
    from multimodal import get_multimodal_memory
    mm = get_multimodal_memory()
    return mm.search_by_tag(tag)


def get_multimedia_stats():
    """获取多媒体统计"""
    from multimodal import get_multimodal_memory
    mm = get_multimodal_memory()
    return mm.get_stats()


def analyze_emotion(text: str) -> dict:
    """分析文本情感"""
    from emotion import get_emotion_adapter
    adapter = get_emotion_adapter()
    return adapter.analyze(text)


def adapt_response(response: str, emotion: dict) -> str:
    """根据情感调整回复"""
    from emotion import get_emotion_adapter
    adapter = get_emotion_adapter()
    return adapter.adapt_response(response, emotion)


def get_tone_suggestion(emotion: dict) -> dict:
    """获取语气调整建议"""
    from emotion import get_emotion_adapter
    adapter = get_emotion_adapter()
    return adapter.get_tone_adjustment(emotion)


def get_emotion_summary() -> dict:
    """获取情感统计"""
    from emotion import get_emotion_detector
    detector = get_emotion_detector()
    return detector.get_emotion_summary()


# ==================== 自动初始化 ====================

# 当导入此模块时，自动初始化
# _auto_init = init_smart_memory()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=== Jarvis Smart-Memory 初始化 ===\n")
    
    result = init_smart_memory()
    
    print("[初始化状态]")
    for k, v in result["status"].items():
        status_str = "OK" if v else "FAIL"
        print(f"  {k}: {status_str}")
    
    print("\n[记忆摘要]")
    for layer, count in result["session_summary"].items():
        if layer != "total":
            print(f"  {layer}: {count}")
    
    print("\n[用户偏好]")
    prefs = result["user_preferences"]
    print(f"  语言: {prefs['language']}")
    print(f"  邮箱: {prefs['contact']}")
    print(f"  设计偏好: {len(prefs['design_preferences'])} 条")
    print(f"  技术偏好: {len(prefs['technical_preferences'])} 条")
    
    print("\n=== 初始化完成 ===")
    print("\n使用方法:")
    print("  from memory.smart import remember, recall, reflect, evolve")
    print("  remember('记住这个')")
    print("  recall('搜索内容')")
    print("  reflect('今天的表现...')")
    print("  evolve()")
