"""
字典管理器模块

统一管理和加载真实词典数据：
- 真实汉语词典
- 常用词库
- 多音字词典

提供高性能的词典访问接口，支持懒加载和缓存优化。
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import json
import os
import time
from pathlib import Path
from functools import lru_cache

# 导入真实词典数据
try:
    from data.dictionaries.real_chinese_dict import RealDictionary, create_real_dictionary
    from data.dictionaries.common_words import load_common_words
    from data.dictionaries.polyphone_complete import create_full_dictionary
    DICTIONARY_AVAILABLE = True
except ImportError:
    DICTIONARY_AVAILABLE = False
    print("警告：无法导入词典数据模块，使用模拟数据")


class DictionaryManager:
    """字典管理器：统一词典数据访问"""
    
    def __init__(self):
        self.real_dictionary: Optional[RealDictionary] = None
        self.common_words: Dict[str, dict] = {}
        self.polyphone_dictionary = None
        self._load_cache: Dict[str, float] = {}  # 缓存加载状态
        self._word_freq_cache: Dict[str, float] = {}  # 词频缓存
        
        if DICTIONARY_AVAILABLE:
            self._load_default_dictionaries()
    
    def _load_default_dictionaries(self):
        """加载默认词典（立即加载）"""
        if DICTIONARY_AVAILABLE:
            # 加载真实词典
            self.real_dictionary = create_real_dictionary()
            
            # 加载常用词
            self.common_words = load_common_words()
            
            # 加载多音字词典
            self.polyphone_dictionary = create_full_dictionary()
        
        self._load_cache['real_dict'] = time.time()
        self._load_cache['common_words'] = time.time()
        self._load_cache['polyphone'] = time.time()
    
    @property
    def word_frequency(self) -> Dict[str, float]:
        """获取词频缓存"""
        return self._word_freq_cache
    
    def load_real_dictionary(self, file_path: Optional[str] = None) -> bool:
        """
        加载真实汉语词典
        
        Args:
            file_path: 词典文件路径（可选，使用默认数据）
            
        Returns:
            是否加载成功
        """
        if not DICTIONARY_AVAILABLE:
            return False
        
        if file_path and os.path.exists(file_path):
            self.real_dictionary = RealDictionary()
            self.real_dictionary.load_from_file(file_path)
        else:
            # 使用内置数据
            self.real_dictionary = create_real_dictionary()
        
        self._load_cache['real_dict'] = time.time()
        return True
    
    def load_common_words(self, file_path: Optional[str] = None) -> bool:
        """
        加载常用词库
        
        Args:
            file_path: 常用词文件路径（可选）
            
        Returns:
            是否加载成功
        """
        if not DICTIONARY_AVAILABLE:
            return False
        
        try:
            self.common_words = load_common_words()
            self._load_cache['common_words'] = time.time()
            return True
        except Exception as e:
            print(f"警告：加载常用词失败：{e}")
            return False
    
    def load_polyphone_dictionary(self, file_path: Optional[str] = None) -> bool:
        """
        加载多音字词典
        
        Args:
            file_path: 多音字词典文件路径（可选）
            
        Returns:
            是否加载成功
        """
        if not DICTIONARY_AVAILABLE:
            return False
        
        try:
            self.polyphone_dictionary = create_full_dictionary()
            self._load_cache['polyphone'] = time.time()
            return True
        except Exception as e:
            print(f"警告：加载多音字词典失败：{e}")
            return False
    
    def get_word_frequency(self, word: str, cache_ttl: int = 300) -> float:
        """
        获取词语频率
        
        Args:
            word: 词语
            cache_ttl: 缓存有效期（秒）
            
        Returns:
            词频（0-100，越高越常用）
        """
        # 检查缓存是否过期
        if word in self._word_freq_cache:
            cached_time = self._word_freq_cache[word]
            if time.time() - cached_time < cache_ttl:
                return self._word_freq_cache[word]
        
        # 从真实词典获取
        freq = 0.0
        if self.real_dictionary and word in self.real_dictionary._data:
            entry = self.real_dictionary._data[word]
            if entry.freq_map:
                # 返回最高频读音
                freq = max(entry.freq_map.values())
        
        # 从常用词获取
        if freq == 0 and word in self.common_words:
            freq = self.common_words[word].get('freq', 50.0)
        
        # 缓存结果
        self._word_freq_cache[word] = freq
        self._word_freq_cache[word + '_time'] = time.time()
        
        return freq
    
    def get_candidates(self, char: str) -> List[str]:
        """
        获取汉字候选读音列表（按频率排序）
        
        Args:
            char: 汉字
            
        Returns:
            候选读音列表
        """
        if not self.real_dictionary:
            return ['']  # 无法获取
        
        entry = self.real_dictionary.get_entry(char)
        if not entry:
            return []
        
        return entry.get_sorted_readings()
    
    def get_candidates_with_info(self, char: str) -> List[dict]:
        """
        获取汉字候选读音详细信息
        
        Args:
            char: 汉字
            
        Returns:
            包含详细信息（拼音、频率、示例词）的列表
        """
        if not self.real_dictionary:
            return []
        
        entry = self.real_dictionary.get_entry(char)
        if not entry:
            return []
        
        result = []
        for pinyin in entry.pinyin_list:
            result.append({
                'pinyin': pinyin,
                'freq': entry.freq_map.get(pinyin, 0.0),
                'examples': entry.examples.get(pinyin, []),
                'pos': entry.part_of_speech.get(pinyin, [])
            })
        
        return result
    
    def get_best_pinyin(self, char: str) -> str:
        """
        获取汉字最佳读音（最高频）
        
        Args:
            char: 汉字
            
        Returns:
            最佳读音拼音
        """
        candidates = self.get_candidates(char)
        if not candidates:
            return char
        
        return candidates[0]
    
    def get_word_candidates(self, word: str) -> List[Tuple[str, float]]:
        """
        获取词语候选词及其频率
        
        Args:
            word: 词语
            
        Returns:
            (词语，频率) 列表
        """
        candidates = []
        
        # 从常用词库获取
        if word in self.common_words:
            entry = self.common_words[word]
            candidates.append((word, entry.get('freq', 50.0)))
        
        # 从真实词典获取
        if self.real_dictionary:
            for char in word:
                entry = self.real_dictionary.get_entry(char)
                if entry and entry.freq_map:
                    freq = max(entry.freq_map.values())
                    candidates.append((word, freq))
                    break
        
        return candidates
    
    def get_context_frequency(self, word: str, prefix: str = "", suffix: str = "") -> float:
        """
        获取词语在上下文中的频率
        
        Args:
            word: 核心词语
            prefix: 前缀
            suffix: 后缀
            
        Returns:
            上下文频率
        """
        # 简单实现：返回基础词频
        return self.get_word_frequency(word)
    
    def get_dictionary_stats(self) -> dict:
        """
        获取词典统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'real_dictionary': {
                'loaded': self.real_dictionary is not None,
                'word_count': len(self.real_dictionary._data) if self.real_dictionary else 0,
            },
            'common_words': {
                'loaded': len(self.common_words) > 0,
                'word_count': len(self.common_words),
            },
            'polyphone_dictionary': {
                'loaded': self.polyphone_dictionary is not None,
                'word_count': len(self.polyphone_dictionary._data) if self.polyphone_dictionary else 0,
            },
            'cache': {
                'word_freq_cache_size': len(self._word_freq_cache),
                'load_cache': self._load_cache,
            }
        }
        
        return stats
    
    def clear_cache(self):
        """清除所有缓存"""
        self._word_freq_cache.clear()
        self._load_cache.clear()


# ==================== 便捷函数 ====================

def create_dictionary_manager() -> DictionaryManager:
    """创建字典管理器实例"""
    return DictionaryManager()


def get_word_frequency(word: str) -> float:
    """便捷函数：获取词频"""
    manager = get_dictionary_manager()
    return manager.get_word_frequency(word)


def get_candidates(char: str) -> List[str]:
    """便捷函数：获取候选读音"""
    manager = get_dictionary_manager()
    return manager.get_candidates(char)


def get_best_pinyin(char: str) -> str:
    """便捷函数：获取最佳拼音"""
    manager = get_dictionary_manager()
    return manager.get_best_pinyin(char)


def get_dictionary_manager() -> DictionaryManager:
    """获取全局字典管理器实例（单例）"""
    if not hasattr(get_dictionary_manager, '_instance'):
        get_dictionary_manager._instance = DictionaryManager()
    return get_dictionary_manager._instance


if __name__ == "__main__":
    # 测试字典管理器
    print("=" * 60)
    print("字典管理器测试")
    print("=" * 60)
    
    manager = DictionaryManager()
    
    # 测试词频查询
    test_words = ['你好', '中国', '发展', '重要', '工作', '生活']
    print("\n词频查询测试:")
    for word in test_words:
        freq = manager.get_word_frequency(word)
        print(f"  {word}: {freq:.2f}")
    
    # 测试多音字
    polyphone_chars = ['重', '长', '着', '行', '好']
    print("\n多音字候选测试:")
    for char in polyphone_chars:
        print(f"\n  {char} 的候选读音:")
        for info in manager.get_candidates_with_info(char):
            print(f"    {info['pinyin']} (freq: {info['freq']}) - 例：{', '.join(info['examples'])}")
    
    # 测试统计
    print("\n词典统计:")
    stats = manager.get_dictionary_stats()
    print(f"  真实词典：{stats['real_dictionary']['word_count']} 词")
    print(f"  常用词库：{stats['common_words']['word_count']} 词")
    print(f"  多音字词典：{stats['polyphone_dictionary']['word_count']} 词")
    print(f"  词频缓存：{stats['cache']['word_freq_cache_size']} 条目")