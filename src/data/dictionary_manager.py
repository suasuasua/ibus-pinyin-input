#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 中文输入法词库管理器
提供词库的统一管理接口，协调存储、加载、更新等功能
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from .dictionary_storage import DictionaryStorage
from .dictionary_loader import DictionaryLoader
from .dictionary_updater import DictionaryUpdater


@dataclass
class DictionaryEntry:
    """词库条目数据结构"""
    word: str           # 词
    frequency: int = 1   # 词频
    variant: str = ""    # 变体词
    tags: List[str] = field(default_factory=list)  # 标签
    created_at: str = "" # 创建时间
    updated_at: str = "" # 更新时间
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DictionaryEntry':
        return cls(**data)


class DictionaryManager:
    """
    词库管理器
    提供词库的统一管理接口
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化词库管理器
        
        Args:
            config: 配置字典，包含以下键:
                - db_path: SQLite 数据库路径
                - json_path: JSON 词库文件路径
                - data_dir: 数据存储目录
                - compression: 是否启用压缩 (True/False)
        """
        self.config = config or {
            'db_path': 'ibus_dictionary.db',
            'json_path': 'dictionary.json',
            'data_dir': 'data',
            'compression': True
        }
        
        # 初始化存储和加载器
        self.storage = DictionaryStorage(self.config)
        self.loader = DictionaryLoader(self.config)
        self.updater = DictionaryUpdater(self.config)
        
        # 初始化数据库
        if not os.path.exists(self.config['db_path']):
            self.storage.init_database()
        
        # 初始化 JSON 词库
        if not os.path.exists(self.config['json_path']):
            self.storage.init_json()
    
    # ==================== 词库管理 ====================
    
    def add_word(self, word: str, frequency: int = 1, 
                 variant: str = "", tags: List[str] = None) -> bool:
        """
        添加词库条目
        
        Args:
            word: 词
            frequency: 词频
            variant: 变体词
            tags: 标签列表
            
        Returns:
            是否成功
        """
        tags = tags or []
        entry = DictionaryEntry(
            word=word,
            frequency=frequency,
            variant=variant,
            tags=tags,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # 同时更新数据库和 JSON
        self.storage.add_entry(entry.to_dict())
        self.loader.add_word(entry)
        
        return True
    
    def remove_word(self, word: str) -> bool:
        """
        删除词库条目
        
        Args:
            word: 要删除的词
            
        Returns:
            是否成功
        """
        # 从数据库删除
        self.storage.remove_word(word)
        
        # 从 JSON 词库删除
        self.loader.remove_word(word)
        
        return True
    
    def update_word(self, word: str, frequency: int = None, 
                    variant: str = None, tags: List[str] = None) -> bool:
        """
        更新词库条目
        
        Args:
            word: 词
            frequency: 词频 (None 表示不变)
            variant: 变体词 (None 表示不变)
            tags: 标签列表 (None 表示不变)
            
        Returns:
            是否成功
        """
        # 从数据库更新
        self.storage.update_word(word, frequency, variant, tags)
        
        # 从 JSON 词库更新
        self.loader.update_word(word, frequency, variant, tags)
        
        return True
    
    def get_word(self, word: str) -> Optional[DictionaryEntry]:
        """
        获取词库条目
        
        Args:
            word: 词
            
        Returns:
            词库条目或 None
        """
        # 从数据库获取
        entry_data = self.storage.get_word(word)
        if entry_data:
            return DictionaryEntry.from_dict(entry_data)
        return None
    
    def get_words(self, limit: int = 1000, offset: int = 0) -> List[DictionaryEntry]:
        """
        批量获取词库条目
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            词库条目列表
        """
        # 从数据库批量获取
        entries_data = self.storage.get_words(limit, offset)
        return [DictionaryEntry.from_dict(data) for data in entries_data]
    
    def search_words(self, prefix: str, limit: int = 100) -> List[DictionaryEntry]:
        """
        搜索词库条目（前缀搜索）
        
        Args:
            prefix: 前缀
            limit: 限制数量
            
        Returns:
            词库条目列表
        """
        return self.loader.search_words(prefix, limit)
    
    # ==================== 词频统计 ====================
    
    def get_frequency(self, word: str) -> int:
        """
        获取词的频率
        
        Args:
            word: 词
            
        Returns:
            词频
        """
        return self.storage.get_frequency(word)
    
    def update_frequency(self, word: str, new_frequency: int) -> bool:
        """
        更新词频
        
        Args:
            word: 词
            new_frequency: 新词频
            
        Returns:
            是否成功
        """
        self.storage.update_frequency(word, new_frequency)
        self.loader.update_frequency(word, new_frequency)
        return True
    
    def get_top_words(self, count: int = 100) -> List[DictionaryEntry]:
        """
        获取高频词
        
        Args:
            count: 数量
            
        Returns:
            高频词列表
        """
        return self.storage.get_top_words(count)
    
    def get_frequency_statistics(self) -> Dict[str, Any]:
        """
        获取词频统计信息
        
        Returns:
            统计信息字典
        """
        return self.storage.get_statistics()
    
    # ==================== 词库加载 ====================
    
    def load_dictionary(self) -> int:
        """
        加载词库
        
        Returns:
            加载的条目数
        """
        return self.loader.load()
    
    def sync_with_json(self) -> int:
        """
        与 JSON 词库同步
        
        Returns:
            同步的条目数
        """
        return self.loader.sync()
    
    # ==================== 词库导出 ====================
    
    def export_json(self, output_path: str = None) -> str:
        """
        导出为 JSON 格式
        
        Args:
            output_path: 输出路径 (None 表示使用默认路径)
            
        Returns:
            输出文件路径
        """
        output_path = output_path or self.config['json_path']
        self.loader.export_json(output_path)
        return output_path
    
    def export_sqlite(self, output_path: str = None) -> str:
        """
        导出为 SQLite 格式
        
        Args:
            output_path: 输出路径
            
        Returns:
            输出文件路径
        """
        output_path = output_path or self.config['db_path']
        self.storage.export_sqlite(output_path)
        return output_path
    
    def export_all(self, output_dir: str = None) -> Dict[str, str]:
        """
        导出所有格式
        
        Args:
            output_dir: 输出目录
            
        Returns:
            导出的文件路径字典
        """
        output_dir = output_dir or self.config['data_dir']
        os.makedirs(output_dir, exist_ok=True)
        
        json_path = os.path.join(output_dir, 'dictionary.json')
        sqlite_path = os.path.join(output_dir, 'dictionary.db')
        
        self.export_json(json_path)
        self.export_sqlite(sqlite_path)
        
        return {
            'json': json_path,
            'sqlite': sqlite_path
        }
    
    # ==================== 词库导入 ====================
    
    def import_json(self, input_path: str) -> int:
        """
        从 JSON 导入词库
        
        Args:
            input_path: 输入路径
            
        Returns:
            导入的条目数
        """
        entries = self.loader.import_json(input_path)
        for entry in entries:
            self.add_word(**entry)
        return len(entries)
    
    def import_sqlite(self, input_path: str) -> int:
        """
        从 SQLite 导入词库
        
        Args:
            input_path: 输入路径
            
        Returns:
            导入的条目数
        """
        entries = self.storage.import_sqlite(input_path)
        for entry in entries:
            self.add_word(**entry)
        return len(entries)
    
    # ==================== 备份与恢复 ====================
    
    def backup(self, backup_dir: str = None, timestamp: bool = True) -> str:
        """
        备份词库
        
        Args:
            backup_dir: 备份目录
            timestamp: 是否在文件名中包含时间戳
            
        Returns:
            备份文件路径
        """
        import shutil
        import tempfile
        
        backup_dir = backup_dir or os.path.join(self.config['data_dir'], 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        if timestamp:
            json_name = f'dictionary_{timestamp_str}.json'
            sqlite_name = f'dictionary_{timestamp_str}.db'
        else:
            json_name = 'dictionary_backup.json'
            sqlite_name = 'dictionary_backup.db'
        
        json_path = os.path.join(backup_dir, json_name)
        sqlite_path = os.path.join(backup_dir, sqlite_name)
        
        # 复制 JSON
        shutil.copy(self.config['json_path'], json_path)
        # 复制 SQLite
        shutil.copy(self.config['db_path'], sqlite_path)
        
        return json_path
    
    def restore(self, backup_path: str) -> bool:
        """
        恢复词库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否成功
        """
        import shutil
        
        if os.path.exists(backup_path):
            shutil.copy(backup_path, self.config['json_path'])
            return True
        return False
    
    def get_backup_list(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        获取备份列表
        
        Args:
            limit: 限制数量
            
        Returns:
            备份信息列表
        """
        backup_dir = os.path.join(self.config['data_dir'], 'backups')
        backups = []
        
        if os.path.exists(backup_dir):
            for f in os.listdir(backup_dir):
                if f.endswith('.json') or f.endswith('.db'):
                    backups.append({
                        'name': f,
                        'path': os.path.join(backup_dir, f),
                        'time': f
                    })
            
            # 按时间排序
            backups.sort(key=lambda x: x['time'], reverse=True)
            return backups[:limit]
        
        return []
    
    # ==================== 词库信息 ====================
    
    def get_word_count(self) -> int:
        """
        获取词库条目数
        
        Returns:
            条目数
        """
        return self.storage.get_word_count()
    
    def get_unique_words(self) -> int:
        """
        获取唯一词数
        
        Returns:
            唯一词数
        """
        return self.storage.get_unique_words()
    
    def get_word_list(self) -> List[str]:
        """
        获取词列表
        
        Returns:
            词列表
        """
        return self.storage.get_word_list()
    
    def get_tags_list(self) -> List[str]:
        """
        获取所有标签
        
        Returns:
            标签列表
        """
        return self.storage.get_tags_list()
    
    # ==================== 词库清理 ====================
    
    def cleanup(self, min_frequency: int = 0) -> int:
        """
        清理词库
        
        Args:
            min_frequency: 最小词频 (低于此值的词将被删除)
            
        Returns:
            删除的条目数
        """
        return self.storage.cleanup(min_frequency)
    
    def compact(self) -> bool:
        """
        压缩词库（清理冗余数据）
        
        Returns:
            是否成功
        """
        return self.storage.compact()
    
    # ==================== 词库验证 ====================
    
    def validate(self) -> Dict[str, Any]:
        """
        验证词库完整性
        
        Returns:
            验证结果
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 验证数据库
        db_valid = self.storage.validate()
        if not db_valid:
            result['valid'] = False
            result['errors'].append('数据库验证失败')
        
        # 验证 JSON
        json_valid = self.loader.validate()
        if not json_valid:
            result['valid'] = False
            result['errors'].append('JSON 验证失败')
        
        return result


if __name__ == '__main__':
    # 测试示例
    manager = DictionaryManager()
    
    print(f"当前词库大小：{manager.get_word_count()} 条")
    print(f"唯一词数：{manager.get_unique_words()}")
    
    # 添加测试词
    manager.add_word('测试词 1', frequency=100, tags=['测试'])
    manager.add_word('测试词 2', frequency=200, tags=['测试', '高频'])
    
    # 搜索
    results = manager.search_words('测试', limit=10)
    print(f"搜索结果：{len(results)} 条")
    
    # 统计
    stats = manager.get_frequency_statistics()
    print(f"词库统计：{stats}")
    
    # 导出
    output = manager.export_all()
    print(f"导出路径：{output}")