#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 输入法词库存储模块
提供词库数据的底层存储接口
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# 默认词典数据
DEFAULT_WORDS = [
    {'word': '你好', 'pinyin': 'ni3hao4', 'frequency': 1000, 'tags': ['常用']},
    {'word': '世界', 'pinyin': 'shi4jie4', 'frequency': 800, 'tags': ['常用']},
    {'word': '中国', 'pinyin': 'zhong1guo2', 'frequency': 900, 'tags': ['国家']},
    {'word': '北京', 'pinyin': 'bei3jing1', 'frequency': 850, 'tags': ['城市']},
    {'word': '上海', 'pinyin': 'shang4hai3', 'frequency': 820, 'tags': ['城市']},
    {'word': '编程', 'pinyin': 'bian2cheng2', 'frequency': 600, 'tags': ['技术']},
    {'word': '代码', 'pinyin': 'ai4ma3', 'frequency': 550, 'tags': ['技术']},
    {'word': '测试', 'pinyin': 'ce4shi4', 'frequency': 500, 'tags': ['技术']},
    {'word': '开发', 'pinyin': 'kai1fa3', 'frequency': 580, 'tags': ['技术']},
    {'word': '学习', 'pinyin': 'xue2xi2', 'frequency': 650, 'tags': ['教育']},
    {'word': '工作', 'pinyin': 'gong4zuo4', 'frequency': 700, 'tags': ['工作']},
    {'word': '生活', 'pinyin': 'sheng1huo2', 'frequency': 680, 'tags': ['生活']},
    {'word': '健康', 'pinyin': 'jian4kang1', 'frequency': 450, 'tags': ['健康']},
    {'word': '家庭', 'pinyin': 'jia1ting2', 'frequency': 480, 'tags': ['生活']},
    {'word': '朋友', 'pinyin': 'peng2you3', 'frequency': 520, 'tags': ['社交']},
]


class DictionaryStorage:
    """词库存储类 - 提供 JSON 和 SQLite 双存储模式"""
    
    def __init__(self, cache_dir: str = '.ibus_cache'):
        """初始化词库存储
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = cache_dir
        self.json_path = os.path.join(cache_dir, 'dictionary.json')
        self.sqlite_path = os.path.join(cache_dir, 'dictionary.db')
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 初始化存储
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储结构"""
        # 初始化 JSON 存储
        if not os.path.exists(self.json_path):
            self._load_default_words()
        
        # 初始化 SQLite 存储
        if not os.path.exists(self.sqlite_path):
            self._init_sqlite()
    
    def _load_default_words(self):
        """加载默认词库"""
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_WORDS, f, ensure_ascii=False, indent=2)
    
    def _init_sqlite(self):
        """初始化 SQLite 数据库"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                pinyin TEXT,
                frequency INTEGER DEFAULT 0,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON words(word)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pinyin ON words(pinyin)')
        
        conn.commit()
        conn.close()
    
    # ==================== JSON 存储接口 ====================
    
    def load_json(self) -> List[Dict]:
        """从 JSON 文件加载词库"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_json(self, words: List[Dict]) -> bool:
        """保存词库到 JSON 文件"""
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(words, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存 JSON 失败：{e}")
            return False
    
    # ==================== SQLite 存储接口 ====================
    
    def load_sqlite(self) -> List[Dict]:
        """从 SQLite 数据库加载词库"""
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM words ORDER BY frequency DESC')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def insert_word(self, word: str, pinyin: str = None, 
                    frequency: int = 0, tags: str = None) -> int:
        """插入新词"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO words (word, pinyin, frequency, tags)
            VALUES (?, ?, ?, ?)
        ''', (word, pinyin, frequency, tags))
        
        word_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return word_id
    
    def update_word(self, word_id: int, pinyin: str = None,
                    frequency: int = None, tags: str = None) -> bool:
        """更新词"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        update_fields = []
        values = []
        
        if pinyin is not None:
            update_fields.append('pinyin = ?')
            values.append(pinyin)
        if frequency is not None:
            update_fields.append('frequency = ?')
            values.append(frequency)
        if tags is not None:
            update_fields.append('tags = ?')
            values.append(tags)
        values.append('')  # updated_at
        
        if update_fields:
            values.insert(0, f"WHERE id = ?")
            values.append(word_id)
            
            cursor.execute('UPDATE words SET ' + ', '.join(update_fields) + ' ', values)
        
        conn.commit()
        conn.close()
        
        return True
    
    def delete_word(self, word_id: int) -> bool:
        """删除词"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM words WHERE id = ?', (word_id,))
        conn.commit()
        conn.close()
        
        return True
    
    def search_sqlite(self, pattern: str, limit: int = 100) -> List[Dict]:
        """搜索词库"""
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM words 
            WHERE word LIKE ?
            ORDER BY frequency DESC
            LIMIT ?
        ''', (f'%{pattern}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== 统一接口 ====================
    
    def get_all_words(self) -> List[Dict]:
        """获取所有词（JSON 优先）"""
        json_words = self.load_json()
        if json_words:
            return json_words
        
        return self.load_sqlite()
    
    def get_word(self, word: str) -> Optional[Dict]:
        """根据拼音获取词"""
        # 优先 JSON
        json_words = self.load_json()
        for w in json_words:
            if w.get('word') == word:
                return w
        
        # 回退 SQLite
        sqlite_words = self.load_sqlite()
        for w in sqlite_words:
            if w.get('word') == word:
                return w
        
        return None
    
    def search_words(self, pattern: str, limit: int = 100) -> List[Dict]:
        """搜索词"""
        # 优先 JSON
        json_words = self.load_json()
        results = [w for w in json_words if pattern in w.get('word', '')]
        
        if len(results) >= limit:
            return results[:limit]
        
        # 补充 SQLite
        sqlite_results = self.search_sqlite(pattern, limit - len(results))
        return results + sqlite_results
    
    def get_top_words(self, count: int) -> List[Dict]:
        """获取高频词"""
        words = self.get_all_words()
        sorted_words = sorted(words, key=lambda x: x.get('frequency', 0), reverse=True)
        return sorted_words[:count]
    
    def get_frequency_statistics(self) -> Dict[str, Any]:
        """获取频率统计"""
        words = self.get_all_words()
        
        return {
            'total_words': len(words),
            'unique_words': len(set(w.get('word') for w in words)),
            'avg_frequency': sum(w.get('frequency', 0) for w in words) / max(len(words), 1),
            'max_frequency': max(w.get('frequency', 0) for w in words) if words else 0,
            'min_frequency': min(w.get('frequency', 0) for w in words) if words else 0,
        }
    
    def export_all(self, base_path: str) -> Dict[str, str]:
        """导出所有词库"""
        words = self.get_all_words()
        
        # JSON 导出
        json_path = os.path.join(base_path, 'dictionary.json')
        os.makedirs(base_path, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
        
        # SQLite 导出
        sqlite_path = os.path.join(base_path, 'dictionary.db')
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM words')
        rows = cursor.fetchall()
        conn.close()
        
        return {
            'json': json_path,
            'sqlite': sqlite_path,
            'count': len(words)
        }
    
    def validate(self) -> Dict[str, Any]:
        """验证词库完整性"""
        words = self.get_all_words()
        
        # 检查必填字段
        required_fields = ['word', 'frequency']
        invalid_words = []
        
        for w in words:
            for field in required_fields:
                if field not in w or not w[field]:
                    invalid_words.append(w.get('word', 'unknown'))
        
        return {
            'valid': len(invalid_words) == 0,
            'total_words': len(words),
            'invalid_words_count': len(invalid_words),
            'invalid_words': invalid_words[:10]  # 最多显示 10 个
        }
