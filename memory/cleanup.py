#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart-Memory Scheduled Cleanup Script
Runs daily to organize memories, upgrade decisions, generate reports
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add path
BASE_DIR = Path(__file__).parent  # memory/smart
sys.path.insert(0, str(BASE_DIR))

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def cleanup_short_term():
    """Clean up expired short-term memories"""
    print("\n[1/4] Cleaning short-term memories...")
    
    L2_DIR = BASE_DIR / "L2_short_term"
    cutoff = datetime.now() - timedelta(days=7)
    cleaned = 0
    
    for f in L2_DIR.glob("*.json"):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                f.unlink()
                cleaned += 1
        except Exception as e:
            print(f"  Failed: {f.name} - {e}")
    
    print(f"  Cleaned {cleaned} expired files")


def check_mid_term_upgrades():
    """Check L3 upgrades"""
    print("\n[2/4] Checking L3 mid-term memories...")
    
    L3_DIR = BASE_DIR / "L3_mid_term" / "events"
    events = list(L3_DIR.glob("*.json"))
    
    print(f"  L3 events: {len(events)}")
    
    # L4 upgrade threshold check
    L4_DIR = BASE_DIR / "L4_long_term"
    l4_file = L4_DIR / "memories.json"

    # 刷新所有L4记忆的lifecycle状态（衰减引擎）
    try:
        sys.path.insert(0, str(BASE_DIR))
        from memory_manager import get_memory_manager
        mm = get_memory_manager()
        mm.get_long_term_memories(refresh_status=True, use_access_count=False)
        print(f"  [Decay] L4 lifecycle status refreshed")
    except Exception as e:
        print(f"  [Decay] Refresh skipped: {e}")
    
    if l4_file.exists():
        with open(l4_file, 'r', encoding='utf-8') as f:
            l4_data = json.load(f)
    else:
        l4_data = {"memories": []}
    
    for event_file in events[:5]:
        with open(event_file, 'r', encoding='utf-8') as f:
            event = json.load(f)
        
        score = event.get("importance_score", 0)
        if score >= 8 and not any(m.get("source") == event_file.name for m in l4_data.get("memories", [])):
            # Upgrade to L4
            memory_entry = {
                "id": len(l4_data["memories"]) + 1,
                "content": event.get("original_content", ""),
                "tags": ["auto_upgraded", "high_importance"],
                "source": event_file.name,
                "created_at": datetime.now().isoformat(),
                "access_count": 0
            }
            l4_data["memories"].append(memory_entry)
            print(f"  Upgraded to L4: {event_file.name}")
    
    with open(l4_file, 'w', encoding='utf-8') as f:
        json.dump(l4_data, f, ensure_ascii=False, indent=2)


def update_long_term_stats():
    """Update long-term memory stats"""
    print("\n[3/4] Updating L4 stats...")
    
    L4_DIR = BASE_DIR / "L4_long_term"
    l4_file = L4_DIR / "memories.json"
    
    if l4_file.exists():
        with open(l4_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = len(data.get("memories", []))
        print(f"  L4 memories: {count}")
    else:
        print("  L4 memories: 0")


def generate_report():
    """Generate cleanup report"""
    print("\n[4/4] Generating report...")
    
    l4_file = BASE_DIR / "L4_long_term" / "memories.json"
    l4_count = 0
    if l4_file.exists():
        with open(l4_file, 'r', encoding='utf-8') as f:
            l4_data = json.load(f)
            l4_count = len(l4_data.get("memories", []))
    
    report = {
        "run_time": datetime.now().isoformat(),
        "L1_working": "in_memory",
        "L2_short_term": len(list((BASE_DIR / "L2_short_term").glob("*.json"))),
        "L3_mid_term": len(list((BASE_DIR / "L3_mid_term" / "events").glob("*.json"))),
        "L4_long_term": l4_count,
        "L5_semantic": len(list((BASE_DIR / "L5_semantic").glob("*.json"))),
    }
    
    report_file = BASE_DIR / "cleanup_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"  Report: cleanup_report.json")
    return report


def cleanup_l3_events():
    """
    检查 L3 中期记忆的衰减状态
    - active: 保留
    - archived: 保持原样（可被搜索但不加权重）
    - deleted: 标记，待确认后删除
    """
    print("\n[NEW] Checking L3 lifecycle decay...")
    
    try:
        sys.path.insert(0, str(BASE_DIR))
        from memory_manager import get_memory_manager
        # 直接导入脚本逻辑（避免循环import）
    except:
        pass
    
    # 使用简化逻辑（避免依赖）
    import math
    L3_DIR = BASE_DIR / "L3_mid_term" / "events"
    L3_ARCHIVE_DIR = BASE_DIR / "L3_mid_term" / "archive"
    L3_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    events = list(L3_DIR.glob("*.json"))
    active, archived, deleted = [], [], []
    
    for event_file in events:
        try:
            with open(event_file, 'r', encoding='utf-8') as f:
                event = json.load(f)
            
            created_at = event.get('promoted_at', event.get('created_at', datetime.now().isoformat()))
            importance = event.get('importance_score', 0)
            base_importance = importance / 10.0
            
            # 计算衰减
            try:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:0'))
                days = (datetime.now() - created.replace(tzinfo=None)).total_seconds() / 86400
                recency = math.exp(-0.01 * days)
            except:
                recency = 0.5
            
            access_factor = 0.3 + 0.7 * math.log(2) / math.log(101)
            decay_score = base_importance * recency * access_factor
            
            if decay_score >= 0.2:
                status = "active"
                active.append((event_file, event))
            elif decay_score >= 0.05:
                status = "archived"
                archived.append((event_file, event))
            else:
                status = "deleted"
                deleted.append((event_file, event))
            
            event['decay_score'] = round(decay_score, 4)
            event['lifecycle_status'] = status
            
            with open(event_file, 'w', encoding='utf-8') as f:
                json.dump(event, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  L3 error: {event_file.name} - {e}")
    
    print(f"  L3 events: total={len(events)}, active={len(active)}, archived={len(archived)}, deleted={len(deleted)}")
    
    # 将 deleted L3 移到归档
    for event_file, event in deleted:
        archive_name = event_file.stem + "_deleted.json"
        archive_path = L3_ARCHIVE_DIR / archive_name
        event['deleted_at'] = datetime.now().isoformat()
        try:
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(event, f, ensure_ascii=False, indent=2)
            event_file.unlink()
            print(f"  Deleted L3: {event_file.name}")
        except Exception as e:
            print(f"  Failed to archive L3: {e}")
    
    return len(active), len(archived), len(deleted)


def cleanup_archived_memories():
    """
    处理 L4 中 archived/deleted 状态的记忆
    - archived -> 移入独立归档文件（可搜索但不参与主文件）
    - deleted  -> 移入待删除队列（超过30天确认删除）
    """
    print("\n[NEW] Processing archived/deleted L4 memories...")
    
    L4_DIR = BASE_DIR / "L4_long_term"
    l4_file = L4_DIR / "memories.json"
    ARCHIVE_DIR = L4_DIR / "archive"
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    if not l4_file.exists():
        print("  L4 file not found, skipping")
        return
    
    with open(l4_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_memories = data.get("memories", [])
    active = [m for m in all_memories if m.get("lifecycle_status") == "active"]
    archived = [m for m in all_memories if m.get("lifecycle_status") == "archived"]
    deleted = [m for m in all_memories if m.get("lifecycle_status") == "deleted"]
    
    print(f"  Active: {len(active)} | Archived: {len(archived)} | Deleted: {len(deleted)}")
    
    # 处理 archived：移入归档文件
    pending_file = ARCHIVE_DIR / "pending_delete.json"
    
    if archived:
        archive_file = ARCHIVE_DIR / f"archived_{datetime.now().strftime('%Y-%m-%d')}.json"
        archived_data = {"archived_at": datetime.now().isoformat(), "memories": archived}
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(archived_data, f, ensure_ascii=False, indent=2)
        print(f"  Archived {len(archived)} memories -> {archive_file.name}")
    
    # 处理 deleted：移入 pending_delete 文件
    if deleted:
        existing_pending = []
        if pending_file.exists():
            with open(pending_file, 'r', encoding='utf-8') as f:
                existing_pending = json.load(f).get("memories", [])
        
        # 合并，标注删除时间
        for mem in deleted:
            mem["deleted_at"] = datetime.now().isoformat()
        all_pending = existing_pending + deleted
        
        with open(pending_file, 'w', encoding='utf-8') as f:
            json.dump({"memories": all_pending, "updated_at": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
        print(f"  Moved {len(deleted)} deleted memories -> pending_delete.json")
    
    # 重写主文件，只保留 active
    data["memories"] = active
    with open(l4_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  L4 main file now has {len(active)} active memories")
    
    # 清理超过30天的 pending_delete
    if pending_file.exists():
        with open(pending_file, 'r', encoding='utf-8') as f:
            pending_data = json.load(f)
        
        remaining = []
        confirmed_deleted = 0
        for mem in pending_data.get("memories", []):
            deleted_at = datetime.fromisoformat(mem.get("deleted_at", "2000-01-01"))
            if (datetime.now() - deleted_at).days > 30:
                confirmed_deleted += 1
            else:
                remaining.append(mem)
        
        if confirmed_deleted > 0:
            pending_data["memories"] = remaining
            with open(pending_file, 'w', encoding='utf-8') as f:
                json.dump(pending_data, f, ensure_ascii=False, indent=2)
            print(f"  Confirmed deleted {confirmed_deleted} memories (30+ days old)")
    
    return len(archived), len(deleted)


def compact_long_term_memories():
    """
    记忆压缩（参考 Memory Guardian 思路）
    1. 检查 MEMORY.md 大小，超过阈值则归档旧内容
    2. 识别并合并重复内容
    3. 将已归档内容移至 archive 目录
    """
    print("\n[5/5] Running memory compaction...")
    
    WORKSPACE_DIR = BASE_DIR.parent.parent  # workspace/
    MEMORY_MD = WORKSPACE_DIR / "MEMORY.md"
    ARCHIVE_DIR = L4_DIR = BASE_DIR / "L4_long_term"
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    if not MEMORY_MD.exists():
        print("  MEMORY.md not found, skipping")
        return
    
    size_kb = MEMORY_MD.stat().st_size / 1024
    target_kb = 10  # 目标不超过10KB
    
    if size_kb <= target_kb:
        print("  Size OK, no compaction needed")
        return
    
    print(f"  Size exceeds target, archiving older entries...")
    
    # 读取当前 MEMORY.md
    with open(MEMORY_MD, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到非头部内容的部分（假设前20行是头部）
    # 保留头部和最近的内容
    keep_lines = []
    archived_count = 0
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    archive_content = []
    is_archived = False
    
    for line in lines:
        # 检测日期标记
        if "## " in line and any(marker in line for marker in ["## 20", "## MEMORY"]):
            date_marker = line.split("## ")[-1].strip()[:10]
            if date_marker < cutoff_date and date_marker.startswith("20"):
                is_archived = True
        
        if is_archived:
            archive_content.append(line)
            archived_count += 1
        else:
            keep_lines.append(line)
    
    if archive_content:
        # 保存归档
        archive_file = ARCHIVE_DIR / f"archive_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(archive_file, 'w', encoding='utf-8') as f:
            f.write("# 归档记忆 (来自 MEMORY.md)\n")
            f.write(f"# 归档时间: {datetime.now().isoformat()}\n\n")
            f.writelines(archive_content)
        print(f"  Archived {archived_count} lines to {archive_file.name}")
        
        # 重写 MEMORY.md
        with open(MEMORY_MD, 'w', encoding='utf-8') as f:
            f.writelines(keep_lines)
        
        new_size_kb = MEMORY_MD.stat().st_size / 1024
        print(f"  MEMORY.md reduced to {new_size_kb:.1f} KB")
    else:
        print("  No archiveable content found")


def main():
    print("=" * 50)
    print("Smart-Memory Scheduled Cleanup + Compaction")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        cleanup_short_term()
        check_mid_term_upgrades()  # 同时刷新了L4 lifecycle
        cleanup_l3_events()  # 新增: L3 events 衰减检查
        cleanup_archived_memories()  # 处理 archived/deleted
        compact_long_term_memories()  # MEMORY.md 压缩
        update_long_term_stats()
        report = generate_report()
        
        print("\n" + "=" * 50)
        print("Cleanup Complete!")
        print(f"L2: {report['L2_short_term']} | L3: {report['L3_mid_term']} | L4: {report['L4_long_term']}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
