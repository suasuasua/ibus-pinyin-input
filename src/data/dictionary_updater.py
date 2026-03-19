#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 输入法词库更新器
负责词库的增量更新和维护
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class DictionaryUpdater:
    """词库更新器 - 提供增量更新功能"""
    
    def __init__(self, cache_dir: str = '.ibus_cache'):
        """初始化词库更新器
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = cache_dir
        self.json_path = os.path.join(cache_dir, 'dictionary.json')
        self.sqlite_path = os.path.join(cache_dir, 'dictionary.db')
    
    def update_word(self, word: str, pinyin: str = None,
                    frequency: int = None, tags: List[str] = None) -> bool:
        """更新词库中的词
        
        Args:
            word: 词
            pinyin: 拼音（可选）
            frequency: 频率（可选）
            tags: 标签（可选）
            
        Returns:
            是否成功更新
        """
        # 加载现有词库
        words = self.load_json()
        
        # 查找并更新词
        for i, w in enumerate(words):
            if w.get('word') == word:
                if pinyin is not None:
                    w['pinyin'] = pinyin
                if frequency is not None:
                    w['frequency'] = frequency
                if tags is not None:
                    w['tags'] = tags
                words[i] = w
                break
        else:
            # 词不存在，添加新词
            words.append({
                'word': word,
                'pinyin': pinyin or '',
                'frequency': frequency or 1,
                'tags': tags or []
            })
        
        # 保存更新
        return self.save_json(words)
    
    def add_word(self, word: str, pinyin: str = None,
                 frequency: int = 1, tags: List[str] = None) -> bool:
        """添加新词
        
        Args:
            word: 词
            pinyin: 拼音（可选）
            frequency: 频率（可选，默认 1）
            tags: 标签（可选）
            
        Returns:
            是否成功添加
        """
        # 加载现有词库
        words = self.load_json()
        
        # 检查是否已存在
        for w in words:
            if w.get('word') == word:
                print(f"⚠️  词已存在：{word}")
                return False
        
        # 添加新词
        words.append({
            'word': word,
            'pinyin': pinyin or '',
            'frequency': frequency,
            'tags': tags or []
        })
        
        # 保存更新
        return self.save_json(words)
    
    def remove_word(self, word: str) -> bool:
        """删除词
        
        Args:
            word: 要删除的词
            
        Returns:
            是否成功删除
        """
        # 加载现有词库
        words = self.load_json()
        
        # 查找并删除词
        original_length = len(words)
        words = [w for w in words if w.get('word') != word]
        
        if len(words) < original_length:
            # 保存更新
            return self.save_json(words)
        
        print(f"⚠️  词不存在或未找到：{word}")
        return False
    
    def save_json(self, words: List[Dict]) -> bool:
        """保存词库到 JSON 文件"""
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(words, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存失败：{e}")
            return False
    
    def load_json(self) -> List[Dict]:
        """加载词库 JSON"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def batch_update(self, updates: List[Dict]) -> int:
        """批量更新词库
        
        Args:
            updates: 更新列表，每个元素包含 word 和更新字段
            
        Returns:
            成功更新的词数
        """
        words = self.load_json()
        updated_count = 0
        
        for update in updates:
            word = update.get('word')
            if not word:
                continue
            
            # 查找并更新
            for i, w in enumerate(words):
                if w.get('word') == word:
                    if 'pinyin' in update:
                        w['pinyin'] = update['pinyin']
                    if 'frequency' in update:
                        w['frequency'] = update['frequency']
                    if 'tags' in update:
                        w['tags'] = update['tags']
                    words[i] = w
                    updated_count += 1
                    break
        
        # 保存更新
        if self.save_json(words):
            return updated_count
        return 0
    
    def batch_add(self, words_to_add: List[Dict]) -> int:
        """批量添加词
        
        Args:
            words_to_add: 词列表
            
        Returns:
            成功添加的词数
        """
        words = self.load_json()
        added_count = 0
        
        for word_info in words_to_add:
            word = word_info.get('word')
            if not word:
                continue
            
            # 检查是否已存在
            for w in words:
                if w.get('word') == word:
                    break
            else:
                # 添加新词
                words.append(word_info)
                added_count += 1
        
        # 保存更新
        if self.save_json(words):
            return added_count
        return 0
    
    def backup(self, backup_dir: str = 'ibus_backups') -> str:
        """创建词库备份
        
        Args:
            backup_dir: 备份目录
            
        Returns:
            备份文件路径
        """
        import shutil
        import os
        
        backup_dir = os.path.join(self.cache_dir, backup_dir)
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'dictionary_{timestamp}.json'
        backup_path = os.path.join(backup_dir, backup_name)
        
        # 复制文件
        if os.path.exists(self.json_path):
            shutil.copy2(self.json_path, backup_path)
        
        return backup_path
    
    def restore(self, backup_path: str) -> bool:
        """恢复词库备份
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否成功恢复
        """
        if not os.path.exists(backup_path):
            print(f"❌ 备份文件不存在：{backup_path}")
            return False
        
        # 加载备份
        with open(backup_path, 'r', encoding='utf-8') as f:
            words = json.load(f)
        
        # 保存
        return self.save_json(words)
    
    def get_update_history(self, limit: int = 100) -> List[Dict]:
        """获取更新历史（从 SQLite）"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM update_history 
                ORDER BY updated_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"⚠️  无法获取更新历史：{e}")
            return []
    
    def record_update(self, word: str, changes: Dict) -> bool:
        """记录更新操作
        
        Args:
            word: 更新的词
            changes: 变更内容
            
        Returns:
            是否成功记录
        """
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO update_history (word, changes, updated_at)
                VALUES (?, ?, ?)
            ''', (word, json.dumps(changes), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"⚠️  记录更新失败：{e}")
            return False
