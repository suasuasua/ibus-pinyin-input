#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 中文输入法引擎 - 核心实现
"""

import sys
import os
import logging
from typing import Callable, Dict, List, Optional, Any
from collections import defaultdict

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.events import EventType
from engine.pinyin_converter import PinyinConverter


class InputEngine:
    """输入法引擎"""
    
    def __init__(self, max_candidates: int = 6, context_window: int = 10):
        """
        初始化输入法引擎
        
        Args:
            max_candidates: 候选词最大数量
            context_window: 上下文窗口大小
        """
        self.max_candidates = max_candidates
        self.context_window = context_window
        
        # 拼音转换器
        self.converter = PinyinConverter()
        
        # 状态管理
        self._input_text = ""
        self._candidates = []
        self._commit_callbacks: List[Callable] = []
        self._shown_callbacks: List[Callable] = []
        
        # 统计信息
        self._stats = {
            "input_count": 0,
            "candidate_count": 0,
            "commit_count": 0
        }
        
        # 日志
        self.logger = logging.getLogger(f"IBusEngine-{id(self)}")
        
        self.logger.info(f"引擎初始化完成 (max_candidates={max_candidates})")
    
    def on_event(self, event_type: EventType, callback: Callable):
        """
        注册事件监听器
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type == EventType.CANDIDATE_COMMIT:
            self._commit_callbacks.append(callback)
        elif event_type == EventType.CANDIDATE_SHOWN:
            self._shown_callbacks.append(callback)
        self.logger.debug(f"注册事件监听器：{event_type}")
    
    def process_input(self, text: str):
        """
        处理输入文本
        
        Args:
            text: 输入文本
        """
        if not text.strip():
            return
        
        self._input_text = text
        self._stats["input_count"] += 1
        
        # 转换为拼音
        pinyin_list = self.converter.convert(text)
        
        # 生成候选词（模拟）
        candidates = self._generate_candidates(text, pinyin_list)
        
        self._candidates = candidates[:self.max_candidates]
        self._stats["candidate_count"] += 1
        
        # 触发候选词显示事件
        self._emit_event(EventType.CANDIDATE_SHOWN, {
            "type": "shown",
            "candidates": candidates[:self.max_candidates]
        })
    
    def commit(self, selection_index: int = 0):
        """
        提交候选词
        
        Args:
            selection_index: 选中的候选词索引
        """
        if not self._candidates or selection_index < 0 or selection_index >= len(self._candidates):
            return
        
        selected = self._candidates[selection_index]
        self._stats["commit_count"] += 1
        
        # 触发提交事件（兼容 dict 和对象）
        text = selected.get("word", str(selected))
        pinyin = selected.get("pinyin", "")
        
        self._emit_event(EventType.CANDIDATE_COMMIT, {
            "text": text,
            "pinyin": pinyin,
            "index": selection_index
        })
        
        # 更新输入文本
        self._input_text = text
    
    def _generate_candidates(self, text: str, pinyin_list: List[str]) -> List[Dict[str, str]]:
        """
        生成候选词（简化版实现）
        
        Args:
            text: 输入文本
            pinyin_list: 拼音列表
            
        Returns:
            候选词列表
        """
        candidates = []
        
        # 尝试匹配常见词语
        common_words = {
            "nihao": [{"word": "你好", "pinyin": "nihao"}],
            "zhongguo": [{"word": "中国", "pinyin": "zhongguo"}],
            "python": [{"word": "Python", "pinyin": "python"}],
            "bu": [
                {"word": "不", "pinyin": "bu"},
                {"word": "步", "pinyin": "bu4"},
                {"word": "布", "pinyin": "bu4"},
                {"word": "部", "pinyin": "bu4"},
                {"word": "部", "pinyin": "bu1"}
            ],
            "chu": [
                {"word": "处", "pinyin": "chu3"},
                {"word": "处", "pinyin": "chu4"},
                {"word": "出", "pinyin": "chu1"},
                {"word": "初", "pinyin": "chu1"},
                {"word": "除", "pinyin": "chu2"}
            ],
            "bo": [
                {"word": "剥", "pinyin": "bo1"},
                {"word": "剥", "pinyin": "bo1"},
                {"word": "博", "pinyin": "bo2"},
                {"word": "伯", "pinyin": "bo2"},
                {"word": "箔", "pinyin": "bo2"}
            ]
        }
        
        key = text.lower()
        if key in common_words:
            return common_words[key]
        
        # 如果没有匹配，返回基础拼音
        for pinyin in pinyin_list[:3]:
            candidates.append({
                "word": pinyin,
                "pinyin": pinyin
            })
        
        return candidates
    
    def _emit_event(self, event_type: EventType, data: Dict[str, Any]):
        """
        触发事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        # 触发对应的事件监听器
        if event_type == EventType.CANDIDATE_COMMIT:
            for callback in self._commit_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"CANDIDATE_COMMIT 回调错误：{e}")
        
        elif event_type == EventType.CANDIDATE_SHOWN:
            for callback in self._shown_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"CANDIDATE_SHOWN 回调错误：{e}")
    
    def is_composing(self) -> bool:
        """
        检查是否处于输入状态
        
        Returns:
            是否在输入状态
        """
        return bool(self._input_text)
    
    def get_candidates(self) -> List[Dict[str, str]]:
        """
        获取当前候选词
        
        Returns:
            候选词列表
        """
        return self._candidates.copy()
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return self._stats.copy()


def create_engine(max_candidates: int = 6, context_window: int = 10) -> InputEngine:
    """
    创建输入法引擎实例
    
    Args:
        max_candidates: 候选词最大数量
        context_window: 上下文窗口大小
        
    Returns:
        InputEngine 实例
    """
    return InputEngine(max_candidates=max_candidates, context_window=context_window)


# 事件类型定义
class EventType:
    """事件类型枚举"""
    CANDIDATE_COMMIT = "candidate_commit"  # 候选词提交事件
    CANDIDATE_SHOWN = "candidate_shown"    # 候选词显示事件


class SimpleInputEngine:
    """简化版输入法引擎（测试用）"""
    
    def __init__(self):
        self.input_text = ""
        self.candidates = []
    
    def process(self, text):
        """处理输入"""
        self.input_text = text
        # 模拟候选词
        self.candidates = [
            {"word": "你好", "pinyin": "nihao"},
            {"word": "您好", "pinyin": "nihao2"},
            {"word": "泥豪", "pinyin": "nihao"}
        ]
    
    def commit(self, index=0):
        """提交"""
        if self.candidates and index < len(self.candidates):
            self.input_text = self.candidates[index]["word"]


def create_simple_engine():
    """创建简化引擎"""
    return SimpleInputEngine()


if __name__ == "__main__":
    # 测试引擎
    print("测试 IBus 输入法引擎...")
    
    engine = create_engine(max_candidates=6)
    
    # 注册回调
    def on_commit(data):
        print(f"✓ 提交：{data['text']} ({data['pinyin']})")
    
    def on_shown(data):
        print(f"📋 候选词 ({len(data['candidates'])})")
        for i, c in enumerate(data['candidates'][:3], 1):
            print(f"  {i}. {c['word']} ({c['pinyin']})")
    
    engine.on_event(EventType.CANDIDATE_COMMIT, on_commit)
    engine.on_event(EventType.CANDIDATE_SHOWN, on_shown)
    
    # 测试输入
    test_inputs = ["nihao", "zhongguo", "bu", "chu", "bo"]
    for text in test_inputs:
        print(f"\n输入：{text}")
        engine.process_input(text)
        if engine.is_composing():
            engine.commit()
    
    print(f"\n统计：{engine.get_stats()}")
