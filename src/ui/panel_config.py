#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 候选词面板配置
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CandidatePanelConfig:
    """候选词面板配置类"""
    
    # 窗口尺寸
    width: int = 320
    height: int = 280
    
    # 装饰
    decorated: bool = False
    
    # 字体
    font_size: int = 18
    
    # 颜色
    bg_color: str = "#ffffff"
    hover_bg: str = "#f0f0f0"
    selected_bg: str = "#e8f4fd"
    text_color: str = "#333333"
    hover_text: str = "#000000"
    selected_text: str = "#0066cc"
    
    # 阴影
    shadow_color: str = "rgba(0, 0, 0, 0.15)"
    shadow_offset_x: int = 0
    shadow_offset_y: int = 2
    shadow_radius: int = 8
    
    # 候选词数量
    max_candidates: int = 9
    
    # 主题
    theme: str = "light"  # light, dark, system
    
    # 跟随光标
    follow_cursor: bool = True
    
    # 窗口模式
    window_mode: bool = False
    
    # 延迟
    show_delay: int = 0
    hide_delay: int = 1000
    
    # 滚动步长
    scroll_step: int = 5
    
    # 快捷键
    # 选择键
    select_key: str = "Tab"
    
    # 上移键
    up_key: str = "Up"
    
    # 下移键
    down_key: str = "Down"
    
    # 最小化键
    minimize_key: str = "Escape"
    
    # 切换窗口模式键
    toggle_window_key: str = "w"
    
    # 刷新键
    refresh_key: str = "r"
    
    # 数字键映射
    # 0-9 对应候选词索引 0-8
    
    # 滚动步长
    page_up_step: int = 5
    page_down_step: int = 5
    
    # 主题颜色
    dark_bg: str = "#2d2d2d"
    dark_text: str = "#ffffff"
    dark_hover_bg: str = "#3d3d3d"
    dark_selected_bg: str = "#0066cc"
    
    # 动画
    animation_duration: int = 100  # 毫秒
    fade_in: bool = True
    slide_in: bool = True

    def get_theme_colors(self) -> dict:
        """获取当前主题颜色"""
        if self.theme == "dark":
            return {
                "bg_color": self.dark_bg,
                "text_color": self.dark_text,
                "hover_bg": self.dark_hover_bg,
                "selected_bg": self.dark_selected_bg,
            }
        elif self.theme == "system":
            # 尝试获取系统主题
            try:
                from gi.repository import Gtk
                screen = Gdk.Screen.get_default()
                style_context = Gtk.StyleContext()
                style_context.set_class_name("candidate-panel")
                if screen:
                    style_context.add_class("theme-dark")
                return self.dark_colors
            except:
                return self.light_colors
        else:
            return self.light_colors

    def to_dict(self) -> dict:
        """转换为字典"""
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict) -> 'CandidatePanelConfig':
        """从字典创建配置"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config

    @property
    def dark_colors(self) -> dict:
        """暗色主题颜色"""
        return {
            "bg_color": self.dark_bg,
            "text_color": self.dark_text,
            "hover_bg": self.dark_hover_bg,
            "selected_bg": self.dark_selected_bg,
        }

    @property
    def light_colors(self) -> dict:
        """亮色主题颜色"""
        return {
            "bg_color": self.bg_color,
            "text_color": self.text_color,
            "hover_bg": self.hover_bg,
            "selected_bg": self.selected_bg,
        }

    def validate(self) -> bool:
        """验证配置"""
        # 检查窗口尺寸
        if self.width <= 0 or self.height <= 0:
            return False
        
        # 检查字体大小
        if self.font_size < 10 or self.font_size > 30:
            return False
        
        # 检查候选词数量
        if self.max_candidates < 1 or self.max_candidates > 9:
            return False
        
        return True

    def get_effective_height(self) -> int:
        """获取有效高度"""
        return self.height - (self.margin_top + self.margin_bottom)

    def get_effective_width(self) -> int:
        """获取有效宽度"""
        return self.width - (self.margin_start + self.margin_end)


# 默认配置
DEFAULT_CONFIG = CandidatePanelConfig()
