"""
候选词排序模块

实现智能候选词排序：
- 多音字上下文感知
- 用户历史学习
- 词频统计
- 语义相关性
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import math
import sys
import os

# 添加父目录到路径，以便导入 dictionary_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.dictionary_manager import DictionaryManager, get_dictionary_manager


@dataclass
class CandidateScore:
    """候选词得分"""
    candidate: str
    base_score: float = 0.0  # 基础词频
    polyphone_score: float = 0.0  # 多音字选择得分
    context_score: float = 0.0  # 上下文匹配得分
    history_score: float = 0.0  # 历史使用得分
    position_bonus: float = 0.0  # 位置加分
    total_score: float = 0.0  # 总分


@dataclass
class CandidateManager:
    """候选词管理器：智能排序"""
    polyphone_dict: Optional = None
    context_aware: Optional = None
    learner: Optional = None
    
    def __init__(self, 
                 polyphone_dict: Optional['util.polyphone.PolyphoneDictionary'] = None,
                 context_aware: Optional = None,
                 learner: Optional = None):
        self.polyphone_dict = polyphone_dict
        self.context_aware = context_aware
        self.learner = learner
        self.current_candidates: List[CandidateScore] = []
        self.current_context = None
    
    def update_context(self, context: 'util.context_aware.ContextInfo'):
        """更新上下文信息"""
        self.current_context = context
    
    def add_candidate(self, text: str, 
                     base_freq: float = 1.0,
                     polyphone_pinyin: Optional[str] = None):
        """添加候选词"""
        score = CandidateScore(candidate=text, base_score=base_freq)
        
        # 如果包含多音字，计算多音字选择得分
        if polyphone_pinyin and self.polyphone_dict:
            entry = self.polyphone_dict.get_entry(polyphone_pinyin[0])
            if entry:
                pinyin = polyphone_pinyin
                score.polyphone_score = entry.freq_map.get(pinyin, 0.0) * 0.5
        
        self.current_candidates.append(score)
    
    def sort_candidates(self) -> List[str]:
        """智能排序候选词"""
        if not self.current_candidates:
            return []
        
        # 计算总分
        for score in self.current_candidates:
            score._calculate_total()
        
        # 按总分排序
        self.current_candidates.sort(key=lambda s: s.total_score, reverse=True)
        
        # 返回候选词列表
        return [s.candidate for s in self.current_candidates]
    
    def _calculate_total(self):
        """计算总分（内部方法）"""
        if not self.context_aware:
            self.total_score = self.base_score * 1.0
            return
        
        context = self.context_aware
        
        # 1. 基础词频（权重 0.3）
        self.total_score = self.base_score * 0.3
        
        # 2. 多音字选择得分（权重 0.25）
        self.total_score += self.polyphone_score * 0.25
        
        # 3. 上下文匹配得分（权重 0.25）
        self.total_score += self.context_score * 0.25
        
        # 4. 历史使用得分（权重 0.1）
        self.total_score += self.history_score * 0.1
        
        # 5. 位置加分（权重 0.1）
        idx = self.current_candidates.index(self)
        self.total_score += 0.1 * (1.0 - idx / max(1, len(self.current_candidates)))


class IntelligentCandidateSorter:
    """智能候选词排序器"""
    
    def __init__(self, dictionary_manager: Optional[DictionaryManager] = None):
        self.candidate_scores: Dict[str, CandidateScore] = {}
        self.context_info: Optional['util.context_aware.ContextInfo'] = None
        self.user_preferences: Dict[str, float] = defaultdict(float)
        self.dictionary_manager = dictionary_manager or get_dictionary_manager()
        # 初始化常用词库
        self.dictionary_manager.load_common_words()
        self.dictionary_manager.load_real_dictionary()
    
    def evaluate_candidate(self, candidate: str,
                          prefix: str = "",
                          suffix: str = "",
                          prefix_chars: str = "",
                          suffix_chars: str = "",
                          recent_history: List[str] = None) -> float:
        """评估候选词得分
        
        Returns:
            总分（越高越优先）
        """
        score = CandidateScore(candidate=candidate)
        
        # 1. 基础词频得分
        score.base_score = self._get_base_freq(candidate)
        
        # 2. 多音字上下文得分
        score.polyphone_score = self._calculate_polyphone_score(candidate, prefix, suffix)
        
        # 3. 上下文匹配得分
        score.context_score = self._calculate_context_score(
            candidate, prefix_chars, suffix_chars, prefix, suffix
        )
        
        # 4. 历史使用得分
        score.history_score = self._calculate_history_score(candidate, recent_history)
        
        # 计算总分
        total = (
            score.base_score * 0.3 +
            score.polyphone_score * 0.25 +
            score.context_score * 0.25 +
            score.history_score * 0.1
        )
        
        return total
    
    def _get_base_freq(self, candidate: str) -> float:
        """获取基础词频（从真实词典）"""
        # 使用字典管理器获取真实词频
        freq = self.dictionary_manager.get_word_frequency(candidate)
        
        # 如果没有找到，返回默认频率
        if freq == 0:
            # 简单回退：基于字符长度估算
            freq = 50.0
        
        return freq
    
    def _calculate_polyphone_score(self, candidate: str, 
                                   prefix: str, 
                                   suffix: str) -> float:
        """计算多音字上下文得分（使用真实词典）"""
        score = 0.0
        
        # 检查候选词中的多音字
        for char in candidate:
            # 使用字典管理器获取真实候选读音
            candidates = self.dictionary_manager.get_candidates_with_info(char)
            if not candidates:
                continue
            
            # 获取最高频读音
            best_pinyin = candidates[0]['pinyin']
            best_freq = candidates[0]['freq']
            
            # 检查是否与上下文匹配
            context_match = self._matches_context(char, best_pinyin, prefix, suffix)
            
            if context_match:
                # 使用真实词频
                score += best_freq * 0.15
        
        # 归一化到最大权重 0.25
        return min(score, 0.25)
    
    def _matches_context(self, char: str, pinyin: str, prefix: str, suffix: str) -> bool:
        """检查多音字读音是否与上下文匹配（使用真实词典）"""
        if not prefix and not suffix:
            return True
        
        # 检查拼音连续性
        if prefix:
            # 检查前缀拼音是否以当前 pinyin 结尾
            if prefix.endswith(pinyin[:2]):
                return True
        
        if suffix:
            # 检查后缀拼音是否以当前 pinyin 开头
            if suffix.startswith(pinyin[:2]):
                return True
        
        # 检查上下文词组
        full_context = prefix + suffix
        if full_context:
            # 检查候选词是否出现在常见词组中
            for word in full_context:
                freq = self.dictionary_manager.get_word_frequency(word)
                if freq > 50:  # 高频词
                    return True
        
        return False
    
    def _calculate_context_score(self, candidate: str,
                                 prefix_chars: str,
                                 suffix_chars: str,
                                 prefix: str,
                                 suffix: str) -> float:
        """计算上下文匹配得分"""
        score = 0.0
        
        # 检查候选词与前后文的语义连贯性
        full_text = prefix_chars + candidate + suffix_chars
        
        # 简单实现：检查候选词是否出现在常见词组中
        common_phrases = [
            '你好', '中国', '发展', '经济', '重要', '工作', 
            '生活', '学习', '研究', '科学', '技术', '文化',
            '政治', '社会', '环境', '自然', '人类', '世界',
        ]
        
        for phrase in common_phrases:
            if phrase in full_text:
                score += 0.1
        
        return min(score, 0.25)
    
    def _calculate_history_score(self, candidate: str,
                                  recent_history: List[str]) -> float:
        """计算历史使用得分"""
        if not recent_history:
            return 0.0
        
        score = 0.0
        for history in recent_history:
            # 检查候选词是否出现在历史中
            if candidate in history or history in candidate:
                score += 1.0
        
        # 归一化
        if score > 0:
            score = min(score / 5.0, 0.1)
        
        return score
    
    def get_sorted_candidates(self, 
                              candidates: List[str],
                              prefix: str = "",
                              suffix: str = "",
                              prefix_chars: str = "",
                              suffix_chars: str = "",
                              recent_history: List[str] = None) -> List[str]:
        """获取排序后的候选词列表"""
        
        scored = []
        for candidate in candidates:
            score = self.evaluate_candidate(
                candidate,
                prefix=prefix,
                suffix=suffix,
                prefix_chars=prefix_chars,
                suffix_chars=suffix_chars,
                recent_history=recent_history
            )
            scored.append((candidate, score))
        
        # 按得分排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [x[0] for x in scored]


def create_sorted_candidates(candidates: List[str],
                             prefix: str = "",
                             suffix: str = "",
                             polyphone_dict: Optional['util.polyphone.PolyphoneDictionary'] = None,
                             context_aware: Optional = None,
                             learner: Optional = None) -> List[str]:
    """便捷函数：获取排序后的候选词"""
    sorter = IntelligentCandidateSorter()
    sorter.polyphone_dict = polyphone_dict
    sorter.context_info = context_aware
    
    return sorter.get_sorted_candidates(
        candidates,
        prefix=prefix,
        suffix=suffix,
    )
