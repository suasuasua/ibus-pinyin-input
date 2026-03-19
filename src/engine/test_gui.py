#!/usr/bin/env python3
"""
IBus 中文输入法引擎 - GUI 测试界面
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QComboBox, QTextEdit,
                             QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.input_engine import create_engine
from engine.events import EventType


class InputMethodTester(QWidget):
    """输入法测试界面"""
    
    def __init__(self):
        super().__init__()
        self.engine = create_engine(max_candidates=6, context_window=10)
        self.setup_ui()
        self.setup_events()
        
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle('IBus 中文输入法引擎 - 测试界面')
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('IBus 中文输入法引擎 - 实时演示')
        title.setStyleSheet('font-size: 18px; font-weight: bold;')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 输入区域
        input_frame = QFrame()
        input_frame.setFixedHeight(80)
        input_layout = QHBoxLayout(input_frame)
        
        input_label = QLabel('请输入拼音：')
        input_label.setFont(QFont('Arial', 14))
        input_layout.addWidget(input_label)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText('例如：nihao, zhongguo, python...')
        self.input_text.setFont(QFont('Arial', 14))
        self.input_text.setMaximumHeight(60)
        input_layout.addWidget(self.input_text, 1)
        
        input_layout.addStretch()
        layout.addWidget(input_frame)
        
        # 候选词显示区域
        self.candidates_label = QLabel('候选词将显示在这里...')
        self.candidates_label.setAlignment(Qt.AlignCenter)
        self.candidates_label.setStyleSheet('font-size: 16px; padding: 10px;')
        layout.addWidget(self.candidates_label)
        
        # 状态信息
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        
        status_label = QLabel('状态：引擎已就绪')
        status_label.setStyleSheet('color: #2ecc71;')
        status_layout.addWidget(status_label)
        
        self.stats_label = QLabel('输入次数：0 | 候选词显示：0 | 提交次数：0')
        self.stats_label.setStyleSheet('font-size: 12px;')
        status_layout.addWidget(self.stats_label)
        
        layout.addWidget(status_frame)
        
        # 说明
        info = QLabel('💡 提示：输入拼音后按回车键查看候选词')
        info.setStyleSheet('color: #95a5a6; font-size: 12px;')
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        self.setLayout(layout)
        
        # 计数器
        self.input_count = 0
        self.cand_count = 0
        self.commit_count = 0
        
    def setup_events(self):
        """设置事件监听"""
        
        def on_commit(event):
            self.commit_count += 1
            self.update_stats()
            text = event.data.get('text', '')
            if text:
                self.input_text.setText(text)
                self.candidates_label.setText(f'✓ 已提交：{text}')
                self.candidates_label.setStyleSheet('color: #3498db; padding: 10px;')
        
        def on_candidates(event):
            self.cand_count += 1
            self.update_stats()
            
            if event.type_ == 'shown':
                candidates_html = ''
                for i, c in enumerate(event.candidates[:6], 1):
                    candidates_html += f'<div style="padding: 5px 0;">{i}. <b>{c.word}</b> ({c.pinyin})</div>'
                
                if not candidates_html:
                    self.candidates_label.setText(f'候选词 ({len(event.candidates)})')
                else:
                    self.candidates_label.setText('<div style="padding: 5px;">' + candidates_html + '</div>')
                    self.candidates_label.setStyleSheet('font-size: 14px; padding: 5px;')
        
        self.engine.on_event(EventType.CANDIDATE_COMMIT, on_commit)
        self.engine.on_event(EventType.CANDIDATE_SHOWN, on_candidates)
        
    def update_stats(self):
        """更新统计信息"""
        self.input_count += 1
        stats = f'输入次数：{self.input_count} | 候选词显示：{self.cand_count} | 提交次数：{self.commit_count}'
        self.stats_label.setText(stats)
    
    def process_input(self, text):
        """处理输入"""
        if text.strip():
            self.input_text.setText(text)
            self.engine.process_input(text)
            self.update_stats()
            
            # 自动显示候选词
            QTimer.singleShot(100, self.on_enter_key)
    
    def on_enter_key(self):
        """模拟回车键"""
        if self.engine.is_composing():
            self.candidates_label.setText('💡 按数字键选择或空格提交...')
            self.candidates_label.setStyleSheet('color: #f39c12; padding: 10px;')


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = InputMethodTester()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
