#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 候选词面板 - 主入口
GTK3 中文输入法候选词面板实现
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import signal
import sys

from src.ui.candidate_panel import CandidatePanel
from src.ui.keyboard_handler import KeyboardHandler
from src.ui.panel_config import CandidatePanelConfig


class IBusCandidatePanel:
    """IBus 候选词面板主类"""

    def __init__(self):
        self.config = CandidatePanelConfig()
        self.panel: Optional[CandidatePanel] = None
        self.handler: Optional[KeyboardHandler] = None
        
        # 信号连接
        self.signals = {
            'candidate-selected': None,
            'selection-changed': None,
            'commit': None,
            'panel-show': None,
            'panel-hide': None,
        }

    def connect_signal(self, signal_name: str, callback):
        """连接信号"""
        if signal_name in self.signals:
            self.signals[signal_name] = callback

    def run(self):
        """运行面板"""
        # 创建主窗口
        self.panel = CandidatePanel()
        
        # 创建键盘处理器
        self.handler = KeyboardHandler(self.panel)
        
        # 设置窗口模式
        self.panel.set_window_mode(self.config.window_mode)
        
        # 更新候选词
        self.panel.update_candidates(self.get_sample_candidates())
        
        # 显示窗口
        self.panel.show()
        
        # 设置焦点
        self.panel.grab_focus()
        
        # 连接信号
        self.panel.connect('candidate-selected', self._on_candidate_selected)
        self.panel.connect('selection-changed', self._on_selection_changed)
        self.panel.connect('commit', self._on_commit)
        self.panel.connect('destroy', self._on_panel_destroy)
        
        # 启动主循环
        print("IBus 候选词面板已启动")
        print("快捷键说明:")
        print("  Tab/Enter - 选择当前候选词")
        print("  数字键 1-9 - 选择候选词")
        print("  ↑/↓ 或方向键 - 移动光标")
        print("  PageUp/PageDown - 滚动")
        print("  w - 切换窗口模式")
        print("  Escape/q - 最小化")
        print("  r - 刷新候选词")
        
        Gtk.main()

    def get_sample_candidates(self) -> list:
        """获取示例候选词"""
        return [
            "你好", "您好", "你", "你们", "你的", "你好啊", "你好呀", "你好吗", "你好吧",
            "测试", "测试 1", "测试 2", "测试 3", "测试 4", "测试 5", "测试 6", "测试 7", "测试 8",
        ]

    def _on_candidate_selected(self, panel: CandidatePanel, candidate: str):
        """候选词选中"""
        print(f"候选词选中：{candidate}")
        if self.signals.get('candidate-selected'):
            self.signals['candidate-selected'](candidate)

    def _on_selection_changed(self, panel: CandidatePanel, candidate: str):
        """候选词选择变化"""
        print(f"选择变化：{candidate}")
        if self.signals.get('selection-changed'):
            self.signals['selection-changed'](candidate)

    def _on_commit(self, panel: CandidatePanel, candidate: str):
        """提交候选词"""
        print(f"提交候选词：{candidate}")
        if self.signals.get('commit'):
            self.signals['commit'](candidate)

    def _on_panel_destroy(self, panel: CandidatePanel):
        """面板销毁"""
        print("面板已销毁")


def main():
    """主函数"""
    try:
        app = IBusCandidatePanel()
        app.run()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
