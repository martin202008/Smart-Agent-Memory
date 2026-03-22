"""
社区知识导入器
从 MEMORY.md 和每日日志中提取有价值的内容，导入 Smart-Memory

触发场景：
  1. 逛完 Moltbook 社区后，运行导入
  2. cron 定期检查新内容
  3. 手动调用

用法:
  python import_knowledge.py [--since "2026-03-20"]
  python import_knowledge.py --from-memory-md  # 从 MEMORY.md 导入
  python import_knowledge.py --from-daily      # 从每日日志导入
"""

import os
import re
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent.parent  # workspace/
MEMORY_MD = WORKSPACE / "MEMORY.md"
DAILY_DIR = WORKSPACE / "memory"
SMART_DIR = Path(__file__).parent  # memory/smart/


# 从 MEMORY.md 中提取有价值内容的模式
# 这些模式表示「可导入的知识点」
VALUABLE_PATTERNS = [
    # 1. 具体知识/经验
    (r"[Aa]gent[:：] (.+)", "Agent经验"),
    (r"Skill[:：] (.+)", "Skill使用"),
    (r"教训[:：](.+)", "教训"),
    (r"经验[:：](.+)", "经验"),
    (r"技巧[:：](.+)", "技巧"),
    (r"方法[:：](.+)", "方法"),
    
    # 2. 决策记录
    (r"决策[:：](.+)", "决策"),
    (r"采用了?(.+?)(?:方案|方法|策略)", "方案采用"),
    (r"选择了?(.+?)(?:方案|方法|策略)", "方案采用"),
    
    # 3. 踩坑记录（高价值）
    (r"踩坑[:：](.+)", "踩坑"),
    (r"坑[：:](.+)", "踩坑"),
    (r"注意[:：](.+)", "注意事项"),
    (r"警告[:：](.+)", "警告"),
    
    # 4. 工具使用
    (r"用 (.+?) (?:实现|完成|做)", "工具使用"),
    (r"调用 (.+?) API", "API调用"),
    (r"使用 (.+?) (?:工具|脚本|命令)", "工具使用"),
    
    # 5. 配置/参数
    (r"(?:配置|设置)[:：](.+)", "配置"),
    (r"(?:参数|选项)[:：](.+)", "配置"),
    
    # 6. Moltbook 洞察
    (r"Moltbook.*?[:：](.+)", "社区洞察"),
    (r"学[一到]?(.+?)[。，]", "学习内容"),
    (r"社区.*?洞察[:：](.+)", "社区洞察"),
]

# 标签
TAG_MAP = {
    "Agent经验": ["Agent", "经验"],
    "Skill使用": ["Skill", "工具"],
    "教训": ["教训", "重要"],
    "经验": ["经验", "重要"],
    "技巧": ["技巧", "技能"],
    "方法": ["方法", "技能"],
    "决策": ["决策", "重要"],
    "方案采用": ["方案", "决策"],
    "踩坑": ["踩坑", "教训", "重要"],
    "注意事项": ["注意事项", "重要"],
    "警告": ["警告", "重要"],
    "工具使用": ["工具", "使用"],
    "API调用": ["API", "开发"],
    "配置": ["配置", "技术"],
    "社区洞察": ["Moltbook", "社区"],
    "学习内容": ["学习", "成长"],
}


def parse_memory_md() -> List[Dict]:
    """从 MEMORY.md 解析有价值的内容"""
    if not MEMORY_MD.exists():
        return []
    
    with open(MEMORY_MD, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    current_section = ""
    
    lines = content.split('\n')
    for line in lines:
        # 章节标题
        if line.startswith('## '):
            current_section = line.replace('## ', '').strip()
        
        # 跳过无意义行
        if not line.strip() or len(line.strip()) < 10:
            continue
        
        # 检查是否符合价值模式
        for pattern, tag_type in VALUABLE_PATTERNS:
            match = re.search(pattern, line)
            if match:
                value_text = match.group(1).strip()
                if len(value_text) > 5:  # 过滤太短的
                    entries.append({
                        "content": value_text,
                        "section": current_section,
                        "tag_type": tag_type,
                        "source": "MEMORY.md",
                        "original_line": line.strip()
                    })
                break  # 一个模式匹配到就跳到下一行
    
    return entries


def parse_daily_logs(since_days: int = 3) -> List[Dict]:
    """从每日日志中解析有价值的内容"""
    since = datetime.now() - timedelta(days=since_days)
    entries = []
    
    if not DAILY_DIR.exists():
        return entries
    
    for log_file in sorted(DAILY_DIR.glob("*.md"), reverse=True):
        try:
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
            if file_date < since:
                break
        except:
            continue
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for line in content.split('\n'):
            if len(line.strip()) < 10:
                continue
            
            for pattern, tag_type in VALUABLE_PATTERNS:
                match = re.search(pattern, line)
                if match:
                    value_text = match.group(1).strip()
                    if len(value_text) > 5:
                        entries.append({
                            "content": value_text,
                            "section": log_file.stem,
                            "tag_type": tag_type,
                            "source": f"daily/{log_file.name}",
                            "original_line": line.strip()
                        })
                    break
    
    return entries


def deduplicate_with_l4(new_entries: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    与 L4 中的现有记忆去重
    
    Returns:
        (to_import, duplicates) - 待导入的和重复的
    """
    l4_file = SMART_DIR / "L4_long_term" / "memories.json"
    
    existing_contents = set()
    if l4_file.exists():
        with open(l4_file, 'r', encoding='utf-8') as f:
            l4_data = json.load(f)
            for mem in l4_data.get("memories", []):
                existing_contents.add(mem.get('content', ''))
    
    to_import, duplicates = [], []
    for entry in new_entries:
        # 检查完全相同
        if entry['content'] in existing_contents:
            duplicates.append(entry)
        else:
            to_import.append(entry)
    
    return to_import, duplicates


def import_to_l4(entries: List[Dict], importance_hint: int = 5) -> int:
    """
    将知识条目导入到 Smart-Memory L4
    
    Args:
        entries: 待导入条目
        importance_hint: 基础重要性分数
    
    Returns:
        实际导入数量
    """
    if not entries:
        print("  没有需要导入的内容")
        return 0
    
    # 动态调整重要性
    HIGH_VALUE_TAGS = {"踩坑", "教训", "警告", "决策", "注意事项"}
    
    l4_file = SMART_DIR / "L4_long_term" / "memories.json"
    
    if l4_file.exists():
        with open(l4_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"memories": []}
    
    count = 0
    for entry in entries:
        tag_type = entry['tag_type']
        tags = TAG_MAP.get(tag_type, [tag_type])
        if tag_type in HIGH_VALUE_TAGS:
            importance = max(importance_hint, 7)  # 高价值内容最低7分
        else:
            importance = max(importance_hint - 1, 3)
        
        # 导入时提取判例模板
        from case_template import CaseTemplateExtractor
        extractor = CaseTemplateExtractor()
        case = extractor.extract(entry['content'])
        
        memory_entry = {
            "id": len(data["memories"]) + 1,
            "content": entry['content'],
            "tags": tags + [entry['source']],
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "importance": importance,
            "base_importance": importance / 10.0,
            "lifecycle_status": "active",
            "case_template": case.to_dict() if case else None,
            "has_correction": case.has_correction if case else False,
            "case_confidence": round(case.confidence, 3) if case else 0.0,
            "imported_from": entry['source'],
            "import_section": entry.get('section', ''),
        }
        
        data["memories"].append(memory_entry)
        count += 1
        print(f"  + {entry['content'][:50]}... [imported, score={importance}]")
    
    with open(l4_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return count


def main():
    import argparse
    parser = argparse.ArgumentParser(description='社区知识导入器')
    parser.add_argument('--since', default=None, help='起始日期 YYYY-MM-DD')
    parser.add_argument('--from-memory-md', action='store_true', help='从MEMORY.md导入')
    parser.add_argument('--from-daily', action='store_true', help='从每日日志导入')
    parser.add_argument('--all', action='store_true', help='导入所有来源')
    args = parser.parse_args()
    
    print("=== 社区知识导入器 ===\n")
    
    entries = []
    
    if args.all or args.from_memory_md:
        print("[1/2] 从 MEMORY.md 解析...")
        md_entries = parse_memory_md()
        print(f"  找到 {len(md_entries)} 条有价值内容")
        entries.extend(md_entries)
    
    if args.all or args.from_daily:
        days = 3
        if args.since:
            since = datetime.strptime(args.since, "%Y-%m-%d")
            days = (datetime.now() - since).days
        print(f"\n[2/2] 从每日日志解析 (最近{days}天)...")
        daily_entries = parse_daily_logs(since_days=days)
        print(f"  找到 {len(daily_entries)} 条有价值内容")
        entries.extend(daily_entries)
    
    if not entries:
        print("没有找到内容")
        return
    
    print(f"\n共 {len(entries)} 条待检查")
    
    # 去重
    to_import, duplicates = deduplicate_with_l4(entries)
    print(f"去重后：{len(to_import)} 待导入，{len(duplicates)} 重复")
    
    if duplicates:
        print(f"\n重复内容（已存在于L4）:")
        for d in duplicates[:5]:
            print(f"  - {d['content'][:50]}...")
    
    if to_import:
        print(f"\n开始导入 {len(to_import)} 条到 L4...")
        count = import_to_l4(to_import)
        print(f"\n导入完成: {count} 条")
    else:
        print("\n没有需要导入的新内容")


if __name__ == "__main__":
    main()
