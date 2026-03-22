"""
MEMORY.md 超限自动压缩脚本
当 MEMORY.md 超过阈值时自动归档旧内容

用法（每次写入 MEMORY.md 后调用）:
  python auto_compact.py [--check-only]

--check-only: 只检查，不执行压缩
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent  # memory/smart
WORKSPACE_DIR = BASE_DIR.parent.parent  # workspace/
MEMORY_MD = WORKSPACE_DIR / "MEMORY.md"
ARCHIVE_DIR = BASE_DIR / "L4_long_term" / "archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# 阈值：超过此大小（KB）触发压缩
SIZE_THRESHOLD_KB = 15  # 比 config 里的 target 稍宽松，避免频繁压缩
TARGET_SIZE_KB = 10  # 压缩后目标大小

# MEMORY.md 头部行数（跳过这些行不压缩）
SKIP_HEADER_LINES = 25


def get_memory_md_size():
    if not MEMORY_MD.exists():
        return 0
    return MEMORY_MD.stat().st_size / 1024


def should_compact():
    """检查是否需要压缩"""
    size = get_memory_md_size()
    return size > SIZE_THRESHOLD_KB


def compact_memory_md():
    """压缩 MEMORY.md：归档30天前的旧内容"""
    if not MEMORY_MD.exists():
        return False, "MEMORY.md not found"
    
    size = get_memory_md_size()
    if size <= SIZE_THRESHOLD_KB:
        return False, f"Size {size:.1f}KB <= threshold, no need"
    
    with open(MEMORY_MD, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if len(lines) <= SKIP_HEADER_LINES:
        return False, "File too short, no content to archive"
    
    # 保留头部
    header = lines[:SKIP_HEADER_LINES]
    content = lines[SKIP_HEADER_LINES:]
    
    # 30天前的日期标记
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # 找到要归档的内容（旧的 ## 日期章节）
    keep_lines = list(header)
    archive_lines = []
    in_old_section = False
    old_sections_count = 0
    
    for line in content:
        # 检测日期章节标记
        if "## " in line and line.strip().startswith("## "):
            date_part = line.strip().split("## ")[-1].strip()[:10]
            if date_part.startswith("20") and date_part < cutoff_date:
                in_old_section = True
                old_sections_count += 1
            else:
                in_old_section = False
        
        if in_old_section:
            archive_lines.append(line)
        else:
            keep_lines.append(line)
    
    if not archive_lines:
        return False, "No old content to archive"
    
    archived_chars = sum(len(l) for l in archive_lines)
    
    # 保存归档文件
    archive_file = ARCHIVE_DIR / f"MEMORY_archive_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(archive_file, 'w', encoding='utf-8') as f:
        f.write(f"# MEMORY.md 归档内容\n")
        f.write(f"# 归档时间: {datetime.now().isoformat()}\n")
        f.write(f"# 阈值: {SIZE_THRESHOLD_KB}KB, 原始大小: {size:.1f}KB\n")
        f.write(f"# 归档章节数: {old_sections_count}\n\n")
        f.writelines(archive_lines)
    
    # 重写主文件
    with open(MEMORY_MD, 'w', encoding='utf-8') as f:
        f.writelines(keep_lines)
    
    new_size = get_memory_md_size()
    return True, f"Archived {len(archive_lines)} lines ({archived_chars} chars) from {old_sections_count} sections -> {archive_file.name}, reduced {size:.1f}KB -> {new_size:.1f}KB"


if __name__ == "__main__":
    check_only = "--check-only" in sys.argv
    
    size = get_memory_md_size()
    print(f"MEMORY.md: {size:.1f}KB / threshold: {SIZE_THRESHOLD_KB}KB")
    
    if check_only:
        if should_compact():
            print("Size exceeds threshold, compaction recommended")
        else:
            print("Size OK, no compaction needed")
    else:
        if should_compact():
            print("Compacting...")
            ok, msg = compact_memory_md()
            print(f"Result: {msg}")
        else:
            print("No compaction needed")
