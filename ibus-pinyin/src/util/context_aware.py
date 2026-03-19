"""
上下文感知的多音字选择模块

根据上下文信息智能选择多音字的正确读音：
- 拼音上下文匹配
- 候选词组合频率
- 用户历史输入学习
- 语义上下文分析
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import re


@dataclass
class ContextInfo:
    """上下文信息容器"""
    # 前缀拼音（已输入的拼音）
    prefix_pinyin: str = ""
    # 后缀拼音（即将输入的拼音）
    suffix_pinyin: str = ""
    # 前缀汉字（已选择的汉字）
    prefix_chars: str = ""
    # 后缀汉字（已选择但未显示的汉字）
    suffix_chars: str = ""
    # 最近输入的候选词列表
    recent_candidates: List[str] = field(default_factory=list)
    # 用户历史输入记录
    history: List[str] = field(default_factory=list)
    # 词组频率上下文
    phrase_freq: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    
    def get_context_window(self, before: int = 3, after: int = 2) -> Dict[str, str]:
        """获取上下文窗口"""
        context = {}
        # 前缀
        for i in range(before, max(0, len(self.prefix_chars) - before), -1):
            context[f'before_{i}'] = self.prefix_chars[i]
        # 后缀
        for i in range(min(after, len(self.suffix_chars)), -1, -1):
            context[f'after_{i}'] = self.suffix_chars[i] if i < len(self.suffix_chars) else ''
        return context


@dataclass
class PolyphoneSelector:
    """多音字选择器：基于上下文智能选择读音"""
    polyphone_dict: Optional = None
    
    def __init__(self, polyphone_dict: Optional['util.polyphone.PolyphoneDictionary'] = None):
        self.polyphone_dict = polyphone_dict
        # 学习缓存
        self.context_scores: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float)
        self.history_weights: Dict[str, float] = defaultdict(float)
    
    def update_context(self, context: ContextInfo):
        """更新上下文信息"""
        self.context_info = context
    
    def select_best_pinyin(self, char: str, 
                          prefix: str = "",
                          suffix: str = "",
                          recent_candidates: Optional[List[str]] = None) -> str:
        """
        选择最佳读音
        
        Args:
            char: 多音字汉字
            prefix: 前缀拼音
            suffix: 后缀拼音
            recent_candidates: 最近候选词
            
        Returns:
            最佳读音（拼音）
        """
        if not self.polyphone_dict:
            return self._fallback_select(char)
        
        entry = self.polyphone_dict.get_entry(char)
        if not entry:
            return self._fallback_select(char)
        
        # 计算每个读音的得分
        scores = self._calculate_scores(char, prefix, suffix, recent_candidates)
        
        # 获取最高得分的读音
        if not scores:
            return entry.get_top_readings()[0]
        
        best_pinyin = max(scores, key=scores.get)
        return best_pinyin
    
    def _calculate_scores(self, char: str, 
                         prefix: str, 
                         suffix: str,
                         recent_candidates: Optional[List[str]]) -> Dict[str, float]:
        """计算每个读音的得分"""
        entry = self.polyphone_dict.get_entry(char)
        if not entry:
            return {}
        
        scores = {}
        
        for pinyin in entry.pinyin_list:
            score = 0.0
            
            # 1. 基础频率分（权重 0.4）
            base_freq = entry.freq_map.get(pinyin, 0.0)
            score += base_freq * 0.4
            
            # 2. 拼音上下文匹配分（权重 0.25）
            context_match = self._check_pinyin_context(pinyin, prefix, suffix)
            score += context_match * 0.25
            
            # 3. 候选词组合频率（权重 0.25）
            combo_freq = self._check_candidate_combo(char, pinyin, suffix)
            score += combo_freq * 0.25
            
            # 4. 用户历史分（权重 0.1）
            history_score = self._check_history(char, pinyin, recent_candidates)
            score += history_score * 0.1
            
            scores[pinyin] = score
        
        return scores
    
    def _check_pinyin_context(self, pinyin: str, 
                              prefix: str, 
                              suffix: str) -> float:
        """检查拼音上下文匹配度"""
        if not prefix and not suffix:
            return 0.0
        
        score = 0.0
        score_threshold = 0.7
        
        # 检查前缀拼音是否以当前读音结尾
        if prefix:
            # 检查是否有常见词组
            if self._is_common_prefix(prefix, pinyin):
                score += 0.15
        
        # 检查后缀拼音是否以当前读音开头
        if suffix:
            if self._is_common_suffix(pinyin, suffix):
                score += 0.15
        
        return min(score, 0.3)
    
    def _check_candidate_combo(self, char: str, 
                               pinyin: str,
                               suffix: str) -> float:
        """检查候选词组合频率"""
        if not self.polyphone_dict:
            return 0.0
        
        score = 0.0
        
        # 尝试构建候选词
        for suffix_pinyin in self.polyphone_dict.get_candidates(suffix[0]) if suffix else []:
            candidate = char + suffix[0] if char else suffix[0]
            
            # 检查组合词频
            if candidate in self.context_info.phrase_freq if hasattr(self, 'context_info') else False:
                score += self.context_info.phrase_freq[candidate] * 0.1
        
        return min(score, 0.15)
    
    def _check_history(self, char: str, 
                       pinyin: str,
                       recent_candidates: Optional[List[str]]) -> float:
        """检查用户历史使用频率"""
        if not recent_candidates:
            return 0.0
        
        score = 0.0
        history_count = 0
        
        for candidate in recent_candidates:
            if char in candidate:
                # 提取该字在候选词中的读音
                # 简化：直接检查候选词频率
                score += 1.0
        
        # 归一化
        if score > 0:
            score = min(score / 10.0, 0.1)
        
        return score
    
    def _is_common_prefix(self, prefix: str, pinyin: str) -> bool:
        """检查是否为常见词组前缀"""
        common_prefixes = {
            'zh': ['zhong', 'zhe', 'zhu', 'zha', 'zhi', 'zhuo', 'zhan', 'zhen', 'zha'],
            'ch': ['chang', 'che', 'chou', 'chi', 'chuan', 'chuang', 'chen', 'chun', 'chu'],
            'sh': ['shen', 'shi', 'shou', 'shua', 'shuo', 'shui', 'shun', 'shuang'],
        }
        
        prefix_lower = prefix.lower()
        for key, values in common_prefixes.items():
            if prefix_lower.startswith(key):
                return pinyin in values
        
        return False
    
    def _is_common_suffix(self, pinyin: str, suffix: str) -> bool:
        """检查是否为常见词组后缀"""
        common_suffixes = {
            'ing': ['zhong', 'chen', 'shen', 'ding', 'ting', 'qing', 'ming'],
            'an': ['zhan', 'chan', 'shan', 'zhen', 'chen', 'shen', 'fan', 'nan', 'wan'],
            'ang': ['zhong', 'chong', 'shuang', 'chuang', 'huang'],
        }
        
        suffix_lower = suffix.lower()
        for key, values in common_suffixes.items():
            if suffix_lower.startswith(key):
                return pinyin in values
        
        return False
    
    def _fallback_select(self, char: str) -> str:
        """回退选择：按频率选择"""
        entry = self.polyphone_dict.get_entry(char) if self.polyphone_dict else None
        if entry:
            return entry.get_top_readings()[0]
        return char  # 无法获取读音时返回汉字本身


@dataclass
class PolyphoneLearner:
    """多音字学习器：从用户输入中学习"""
    learning_data: Dict[str, List[Dict]] = field(default_factory=lambda: defaultdict(list))
    
    def __init__(self):
        self.learning_data = defaultdict(list)
        self.global_weights: Dict[str, float] = defaultdict(float)
    
    def record_selection(self, char: str, 
                        pinyin: str,
                        context: ContextInfo,
                        confidence: float = 0.8):
        """记录一次多音字选择"""
        entry = {
            'char': char,
            'pinyin': pinyin,
            'context': {
                'prefix': context.prefix_pinyin,
                'suffix': context.suffix_pinyin,
                'prefix_chars': context.prefix_chars,
                'suffix_chars': context.suffix_chars,
            },
            'confidence': confidence,
            'timestamp': time.time() if 'time' in globals() else 0,
        }
        
        self.learning_data[char].append(entry)
        
        # 更新权重
        if len(self.learning_data[char]) > 100:  # 限制历史记录
            self.learning_data[char].pop(0)
        
        # 更新全局权重
        weight = confidence * 0.1
        self.global_weights[char] += weight
    
    def get_learned_pinyin(self, char: str, 
                          context: ContextInfo) -> Optional[str]:
        """根据学习记录获取最可能的读音"""
        entries = self.learning_data.get(char, [])
        if not entries:
            return None
        
        # 根据上下文过滤
        filtered = []
        for entry in entries:
            context_match = 0.0
            
            # 前缀匹配
            if entry['context']['prefix'] == context.prefix_pinyin:
                context_match += 0.5
            
            # 后缀匹配
            if entry['context']['suffix'] == context.suffix_pinyin:
                context_match += 0.5
            
            if context_match > 0:
                filtered.append(entry)
        
        if not filtered:
            # 无上下文匹配时返回最高频
            return max(entries, key=lambda e: e['confidence'])['pinyin']
        
        # 返回最高置信度的
        return max(filtered, key=lambda e: e['confidence'])['pinyin']


def create_selector_and_learner(polyphone_dict: Optional[util.polyphone.PolyphoneDictionary] = None):
    """创建选择器和学习器"""
    selector = PolyphoneSelector(polyphone_dict)
    learner = PolyphoneLearner()
    return selector, learner
