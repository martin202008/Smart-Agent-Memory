#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarvis 多模态记忆系统
支持图片、语音、视频等多媒体记忆
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import base64

# 基础路径
MULTIMODAL_DIR = Path(__file__).parent
MEDIA_DIR = MULTIMODAL_DIR / "media"
METADATA_FILE = MULTIMODAL_DIR / "multimodal_index.json"

# 确保目录存在
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


class MultimodalMemory:
    """多模态记忆管理器"""
    
    def __init__(self):
        self.media_dir = MEDIA_DIR
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """加载元数据"""
        if METADATA_FILE.exists():
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "images": [],
            "audio": [],
            "video": [],
            "documents": [],
            "total_count": 0
        }
    
    def _save_metadata(self):
        """保存元数据"""
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def add_image(self, image_path: str, description: str = "", tags: List[str] = None) -> Dict:
        """
        添加图片记忆
        
        Args:
            image_path: 图片文件路径
            description: 图片描述
            tags: 标签
            
        Returns:
            添加结果
        """
        source = Path(image_path)
        
        if not source.exists():
            return {"success": False, "error": "文件不存在"}
        
        # 生成唯一ID
        media_id = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{source.stem}"
        
        # 复制文件
        ext = source.suffix.lower()
        dest_path = self.media_dir / f"{media_id}{ext}"
        shutil.copy2(source, dest_path)
        
        # 提取信息
        file_size = dest_path.stat().st_size
        
        # 添加元数据
        media_entry = {
            "id": media_id,
            "filename": dest_path.name,
            "original_name": source.name,
            "description": description,
            "tags": tags or [],
            "type": "image",
            "size": file_size,
            "created_at": datetime.now().isoformat()
        }
        
        self.metadata["images"].append(media_entry)
        self.metadata["total_count"] += 1
        self._save_metadata()
        
        return {
            "success": True,
            "media_id": media_id,
            "path": str(dest_path),
            "size": file_size
        }
    
    def add_audio(self, audio_path: str, transcript: str = "", tags: List[str] = None) -> Dict:
        """添加语音记忆"""
        source = Path(audio_path)
        
        if not source.exists():
            return {"success": False, "error": "文件不存在"}
        
        media_id = f"aud_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{source.stem}"
        
        ext = source.suffix.lower()
        dest_path = self.media_dir / f"{media_id}{ext}"
        shutil.copy2(source, dest_path)
        
        file_size = dest_path.stat().st_size
        
        media_entry = {
            "id": media_id,
            "filename": dest_path.name,
            "original_name": source.name,
            "transcript": transcript,
            "tags": tags or [],
            "type": "audio",
            "size": file_size,
            "duration": None,  # 可以后续提取
            "created_at": datetime.now().isoformat()
        }
        
        self.metadata["audio"].append(media_entry)
        self.metadata["total_count"] += 1
        self._save_metadata()
        
        return {
            "success": True,
            "media_id": media_id,
            "path": str(dest_path),
            "size": file_size
        }
    
    def add_video(self, video_path: str, description: str = "", tags: List[str] = None) -> Dict:
        """添加视频记忆"""
        source = Path(video_path)
        
        if not source.exists():
            return {"success": False, "error": "文件不存在"}
        
        media_id = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{source.stem}"
        
        ext = source.suffix.lower()
        dest_path = self.media_dir / f"{media_id}{ext}"
        shutil.copy2(source, dest_path)
        
        file_size = dest_path.stat().st_size
        
        media_entry = {
            "id": media_id,
            "filename": dest_path.name,
            "original_name": source.name,
            "description": description,
            "tags": tags or [],
            "type": "video",
            "size": file_size,
            "created_at": datetime.now().isoformat()
        }
        
        self.metadata["video"].append(media_entry)
        self.metadata["total_count"] += 1
        self._save_metadata()
        
        return {
            "success": True,
            "media_id": media_id,
            "path": str(dest_path),
            "size": file_size
        }
    
    def search_by_tag(self, tag: str) -> List[Dict]:
        """按标签搜索"""
        results = []
        
        for media_type in ["images", "audio", "video", "documents"]:
            for item in self.metadata.get(media_type, []):
                if tag in item.get("tags", []):
                    results.append(item)
        
        return results
    
    def get_recent(self, media_type: str = None, limit: int = 10) -> List[Dict]:
        """获取最近的多媒体记忆"""
        all_items = []
        
        if media_type:
            items = self.metadata.get(media_type, [])
            all_items.extend([(item, item.get("created_at", "")) for item in items])
        else:
            for mtype in ["images", "audio", "video", "documents"]:
                for item in self.metadata.get(mtype, []):
                    all_items.append((item, item.get("created_at", "")))
        
        # 按时间排序
        all_items.sort(key=lambda x: x[1], reverse=True)
        
        return [item for item, _ in all_items[:limit]]
    
    def delete(self, media_id: str) -> bool:
        """删除多媒体记忆"""
        # 查找
        for media_type in ["images", "audio", "video", "documents"]:
            for i, item in enumerate(self.metadata.get(media_type, [])):
                if item["id"] == media_id:
                    # 删除文件
                    file_path = self.media_dir / item["filename"]
                    if file_path.exists():
                        file_path.unlink()
                    
                    # 删除元数据
                    del self.metadata[media_type][i]
                    self.metadata["total_count"] -= 1
                    self._save_metadata()
                    
                    return True
        
        return False
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_size = 0
        
        stats = {
            "images": {
                "count": len(self.metadata.get("images", [])),
                "size": 0
            },
            "audio": {
                "count": len(self.metadata.get("audio", [])),
                "size": 0
            },
            "video": {
                "count": len(self.metadata.get("video", [])),
                "size": 0
            },
            "total": self.metadata.get("total_count", 0)
        }
        
        for media_type in ["images", "audio", "video"]:
            for item in self.metadata.get(media_type, []):
                stats[media_type]["size"] += item.get("size", 0)
                total_size += item.get("size", 0)
        
        stats["total_size"] = total_size
        
        return stats


def get_multimodal_memory() -> MultimodalMemory:
    """获取多模态记忆管理器"""
    return MultimodalMemory()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=== 多模态记忆测试 ===\n")
    
    mm = get_multimodal_memory()
    
    # 查看统计
    stats = mm.get_stats()
    print("[统计]")
    print(f"  图片: {stats['images']['count']} 个")
    print(f"  音频: {stats['audio']['count']} 个")
    print(f"  视频: {stats['video']['count']} 个")
    print(f"  总计: {stats['total']} 个")
    
    print("\n[使用方法]")
    print("""
from memory.smart.multimodal import get_multimodal_memory

mm = get_multimodal_memory()

# 添加图片
mm.add_image("photo.jpg", "用户发来的图片", ["照片", "重要"])

# 添加语音
mm.add_audio("recording.mp3", "语音转文字内容", ["语音", "对话"])

# 搜索
results = mm.search_by_tag("重要")

# 获取最近
recent = mm.get_recent("images", 5)
""")
