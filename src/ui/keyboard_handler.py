#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 键盘事件处理器
处理候选词面板的键盘快捷键
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from typing import Optional, List
import signal

# 导入候选词面板
try:
    from .candidate_panel import CandidatePanel
    from .panel_config import CandidatePanelConfig
except ImportError:
    from candidate_panel import CandidatePanel
    from panel_config import CandidatePanelConfig


class KeyboardHandler:
    """键盘事件处理器类"""

    def __init__(self, panel: CandidatePanel):
        self.panel = panel
        self.config = CandidatePanelConfig()
        
        # 当前选中的索引
        self.selected_index = 0
        
        # 键盘映射
        self.key_map = {
            # 数字键选择候选词
            '1': 0,
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            '6': 5,
            '7': 6,
            '8': 7,
            '9': 8,
            '0': 9,
            # 上下键选择
            'Up': -1,
            'Down': 1,
            # 方向键
            'up': -1,
            'down': 1,
            # 确认键
            'Tab': 0,
            'Return': 0,
            'KP_Enter': 0,
            # 删除键
            'BackSpace': -1,
            'delete': -1,
            'Delete': -1,
            # 切换窗口模式
            'w': 'toggle_window',
            'W': 'toggle_window',
            # 最小化
            'Escape': 'minimize',
            'q': 'minimize',
            'Q': 'minimize',
            # 刷新
            'r': 'refresh',
            'R': 'refresh',
            # 滚动
            'Page_Up': -5,
            'Page_Down': 5,
            'KP_Page_Up': -5,
            'KP_Page_Down': 5,
            # 数字滚动
            'KP_1': 1,
            'KP_2': 2,
            'KP_3': 3,
            'KP_4': 4,
            'KP_5': 5,
            'KP_6': 6,
            'KP_7': 7,
            'KP_8': 8,
            'KP_9': 9,
            'KP_0': 0,
        }
        
        # 绑定键盘事件
        self.panel.connect('key-press-event', self._on_key_press)
        self.panel.connect('key-release-event', self._on_key_release)
        
        # 设置键盘抓取
        self.panel.set_app_paintable(True)
        
        # 初始化事件处理
        self._init_event_handling()

    def _init_event_handling(self):
        """初始化事件处理"""
        # 创建事件过滤器
        self.event_filter = self.panel.connect('key-press-event', self._on_key_press)

    def _on_key_press(self, widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        """处理按键事件"""
        # 获取键值
        keyval = event.keyval
        keycode = event.hardware_keycode
        
        # 转换为字符串
        key_str = Gdk.keyval_name(keyval)
        
        # 如果是特殊键，使用 keyval
        if not key_str:
            key_str = str(keyval)
        
        # 获取按键类型
        key_type = self._get_key_type(key_str, keycode)
        
        # 检查是否有对应的处理
        if key_type in self.key_map:
            # 阻止默认行为
            if event.consume():
                # 执行操作
                self._handle_key(key_type, key_str)
                return True
            else:
                return False
        else:
            return False

    def _get_key_type(self, key_str: str, keycode: int) -> str:
        """获取按键类型"""
        # 处理数字键
        if keycode >= Gdk.KEY_0 and keycode <= Gdk.KEY_9:
            return str(keycode - Gdk.KEY_0)
        
        # 处理字母键（大写）
        if keycode >= Gdk.KEY_a and keycode <= Gdk.KEY_z:
            return key_str.upper()
        
        return key_str

    def _handle_key(self, key_type: str, key_str: str):
        """处理按键"""
        action = self.key_map.get(key_type)
        
        if action == 0:
            # 选择当前候选词
            self._select_candidate()
            
        elif action < 0:
            # 移动光标
            self._move_cursor(action)
            
        elif action > 0:
            # 滚动
            self._scroll(action)
            
        elif action == 'toggle_window':
            # 切换窗口模式
            self.panel.toggle_window_mode()
            
        elif action == 'minimize':
            # 最小化
            self.panel.minimize()
            
        elif action == 'refresh':
            # 刷新
            self._refresh()

    def _select_candidate(self):
        """选择当前候选词"""
        index = self.panel.get_selected_index()
        if index < len(self.panel.candidates):
            self.panel.candidates[self.panel.candidates.index(self.panel.candidates[index])] = \
                self.panel.candidates[index]
            self.panel.emit('candidate-selected', self.panel.candidates[index])

    def _move_cursor(self, delta: int):
        """移动光标"""
        index = self.panel.get_selected_index()
        new_index = index + delta
        
        # 边界检查
        if new_index < 0:
            new_index = 0
        elif new_index >= len(self.panel.candidates):
            new_index = len(self.panel.candidates) - 1
        
        # 更新光标位置
        self.panel.cursor_pos = new_index
        self.panel._render_candidates()
        self.panel._scroll_to_cursor(new_index)

    def _scroll(self, delta: int):
        """滚动"""
        index = self.panel.get_selected_index()
        new_index = index + delta
        
        # 边界检查
        if new_index < 0:
            new_index = 0
        elif new_index >= len(self.panel.candidates):
            new_index = len(self.panel.candidates) - 1
        
        # 更新光标位置
        self.panel.cursor_pos = new_index
        self.panel._render_candidates()
        self.panel._scroll_to_cursor(new_index)

    def _refresh(self):
        """刷新候选词"""
        pass  # 由外部调用 update_candidates 刷新

    def handle_selection(self):
        """处理候选词选择"""
        selected = self.panel.get_selected_candidate()
        if selected:
            # 发送选中的候选词
            self.panel.emit('selection-changed', selected)

    def handle_commit(self):
        """处理提交"""
        selected = self.panel.get_selected_candidate()
        if selected:
            # 提交选中的候选词
            self.panel.emit('commit', selected)

    def handle_candidate_update(self, candidates: List[str], cursor_pos: Optional[int] = None):
        """处理候选词更新"""
        self.panel.update_candidates(candidates, cursor_pos)
        self.selected_index = cursor_pos if cursor_pos is not None else 0

    def get_selected_index(self) -> int:
        """获取当前选中索引"""
        return self.selected_index

    def set_selected_index(self, index: int):
        """设置选中索引"""
        self.selected_index = max(0, min(index, len(self.panel.candidates) - 1))
