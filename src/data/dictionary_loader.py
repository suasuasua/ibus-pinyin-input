#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 输入法词库加载器
负责从文件加载词库数据
支持 Rime、IBus 等多种词库格式
"""

import json
import os
import re
from typing import List, Dict, Optional, Union


class DictionaryLoader:
    """词库加载器 - 支持多种格式"""
    
    SUPPORTED_EXTENSIONS = ['.json', '.txt', '.csv', '.yaml', '.yml']
    RIME_PUNCTUATION = re.compile(r'[\'"\\,;：,.!?~!@#$%^&*()_+\-=\[\]{}|\\:;\'\"<>/\\s]+')
    
    def __init__(self, cache_dir: str = '.ibus_cache'):
        """初始化词库加载器
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def load_from_file(self, file_path: str) -> List[Dict]:
        """从文件加载词库
        
        Args:
            file_path: 词库文件路径
            
        Returns:
            词库数据列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"词库文件不存在：{file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.json':
            return self._load_json(file_path)
        elif ext == '.txt':
            return self._load_txt(file_path)
        elif ext == '.csv':
            return self._load_csv(file_path)
        else:
            raise ValueError(f"不支持的文件格式：{ext}")
    
    def _load_json(self, file_path: str) -> List[Dict]:
        """加载 JSON 格式词库"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'words' in data:
                    return data['words']
                else:
                    print(f"⚠️  JSON 格式不标准，尝试直接解析")
                    return data
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败：{e}")
            return []
    
    def _load_txt(self, file_path: str) -> List[Dict]:
        """加载 TXT 格式词库（每行一个词）"""
        words = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # 尝试解析一行数据
                    word = line
                    
                    # 尝试解析 pinyin 和 frequency
                    pinyin = None
                    frequency = 1  # 默认频率
                    
                    # 检查是否有频率信息
                    if ' ' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                frequency = int(parts[1])
                                word = parts[0]
                            except ValueError:
                                pass
                    
                    words.append({
                        'word': word,
                        'pinyin': pinyin,
                        'frequency': frequency,
                        'tags': []
                    })
        except Exception as e:
            print(f"❌ TXT 加载失败：{e}")
            return []
        
        return words
    
    def _load_csv(self, file_path: str) -> List[Dict]:
        """加载 CSV 格式词库"""
        import csv
        
        words = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    words.append({
                        'word': row.get('word', row.get('pinyin', '')),
                        'pinyin': row.get('pinyin', ''),
                        'frequency': int(row.get('frequency', 1)),
                        'tags': [tag.strip() for tag in row.get('tags', '').split(',')]
                    })
        except Exception as e:
            print(f"❌ CSV 加载失败：{e}")
            return []
        
        return words
    
    def load_default_dict(self) -> List[Dict]:
        """加载默认词库"""
        # 内置默认词库
        default_words = [
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
        ]
        
        return default_words
    
    def load_user_dict(self, user_dict_path: str) -> List[Dict]:
        """加载用户自定义词库
        
        Args:
            user_dict_path: 用户词库文件路径
            
        Returns:
            用户词库数据
        """
        if not os.path.exists(user_dict_path):
            print(f"⚠️  用户词库文件不存在：{user_dict_path}")
            return []
        
        print(f"📂 加载用户词库：{user_dict_path}")
        return self.load_from_file(user_dict_path)
    
    def merge_dicts(self, dict1: List[Dict], dict2: List[Dict]) -> List[Dict]:
        """合并两个词库"""
        merged = dict1.copy()
        
        for word_info in dict2:
            word = word_info.get('word')
            found = False
            
            for w in merged:
                if w.get('word') == word:
                    # 更新现有词
                    if word_info.get('frequency'):
                        w['frequency'] = max(w.get('frequency', 0), word_info.get('frequency', 0))
                    if word_info.get('tags'):
                        w['tags'] = list(set(w.get('tags', []) + word_info.get('tags', [])))
                    found = True
                    break
            
            if not found:
                # 添加新词
                merged.append(word_info)
        
        # 按频率排序
        merged.sort(key=lambda x: x.get('frequency', 0), reverse=True)
        
        return merged

    def load_rime_dict(self, file_path: str) -> List[Dict]:
        """加载 Rime 格式词库
        
        Args:
            file_path: Rime 词库文件路径
            
        Returns:
            词库数据列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Rime 词库文件不存在：{file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.json', '.yaml', '.yml']:
            return self._load_rime_json_yaml(file_path)
        elif ext in ['.txt']:
            return self._load_rime_txt(file_path)
        else:
            raise ValueError(f"不支持的 Rime 文件格式：{ext}")
    
    def _load_rime_json_yaml(self, file_path: str) -> List[Dict]:
        """加载 Rime JSON/YAML 格式词库
        
        Rime 词库格式示例：
        {
          "words": [
            {"word": "你好", "pinyin": "ni3hao4", "frequency": 1000},
            {"word": "世界", "pinyin": "shi4jie4", "frequency": 800}
          ]
        }
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 支持多种数据结构
                if isinstance(data, list):
                    # 直接是词列表
                    return self._normalize_rime_words(data)
                elif isinstance(data, dict):
                    # 检查是否是 Rime 词库结构
                    if 'words' in data:
                        return self._normalize_rime_words(data['words'])
                    elif 'dictionary' in data and 'word' in data['dictionary']:
                        # 兼容 Rime 配置格式
                        return self._normalize_rime_words(data['dictionary'])
                    else:
                        # 尝试查找可能的词字段
                        word_keys = ['word', 'words', 'words_list', 'dict']
                        for key in word_keys:
                            if key in data:
                                return self._normalize_rime_words(data[key])
                        print(f"⚠️  Rime JSON 格式不标准，尝试直接解析字典键")
                        return self._try_parse_dict_keys(data)
                else:
                    print(f"⚠️  Rime JSON 格式不标准")
                    return []
        except json.JSONDecodeError as e:
            print(f"❌ Rime JSON/YAML 解析失败：{e}")
            return []
    
    def _load_rime_txt(self, file_path: str) -> List[Dict]:
        """加载 Rime TXT 格式词库
        
        支持多种格式：
        1. 每行一个词：word [ frequency ]
        2. 拼音 + 词：pinyin word [ frequency ]
        """
        words = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith(';'):
                        continue
                    
                    word_info = self._parse_rime_txt_line(line, line_num)
                    if word_info:
                        words.append(word_info)
        except Exception as e:
            print(f"❌ Rime TXT 加载失败：{e}")
            return []
        
        return words
    
    def _parse_rime_txt_line(self, line: str, line_num: int) -> Optional[Dict]:
        """解析 Rime TXT 格式单行"""
        word = None
        pinyin = None
        frequency = 1
        
        # 尝试识别拼音和词语
        parts = line.split()
        
        if len(parts) >= 1:
            # 第一个字段可能是拼音或词语
            if self._looks_like_pinyin(parts[0]):
                pinyin = parts[0]
                # 第二个字段是词语
                if len(parts) >= 2:
                    word = parts[1]
                    # 第三个字段可能是频率
                    if len(parts) >= 3:
                        try:
                            frequency = int(parts[2])
                        except ValueError:
                            pass
            else:
                # 第一个字段是词语
                word = parts[0]
                # 第二个字段可能是拼音
                if len(parts) >= 2:
                    pinyin = parts[1]
                    # 第三个字段可能是频率
                    if len(parts) >= 3:
                        try:
                            frequency = int(parts[2])
                        except ValueError:
                            pass
        
        if not word:
            return None
        
        return {
            'word': word,
            'pinyin': pinyin,
            'frequency': frequency,
            'tags': []
        }
    
    def _looks_like_pinyin(self, text: str) -> bool:
        """判断是否为拼音格式（带声调）"""
        # 拼音通常由 a-z 和数字 1-5 组成
        return bool(re.match(r'^[a-z]+[1-5][a-z]*[1-5]?$|^[a-z]+$|^[a-z]+$', text.lower()))
    
    def _normalize_rime_words(self, words: List) -> List[Dict]:
        """标准化 Rime 词库数据格式
        
        Args:
            words: 原始词库数据列表
            
        Returns:
            标准化后的词库数据
        """
        normalized = []
        
        for item in words:
            if isinstance(item, dict):
                # 已经是字典格式
                word_info = {
                    'word': item.get('word', item.get('pinyin', '')),
                    'pinyin': item.get('pinyin', item.get('word', '')),
                    'frequency': int(item.get('frequency', item.get('freq', 1))) if item.get('frequency') else 1,
                    'tags': item.get('tags', item.get('tag', []))
                }
                
                # 处理多音字情况
                if isinstance(word_info['pinyin'], list):
                    # 多音字：保留第一个拼音，记录所有拼音
                    word_info['pinyin'] = word_info['pinyin'][0]
                    word_info['all_pinyin'] = word_info['pinyin']
                elif not isinstance(word_info['pinyin'], str):
                    word_info['pinyin'] = ''
                    
                # 清理 tags
                if isinstance(word_info['tags'], str):
                    word_info['tags'] = [t.strip() for t in word_info['tags'].split(',')]
                elif not isinstance(word_info['tags'], list):
                    word_info['tags'] = []
                    
                normalized.append(word_info)
            elif isinstance(item, str):
                # 单个字符串，尝试解析
                word_info = self._parse_rime_txt_line(item, 0)
                if word_info:
                    normalized.append(word_info)
        
        return normalized
    
    def _try_parse_dict_keys(self, data: Dict) -> List[Dict]:
        """尝试从字典键值对解析词库"""
        words = []
        
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        word_info = self._parse_rime_txt_line(item, 0)
                        if word_info:
                            words.append(word_info)
            elif isinstance(value, str):
                words.append({
                    'word': value,
                    'pinyin': '',
                    'frequency': 1,
                    'tags': []
                })
        
        return words
    
    def validate_dict(self, words: List[Dict]) -> Dict:
        """验证词库数据完整性
        
        Args:
            words: 词库数据列表
            
        Returns:
            验证结果字典
        """
        result = {
            'valid': True,
            'total_words': 0,
            'words_with_pinyin': 0,
            'words_with_frequency': 0,
            'words_with_tags': 0,
            'duplicates': 0,
            'errors': []
        }
        
        seen_words = {}
        
        for i, word_info in enumerate(words):
            result['total_words'] += 1
            
            # 检查必需字段
            if not word_info.get('word'):
                result['valid'] = False
                result['errors'].append(f"第 {i} 条：缺少 word 字段")
                continue
            
            word = word_info['word']
            
            # 检查重复
            if word in seen_words:
                result['duplicates'] += 1
                result['errors'].append(f"第 {i} 条：重复词 '{word}' (首次出现：{seen_words[word]})")
            else:
                seen_words[word] = i
            
            # 检查拼音
            if word_info.get('pinyin'):
                result['words_with_pinyin'] += 1
            
            # 检查频率
            if word_info.get('frequency'):
                result['words_with_frequency'] += 1
            
            # 检查标签
            if word_info.get('tags'):
                result['words_with_tags'] += 1
        
        result['valid'] = len(result['errors']) == 0
        
        return result
    
    def export_to_ibus_format(self, words: List[Dict], output_path: str) -> bool:
        """将词库导出为 IBus 兼容格式
        
        IBus 词库格式：每行一个词，格式为 pinyin word [ frequency ]
        
        Args:
            words: 词库数据列表
            output_path: 输出文件路径
            
        Returns:
            是否成功导出
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for word_info in words:
                    word = word_info.get('word', '')
                    pinyin = word_info.get('pinyin', '')
                    frequency = word_info.get('frequency', 1)
                    tags = word_info.get('tags', [])
                    
                    # 写入 IBus 格式
                    line = f"{pinyin} {word}"
                    if frequency:
                        line += f" {frequency}"
                    f.write(line + '\n')
            
            print(f"✅ 词库已导出：{output_path}")
            print(f"   - 词数：{len(words)}")
            print(f"   - 格式：IBus 兼容")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败：{e}")
            return False
