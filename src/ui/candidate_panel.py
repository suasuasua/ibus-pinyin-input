#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 候选词面板 UI
GTK3 + PyGObject 实现
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from typing import List, Dict, Optional
import os

from .panel_config import CandidatePanelConfig


class CandidatePanel(Gtk.Window):
    """IBus 候选词面板类"""

    def __init__(self, parent: Optional[Gtk.Window] = None):
        super().__init__(
            title="候选词",
            skip_taskbar_hint=True,
            skip_pager_hint=True,
            modal=True,
            destroy_with_parent=True
        )

        self.config = CandidatePanelConfig()
        self.cursor_pos: Optional[int] = None
        self.candidates: List[str] = []
        
        # 窗口位置模式
        self.window_mode = False
        self.last_cursor_x = 0
        self.last_cursor_y = 0
        
        # 设置窗口属性
        self.set_default_size(self.config.width, self.config.height)
        self.set_decorated(self.config.decorated)
        self.set_grab_focus(True)
        
        # 创建内容容器
        self.content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
            margin_start=4,
            margin_end=4,
            margin_top=4,
            margin_bottom=4
        )
        self.add(self.content_box)
        
        # 创建候选词列表
        self.candidates_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0
        )
        self.content_box.append(self.candidates_box)
        
        # 创建空行（用于显示光标位置）
        self.empty_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            margin_start=6,
            margin_end=6
        )
        self.empty_row.visible = False
        self.content_box.append(self.empty_row)
        
        # 设置键盘焦点
        self.connect("focus-in-event", self._on_focus_in)
        self.connect("focus-out-event", self._on_focus_out)
        
        # 初始化候选词
        self._init_candidates()

    def _init_candidates(self):
        """初始化候选词列表"""
        self.candidates = [
            "你好", "您好", "你", "你们", "你的", "你的", 
            "你好啊", "你好呀", "你好吗", "你好吧"
        ]
        self._render_candidates()

    def _render_candidates(self):
        """渲染候选词列表"""
        # 清空列表
        while self.candidates_box.get_children():
            self.candidates_box.remove(self.candidates_box.get_children()[0])
        
        # 渲染每个候选词
        for i, candidate in enumerate(self.candidates):
            label = Gtk.Label()
            label.set_text(candidate)
            label.set_halign(Gtk.Align.START)
            label.set_hexpand(True)
            label.set_margin_start(10)
            
            # 设置样式
            css_provider = Gtk.CssProvider()
            css = f"""
            .candidate {{
                font-size: {self.config.font_size}px;
                color: {self.config.text_color};
            }}
            .candidate:hover {{
                background-color: {self.config.hover_bg};
                color: {self.config.hover_text};
            }}
            .candidate:selected {{
                background-color: {self.config.selected_bg};
                color: {self.config.selected_text};
                font-weight: bold;
            }}
            """
            css_provider.load_from_string(css)
            
            # 获取屏幕显示并添加样式
            screen = Gdk.Screen.get_default()
            context = Gtk.StyleContext()
            context.add_class("candidate")
            context.add_class(f"candidate-{i}")
            
            # 为每个候选词添加类
            label.get_style_context().add_class("candidate")
            label.get_style_context().add_class(f"candidate-{i}")
            
            # 添加样式
            style_provider = Gtk.CssProvider()
            style_provider.load_from_string(f"""
            .candidate {{
                padding: 2px 4px;
            }}
            .candidate:hover {{
                background-color: {self.config.hover_bg};
            }}
            .candidate:selected {{
                background-color: {self.config.selected_bg};
                font-weight: bold;
            }}
            """)
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            
            self.candidates_box.append(label)

    def update_candidates(self, candidates: List[str], cursor_pos: Optional[int] = None):
        """更新候选词列表"""
        self.candidates = candidates
        self.cursor_pos = cursor_pos
        self._render_candidates()
        self._scroll_to_cursor(cursor_pos)

    def _scroll_to_cursor(self, pos: Optional[int]):
        """滚动到光标位置"""
        if pos is None or pos < 0 or pos >= len(self.candidates):
            return
        
        # 获取当前可见范围
        adjustment = self.candidates_box.get_vadjustment()
        page_size = adjustment.get_page_size()
        value = adjustment.get_value()
        
        # 计算目标位置
        child = self.candidates_box.get_child_at_pos(pos, 0)
        if child:
            # 滚动到目标位置
            adjustment.set_value(max(0, value - page_size // 2 + child.get_allocation().height // 2))

    def _on_focus_in(self, widget: Gtk.Widget, event: Gdk.Event):
        """获取焦点事件"""
        if not self.window_mode:
            # 跟随光标模式
            screen = Gdk.Screen.get_default()
            window = Gdk.Window.get_root()
            
            if window:
                event_x = event.get_root_x()
                event_y = event.get_root_y()
                
                self.last_cursor_x = event_x
                self.last_cursor_y = event_y
                
                # 设置窗口位置
                self.move(event_x, event_y)
        
        self.grab_focus()

    def _on_focus_out(self, widget: Gtk.Widget, event: Gdk.Event):
        """失去焦点事件"""
        if not self.window_mode:
            # 最小化
            self.minimize()

    def minimize(self):
        """最小化窗口"""
        self.hide()

    def show(self):
        """显示窗口"""
        if not self.window_mode:
            self.move(self.last_cursor_x, self.last_cursor_y)
        self.show_all()

    def get_selected_candidate(self) -> Optional[str]:
        """获取当前选中的候选词"""
        if self.cursor_pos is None or self.cursor_pos >= len(self.candidates):
            return None
        return self.candidates[self.cursor_pos]

    def get_selected_index(self) -> int:
        """获取当前选中候选词的索引"""
        if self.cursor_pos is None or self.cursor_pos >= len(self.candidates):
            return 0
        return self.cursor_pos

    def set_window_mode(self, mode: bool):
        """设置窗口模式"""
        self.window_mode = mode

    def toggle_window_mode(self):
        """切换窗口模式"""
        self.window_mode = not self.window_mode
