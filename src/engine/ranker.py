"""
候选词排序器模块

负责根据多种因素对候选词进行排序，包括词频、上下文匹配度等。
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class CandidateWord:
    """
    候选词数据结构
    
    Attributes:
        word: 候选词文本
        pinyin: 拼音表示
        frequency: 词频（越高越常用）
        context_match: 与上下文的匹配度 (0-1)
        user_preference: 用户偏好权重 (0-1)
        length_bonus: 长度加分 (-1 到 0)
    """
    word: str
    pinyin: str
    frequency: float = 1.0
    context_match: float = 0.0
    user_preference: float = 0.0
    length_bonus: float = 0.0
    
    def __post_init__(self):
        """计算综合得分"""
        self.score = self._calculate_score()
    
    def _calculate_score(self) -> float:
        """
        计算候选词的排序得分
        
        Returns:
            综合得分
        """
        # 基础得分：词频 * 上下文匹配
        base_score = self.frequency * (1.0 + self.context_match)
        
        # 长度惩罚：较短的词优先
        length_penalty = -min(len(self.word) * 0.1, 0.5)
        
        # 用户偏好加分
        user_boost = self.user_preference * 2.0
        
        # 综合得分
        total_score = base_score + length_penalty + user_boost
        
        return total_score
    
    def length(self) -> int:
        """获取词的长度"""
        return len(self.word)


class Ranker:
    """
    候选词排序器类
    
    负责根据多种因素对候选词进行排序，包括词频、上下文匹配度、
    用户偏好等。
    
    Attributes:
        word_freq: 词频字典
        user_history: 用户输入历史
        context_window: 上下文窗口大小
        max_candidates: 最大候选词数量
    """
    
    def __init__(
        self,
        word_freq: Optional[Dict[str, float]] = None,
        user_history: Optional[List[str]] = None,
        context_window: int = 10,
        max_candidates: int = 6
    ):
        """
        初始化排序器
        
        Args:
            word_freq: 词频字典 {词：频率}
            user_history: 用户输入历史列表
            context_window: 上下文窗口大小
            max_candidates: 最大候选词数量
        """
        self.word_freq = word_freq or self._load_default_freq_dict()
        self.user_history = user_history or []
        self.context_window = context_window
        self.max_candidates = max_candidates
    
    def _load_default_freq_dict(self) -> Dict[str, float]:
        """
        加载默认词频字典
        
        Returns:
            默认词频字典
        """
        # 这是一个简化的示例词频表
        # 实际项目中应从词典文件加载
        return {
            '你好': 100.0,
            '世界': 80.0,
            '中国': 90.0,
            '北京': 70.0,
            '上海': 60.0,
            '电脑': 50.0,
            '手机': 45.0,
            '编程': 55.0,
            '代码': 48.0,
            '学习': 42.0,
            '工作': 38.0,
            '生活': 35.0,
            '朋友': 32.0,
            '家人': 30.0,
            '快乐': 28.0,
            '悲伤': 15.0,
            '爱': 50.0,
            '喜欢': 45.0,
            '讨厌': 20.0,
        }
    
    def rank_candidates(self, candidates: List[CandidateWord]) -> List[CandidateWord]:
        """
        对候选词进行排序
        
        Args:
            candidates: 候选词列表
            
        Returns:
            排序后的候选词列表
        """
        if not candidates:
            return []
        
        # 计算每个候选词的上下文匹配度
        self._calculate_context_match(candidates)
        
        # 计算用户偏好
        self._calculate_user_preference(candidates)
        
        # 根据得分排序
        sorted_candidates = sorted(
            candidates,
            key=lambda x: x.score,
            reverse=True
        )
        
        # 限制最大数量
        return sorted_candidates[:self.max_candidates]
    
    def _calculate_context_match(self, candidates: List[CandidateWord]):
        """
        计算候选词与上下文的匹配度
        
        Args:
            candidates: 候选词列表
        """
        # 获取上下文
        context = self._get_context()
        
        for candidate in candidates:
            # 计算与上下文的相似度
            candidate.context_match = self._calculate_similarity(
                candidate.word, context
            )
            candidate.__post_init__()  # 重新计算得分
    
    def _calculate_similarity(self, word: str, context: str) -> float:
        """
        计算词与上下文的相似度
        
        Args:
            word: 候选词
            context: 上下文文本
            
        Returns:
            相似度分数 (0-1)
        """
        if not context:
            return 0.0
        
        # 简单 Jaccard 相似度
        word_set = set(word)
        context_set = set(context)
        
        if not word_set:
            return 0.0
        
        intersection = len(word_set.intersection(context_set))
        union = len(word_set.union(context_set))
        
        return min(intersection / union, 1.0)
    
    def _get_context(self) -> str:
        """
        获取上下文窗口
        
        Returns:
            上下文字符串
        """
        if not self.user_history:
            return ""
        
        # 获取最近的上下文
        recent_history = self.user_history[-self.context_window:]
        return ' '.join(recent_history)
    
    def _calculate_user_preference(self, candidates: List[CandidateWord]):
        """
        计算用户偏好权重
        
        Args:
            candidates: 候选词列表
        """
        for candidate in candidates:
            # 基于用户历史计算偏好
            preference = self._calculate_historical_preference(candidate.word)
            candidate.user_preference = preference
            candidate.__post_init__()  # 重新计算得分
    
    def _calculate_historical_preference(self, word: str) -> float:
        """
        基于用户历史计算词偏好
        
        Args:
            word: 候选词
            
        Returns:
            偏好权重 (0-1)
        """
        if not self.user_history:
            return 0.0
        
        # 计算词在历史中出现的频率
        history_lower = ' '.join(self.user_history).lower()
        word_lower = word.lower()
        
        # 计算出现次数
        count = history_lower.count(word_lower)
        total_chars = len(' '.join(self.user_history))
        
        # 归一化到 0-1 范围
        if total_chars > 0:
            return min(count / (total_chars / 10.0), 1.0)
        
        return 0.0
    
    def add_to_history(self, text: str):
        """
        将输入添加到用户历史
        
        Args:
            text: 输入的文本
        """
        self.user_history.append(text)
    
    def update_frequency(self, word: str, frequency: float):
        """
        更新词频
        
        Args:
            word: 词
            frequency: 新频率
        """
        self.word_freq[word] = frequency
    
    def get_word_frequency(self, word: str) -> float:
        """
        获取词频
        
        Args:
            word: 词
            
        Returns:
            频率值，如果词不存在则返回默认值 1.0
        """
        return self.word_freq.get(word, 1.0)
    
    def clear_history(self):
        """清除用户历史"""
        self.user_history.clear()
    
    def get_top_candidates(self, count: int) -> List[CandidateWord]:
        """
        获取前 N 个候选词
        
        Args:
            count: 数量
            
        Returns:
            候选词列表
        """
        return self.user_history[-count:] if count <= len(self.user_history) else self.user_history[:count]


class SimpleRanker:
    """
    简单排序器（无上下文）
    
    仅基于词频进行排序，适用于简单场景。
    """
    
    def __init__(self, word_freq: Optional[Dict[str, float]] = None):
        """
        初始化简单排序器
        
        Args:
            word_freq: 词频字典
        """
        self.word_freq = word_freq or {}
    
    def rank(self, candidates: List[CandidateWord]) -> List[CandidateWord]:
        """
        基于词频排序候选词
        
        Args:
            candidates: 候选词列表
            
        Returns:
            排序后的候选词列表
        """
        if not candidates:
            return []
        
        # 按词频排序
        sorted_candidates = sorted(
            candidates,
            key=lambda x: self.word_freq.get(x.word, 1.0),
            reverse=True
        )
        
        return sorted_candidates[:6]


# 测试示例
if __name__ == "__main__":
    # 创建排序器
    ranker = Ranker(
        word_freq={'你好': 100, '世界': 80, '中国': 90},
        user_history=['你好', '世界', '中国']
    )
    
    # 创建候选词
    candidates = [
        CandidateWord(word='你好', pinyin='ni hao', frequency=100),
        CandidateWord(word='世界', pinyin='shi jie', frequency=80),
        CandidateWord(word='中国', pinyin='zhong guo', frequency=90),
        CandidateWord(word='电脑', pinyin='dian nao', frequency=50),
    ]
    
    # 排序
    sorted_candidates = ranker.rank_candidates(candidates)
    
    print("排序后的候选词:")
    for i, candidate in enumerate(sorted_candidates, 1):
        print(f"{i}. {candidate.word} (得分：{candidate.score:.2f})")
