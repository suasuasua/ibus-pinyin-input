"""
事件处理模块

定义 IBus 输入法的事件类型和回调机制，支持输入事件、候选词事件和键盘事件。
"""

from enum import Enum, auto
from typing import List, Callable, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import weakref


class EventType(Enum):
    """事件类型枚举"""
    # 输入事件
    INPUT_CHAR = auto()           # 输入字符
    INPUT_TEXT = auto()           # 输入文本
    INPUT_DELETE = auto()         # 删除字符
    INPUT_BACKSPACE = auto()      # 退格删除
    INPUT_COMPOSE = auto()        # 组合键
    
    # 候选词事件
    CANDIDATE_SHOWN = auto()      # 显示候选词
    CANDIDATE_SELECTED = auto()   # 选择候选词
    CANDIDATE_COMMIT = auto()     # 提交候选词
    
    # 键盘事件
    KEY_PRESS = auto()            # 按键按下
    KEY_RELEASE = auto()          # 按键释放
    KEY_ENTER = auto()            # 回车键
    
    # 语言切换事件
    LANG_SWITCH = auto()          # 切换语言
    LANG_CHANGED = auto()         # 语言改变
    
    # 引擎事件
    ENGINE_STARTED = auto()       # 引擎启动
    ENGINE_STOPPED = auto()       # 引擎停止
    ENGINE_ERROR = auto()         # 引擎错误


@dataclass
class Event:
    """
    事件基类
    
    Attributes:
        type: 事件类型
        timestamp: 事件时间戳
        source: 事件源
        data: 附加数据
    """
    type: EventType
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    source: str = "input_engine"
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.type)
    
    def __eq__(self, other):
        if not isinstance(other, Event):
            return False
        return self.type == other.type and self.data == other.data


class InputCharEvent(Event):
    """字符输入事件"""
    def __init__(
        self,
        char: str,
        context: str = "",
        position: int = 0
    ):
        super().__init__(type=EventType.INPUT_CHAR)
        self.char = char
        self.context = context
        self.position = position
        self.data = {'char': char, 'context': context, 'position': position}


class InputTextEvent(Event):
    """文本输入事件"""
    def __init__(self, text: str):
        super().__init__(type=EventType.INPUT_TEXT)
        self.text = text
        self.data = {'text': text}


class InputDeleteEvent(Event):
    """删除事件"""
    def __init__(
        self,
        count: int = 1,
        method: str = "backspace"  # "backspace" 或 "delete"
    ):
        super().__init__(type=EventType.INPUT_DELETE)
        self.count = count
        self.method = method
        self.data = {'count': count, 'method': method}


class CandidateEvent(Event):
    """候选词事件"""
    def __init__(
        self,
        type_: str,  # "shown", "selected", "committed"
        candidates: List[str],
        index: int = -1
    ):
        super().__init__(type=EventType.CANDIDATE_SHOWN if type_ == "shown" else
                      EventType.CANDIDATE_SELECTED if type_ == "selected" else
                      EventType.CANDIDATE_COMMIT)
        self.type_ = type_
        self.candidates = candidates
        self.index = index
        self.data = {'type': type_, 'candidates': candidates, 'index': index}


class KeyboardEvent(Event):
    """键盘事件"""
    def __init__(
        self,
        key: str,
        state: str = "pressed",  # "pressed" 或 "released"
        modifiers: List[str] = []
    ):
        super().__init__(type=EventType.KEY_PRESS if state == "pressed" else
                      EventType.KEY_RELEASE)
        self.key = key
        self.state = state
        self.modifiers = modifiers
        self.data = {'key': key, 'state': state, 'modifiers': modifiers}


class LangChangeEvent(Event):
    """语言切换事件"""
    def __init__(self, from_lang: str, to_lang: str):
        super().__init__(type=EventType.LANG_SWITCH)
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.data = {'from_lang': from_lang, 'to_lang': to_lang}


class EngineEvent(Event):
    """引擎事件"""
    def __init__(self, type_: str, error: Optional[str] = None):
        super().__init__(type=EventType.ENGINE_STARTED if type_ == "started" else
                      EventType.ENGINE_STOPPED if type_ == "stopped" else
                      EventType.ENGINE_ERROR)
        self.type_ = type_
        self.error = error
        self.data = {'type': type_, 'error': error}


class EventHandler:
    """
    事件处理器类
    
    负责连接和分发事件，支持事件过滤和回调机制。
    
    Attributes:
        _handlers: 事件处理器字典 {EventType: List[Callable]}
        _filters: 事件过滤器 {EventType: List[Callable]}
    """
    
    def __init__(self):
        """初始化事件处理器"""
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._filters: Dict[EventType, List[Callable]] = {}
    
    def connect(
        self,
        event_type: EventType,
        callback: Callable,
        priority: int = 0
    ):
        """
        连接事件处理器
        
        Args:
            event_type: 要监听的事件类型
            callback: 回调函数
            priority: 优先级（越高越先执行）
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        # 按优先级排序
        self._handlers[event_type].append((priority, callback))
        self._handlers[event_type].sort(key=lambda x: x[0], reverse=True)
    
    def disconnect(self, event_type: EventType, callback: Callable):
        """
        断开事件处理器
        
        Args:
            event_type: 事件类型
            callback: 要移除的回调函数
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                (p, c) for p, c in self._handlers[event_type] if c != callback
            ]
    
    def filter_event(
        self,
        event: Event,
        callback: Callable
    ) -> bool:
        """
        应用事件过滤器
        
        Args:
            event: 要过滤的事件
            callback: 过滤器回调函数
            
        Returns:
            是否允许事件继续（True）或阻止（False）
        """
        if event.type not in self._filters:
            return True
        
        for filter_fn in self._filters[event.type]:
            if not filter_fn(event):
                return False
        
        return True
    
    def add_filter(self, event_type: EventType, callback: Callable):
        """
        添加事件过滤器
        
        Args:
            event_type: 事件类型
            callback: 过滤器回调函数
        """
        if event_type not in self._filters:
            self._filters[event_type] = []
        self._filters[event_type].append(callback)
    
    def emit(self, event: Event) -> bool:
        """
        发布事件
        
        Args:
            event: 要发布的事件
            
        Returns:
            是否成功发布
        """
        # 检查过滤器
        if not self.filter_event(event, lambda e: True):
            return False
        
        # 查找处理器
        if event.type not in self._handlers:
            return False
        
        # 调用所有处理器
        for priority, callback in self._handlers[event.type]:
            try:
                callback(event)
            except Exception as e:
                # 记录错误但不中断
                print(f"Event handler error: {e}")
        
        return True


class IBusEventEmitter:
    """
    IBus 事件发射器
    
    封装 IBus 事件回调机制，提供统一的事件接口。
    """
    
    def __init__(self):
        """初始化 IBus 事件发射器"""
        self._event_handler = EventHandler()
        self._callbacks: Dict[EventType, List[Callable]] = {
            EventType.INPUT_CHAR: [],
            EventType.INPUT_TEXT: [],
            EventType.CANDIDATE_SHOWN: [],
            EventType.CANDIDATE_SELECTED: [],
            EventType.CANDIDATE_COMMIT: [],
            EventType.LANG_SWITCH: [],
            EventType.KEY_PRESS: [],
            EventType.KEY_RELEASE: [],
        }
    
    def on(self, event_type: EventType, callback: Callable):
        """
        监听事件
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        self._event_handler.connect(event_type, callback)
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
    
    def emit(self, event: Event):
        """
        发射事件
        
        Args:
            event: 要发射的事件
        """
        self._event_handler.emit(event)
    
    def emit_char(self, char: str, context: str = "", position: int = 0):
        """
        发射字符输入事件
        
        Args:
            char: 输入的字符
            context: 上下文文本
            position: 字符位置
        """
        event = InputCharEvent(char, context, position)
        self.emit(event)
    
    def emit_text(self, text: str):
        """
        发射文本输入事件
        
        Args:
            text: 输入的文本
        """
        event = InputTextEvent(text)
        self.emit(event)
    
    def emit_delete(self, count: int = 1, method: str = "backspace"):
        """
        发射删除事件
        
        Args:
            count: 删除数量
            method: 删除方法
        """
        event = InputDeleteEvent(count, method)
        self.emit(event)
    
    def emit_candidates(
        self,
        candidates: List[str],
        index: int = -1
    ):
        """
        发射候选词事件
        
        Args:
            candidates: 候选词列表
            index: 选中的候选词索引
        """
        event = CandidateEvent("shown", candidates, index)
        self.emit(event)
    
    def emit_selection(self, index: int):
        """
        发射候选词选择事件
        
        Args:
            index: 选中的索引
        """
        candidates = ["候选词" if i != index else "" for i, _ in enumerate(["候选词1", "候选词2"])]
        event = CandidateEvent("selected", candidates, index)
        self.emit(event)
    
    def emit_commit(self, text: str):
        """
        发射提交事件
        
        Args:
            text: 提交的文本
        """
        event = CandidateEvent("committed", [text], -1)
        self.emit(event)
    
    def emit_language_switch(self, from_lang: str, to_lang: str):
        """
        发射语言切换事件
        
        Args:
            from_lang: 原语言
            to_lang: 新语言
        """
        event = LangChangeEvent(from_lang, to_lang)
        self.emit(event)
    
    def emit_key_press(self, key: str, modifiers: List[str] = []):
        """
        发射按键按下事件
        
        Args:
            key: 按键名称
            modifiers: 修饰键列表
        """
        event = KeyboardEvent(key, "pressed", modifiers)
        self.emit(event)
    
    def emit_key_release(self, key: str, modifiers: List[str] = []):
        """
        发射按键释放事件
        
        Args:
            key: 按键名称
            modifiers: 修饰键列表
        """
        event = KeyboardEvent(key, "released", modifiers)
        self.emit(event)


# 全局事件发射器实例
_event_emitter = IBusEventEmitter()


def get_emitter() -> IBusEventEmitter:
    """获取全局事件发射器实例"""
    return _event_emitter


# 测试示例
if __name__ == "__main__":
    emitter = IBusEventEmitter()
    
    # 定义回调
    def on_char(event):
        print(f"字符输入：{event.char}")
    
    def on_candidates(event):
        print(f"候选词：{event.candidates}")
    
    # 连接事件
    emitter.on(EventType.INPUT_CHAR, on_char)
    emitter.on(EventType.CANDIDATE_SHOWN, on_candidates)
    
    # 发射事件
    emitter.emit_char('中', '上下文')
    emitter.emit_candidates(['中文', '中国'])
