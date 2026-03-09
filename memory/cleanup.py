#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis 记忆自动清理系统
自动清理过期的 L2 短期记忆，支持定时任务
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import shutil

# 基础路径
SMART_DIR = Path(__file__).parent


class MemoryCleanup:
    """记忆自动清理器"""
    
    def __init__(self, ttl_days: int = 7):
        self.ttl_days = ttl_days
        self.cleanup_log = []
    
    def cleanup(self, dry_run: bool = False) -> Dict:
        """
        执行清理
        
        Args:
            dry_run: True 则只报告不删除
            
        Returns:
            清理报告
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "L2_deleted": [],
            "L2_promoted": [],
            "L3_deleted": [],
            "total_freed": 0,
            "errors": []
        }
        
        # 清理 L2 短期记忆
        self._cleanup_L2(report, dry_run)
        
        # 清理 L3 过期事件
        self._cleanup_L3(report, dry_run)
        
        # 清理旧日志
        self._cleanup_logs(report, dry_run)
        
        return report
    
    def _cleanup_L2(self, report: Dict, dry_run: bool):
        """清理 L2 短期记忆"""
        l2_dir = SMART_DIR / "L2_short_term"
        
        if not l2_dir.exists():
            return
        
        cutoff = datetime.now() - timedelta(days=self.ttl_days)
        
        for file in l2_dir.glob("*.json"):
            try:
                file_date = datetime.strptime(file.stem, "%Y-%m-%d")
                
                if file_date < cutoff:
                    # 读取内容检查重要性
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查是否需要升级到 L3
                    promoted = self._check_promotion(data.get("memories", []))
                    
                    if promoted and not dry_run:
                        self._promote_to_L3(promoted)
                        report["L2_promoted"].append({
                            "file": file.name,
                            "count": len(promoted)
                        })
                    
                    # 删除文件
                    if not dry_run:
                        file.unlink()
                        report["L2_deleted"].append(file.name)
                    
                    report["total_freed"] += 1
                    
            except Exception as e:
                report["errors"].append(f"L2 cleanup error: {e}")
    
    def _check_promotion(self, memories: List) -> List:
        """检查哪些记忆需要升级到 L3"""
        threshold = 5  # 重要性阈值
        to_promote = []
        
        for mem in memories:
            score = mem.get("metadata", {}).get("importance_score", 0)
            if score >= threshold:
                to_promote.append(mem)
        
        return to_promote
    
    def _promote_to_L3(self, memories: List):
        """升级到 L3"""
        l3_dir = SMART_DIR / "L3_mid_term" / "events"
        l3_dir.mkdir(parents=True, exist_ok=True)
        
        for mem in memories:
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"{today}_auto_{mem.get('id', 'unk')}.json"
            
            event_data = {
                "original_content": mem.get("content", ""),
                "importance_score": mem.get("metadata", {}).get("importance_score", 0),
                "promoted_at": datetime.now().isoformat(),
                "auto_promoted": True,
                "metadata": mem.get("metadata", {})
            }
            
            with open(l3_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(event_data, f, ensure_ascii=False, indent=2)
    
    def _cleanup_L3(self, report: Dict, dry_run: bool):
        """清理 L3 过期事件（保留90天）"""
        l3_dir = SMART_DIR / "L3_mid_term" / "events"
        
        if not l3_dir.exists():
            return
        
        cutoff = datetime.now() - timedelta(days=90)
        
        for file in l3_dir.glob("*.json"):
            try:
                # 从文件名提取日期
                parts = file.stem.split("_")
                if len(parts) >= 1:
                    file_date = datetime.strptime(parts[0], "%Y-%m-%d")
                    
                    if file_date < cutoff:
                        if not dry_run:
                            file.unlink()
                            report["L3_deleted"].append(file.name)
                        
                        report["total_freed"] += 1
                        
            except Exception as e:
                report["errors"].append(f"L3 cleanup error: {e}")
    
    def _cleanup_logs(self, report: Dict, dry_run: bool):
        """清理旧日志文件"""
        # 清理 memory 目录下的旧日志（保留30天）
        memory_dir = SMART_DIR.parent
        
        if not memory_dir.exists():
            return
        
        cutoff = datetime.now() - timedelta(days=30)
        
        for file in memory_dir.glob("*.md"):
            try:
                if file.stat().st_mtime < cutoff.timestamp():
                    # 不删除 MEMORY.md, AGENTS.md, USER.md 等核心文件
                    if file.name not in ["MEMORY.md", "AGENTS.md", "USER.md", "SOUL.md"]:
                        if not dry_run:
                            # 移动到 trash 而不是删除
                            trash_dir = memory_dir / "trash"
                            trash_dir.mkdir(exist_ok=True)
                            shutil.move(str(file), str(trash_dir / file.name))
            except:
                pass
    
    def schedule_cleanup(self) -> str:
        """生成定时任务命令"""
        # 返回 cron 命令
        # 每周日凌晨3点执行清理
        return """
# 添加到 crontab (每周日凌晨3点自动清理)
0 3 * * 0 cd /path/to/workspace && python memory/smart/cleanup.py --auto

# 或者使用 Windows 计划任务
schtasks /create /tn "Jarvis Memory Cleanup" /tr "python memory\\smart\\cleanup.py --auto" /sc weekly /d SUN /st 03:00
"""
    
    def get_storage_stats(self) -> Dict:
        """获取存储统计"""
        stats = {
            "L1": 0,
            "L2_files": 0,
            "L2_memories": 0,
            "L3_events": 0,
            "L4_memories": 0,
            "L5_concepts": 0,
            "total_size_kb": 0
        }
        
        # L1
        l1_file = SMART_DIR / "L1_working" / "session.json"
        if l1_file.exists():
            stats["L1"] = l1_file.stat().st_size
        
        # L2
        l2_dir = SMART_DIR / "L2_short_term"
        if l2_dir.exists():
            stats["L2_files"] = len(list(l2_dir.glob("*.json")))
            for f in l2_dir.glob("*.json"):
                stats["total_size_kb"] += f.stat().st_size / 1024
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        data = json.load(fp)
                        stats["L2_memories"] += len(data.get("memories", []))
                except:
                    pass
        
        # L3
        l3_dir = SMART_DIR / "L3_mid_term" / "events"
        if l3_dir.exists():
            stats["L3_events"] = len(list(l3_dir.glob("*.json")))
        
        # L4
        l4_file = SMART_DIR / "L4_long_term" / "memories.json"
        if l4_file.exists():
            with open(l4_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats["L4_memories"] = len(data.get("memories", []))
            stats["total_size_kb"] += l4_file.stat().st_size / 1024
        
        # L5
        l5_file = SMART_DIR / "L5_semantic" / "concepts.json"
        if l5_file.exists():
            with open(l5_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats["L5_concepts"] = len(data.get("concepts", []))
        
        stats["total_size_kb"] = round(stats["total_size_kb"], 2)
        
        return stats


def get_cleanup_manager(ttl_days: int = 7) -> MemoryCleanup:
    """获取清理管理器"""
    return MemoryCleanup(ttl_days)


if __name__ == "__main__":
    import sys
    
    # 检查是否是自动模式
    auto_mode = "--auto" in sys.argv
    dry_run = "--dry-run" in sys.argv
    
    cleanup = get_cleanup_manager()
    
    if auto_mode:
        print("[自动清理] 开始执行清理...")
        report = cleanup.cleanup(dry_run=dry_run)
        
        print(f"\n[清理报告]")
        print(f"  时间: {report['timestamp']}")
        print(f"  模式: {'模拟' if dry_run else '实际'}")
        print(f"  L2文件删除: {len(report['L2_deleted'])}")
        print(f"  L2升级L3: {len(report['L2_promoted'])}")
        print(f"  L3事件删除: {len(report['L3_deleted'])}")
        print(f"  总计释放: {report['total_freed']} 项")
        
        if report['errors']:
            print(f"  错误: {report['errors']}")
    else:
        # 显示存储统计
        stats = cleanup.get_storage_stats()
        print("[存储统计]")
        print(f"  L1 (工作记忆): {stats['L1']} bytes")
        print(f"  L2 (短期记忆): {stats['L2_files']} 文件, {stats['L2_memories']} 条")
        print(f"  L3 (中期记忆): {stats['L3_events']} 事件")
        print(f"  L4 (长期记忆): {stats['L4_memories']} 条")
        print(f"  L5 (语义记忆): {stats['L5_concepts']} 概念")
        print(f"  总大小: {stats['total_size_kb']} KB")
        
        print("\n[使用方法]")
        print("  python cleanup.py --auto      # 自动清理")
        print("  python cleanup.py --dry-run  # 模拟清理")
