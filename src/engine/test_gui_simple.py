#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IBus 输入法引擎 - 简化 GUI 测试
无需 Xvfb，使用虚拟显示
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# 添加路径
sys.path.insert(0, '/home/doudou/.openclaw/workspace/src/engine')

from input_engine import create_engine, EventType


class SimplifiedInputTester(QWidget):
    """简化版输入法测试界面"""
    
    def __init__(self):
        super().__init__()
        self.engine = create_engine(max_candidates=6)
        self.setup_ui()
        self.setup_events()
        
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle('IBus 输入法测试 - 简化版')
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('IBus 输入法引擎 - 测试')
        title.setStyleSheet('font-size: 16px; font-weight: bold;')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 输入区域
        input_frame = QFrame()
        input_frame.setFixedHeight(60)
        input_layout = QHBoxLayout(input_frame)
        
        input_label = QLabel('拼音输入：')
        input_layout.addWidget(input_label)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText('输入：nihao, zhongguo, bu...')
        self.input_text.setFont(QFont('Arial', 12))
        self.input_layout.addWidget(self.input_text, 1)
        
        self.input_layout.addStretch()
        layout.addWidget(input_frame)
        
        # 候选词显示
        self.candidates_label = QLabel('候选词将显示在这里...')
        self.candidates_label.setAlignment(Qt.AlignCenter)
        self.candidates_label.setStyleSheet('font-size: 14px; padding: 8px;')
        layout.addWidget(self.candidates_label)
        
        # 状态
        status_label = QLabel('状态：引擎就绪')
        status_label.setStyleSheet('color: #2ecc71; font-size: 12px;')
        layout.addWidget(status_label)
        
        self.setLayout(layout)
        
        # 计数器
        self.input_count = 0
        self.cand_count = 0
        self.commit_count = 0
        
    def setup_events(self):
        """设置事件监听"""
        
        def on_commit(data):
            self.commit_count += 1
            text = data.get('text', '')
            self.candidates_label.setText(f'✓ 已提交：{text}')
            self.candidates_label.setStyleSheet('color: #3498db; padding: 8px;')
        
        def on_candidates(data):
            self.cand_count += 1
            
            if data.get('type') == 'shown':
                candidates_html = ''
                for i, c in enumerate(data['candidates'][:6], 1):
                    candidates_html += f'<div>{i}. <b>{c.get("word", c)}</b> ({c.get("pinyin", "")})</div>'
                
                if candidates_html:
                    self.candidates_label.setText('<div>' + candidates_html + '</div>')
                    self.candidates_label.setStyleSheet('font-size: 12px; padding: 5px;')
        
        self.engine.on_event(EventType.CANDIDATE_COMMIT, on_commit)
        self.engine.on_event(EventType.CANDIDATE_SHOWN, on_candidates)
        
    def process_input(self, text):
        """处理输入"""
        if text.strip():
            self.input_text.setText(text)
            self.engine.process_input(text)
            self.candidates_label.setText('💡 按数字键选择或空格提交...')
            self.candidates_label.setStyleSheet('color: #f39c12; padding: 8px;')


def main():
    """主函数 - 使用虚拟显示"""
    
    print("="*60)
    print("IBus 输入法引擎 - GUI 测试")
    print("="*60)
    
    # 尝试创建虚拟显示
    try:
        from pyvirtualdisplay import Display
        
        print("创建虚拟显示环境...")
        display = Display(visible=False, size=(800, 600))
        display.start()
        print("✓ 虚拟显示已启动")
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建测试窗口
        window = SimplifiedInputTester()
        window.show()
        
        print("✓ 测试窗口已显示")
        
        # 模拟输入和测试
        print("\n开始模拟测试...")
        
        # 测试用例
        test_cases = [
            ("nihao", "你好"),
            ("zhongguo", "中国"),
            ("python", "Python"),
            ("bu", "不"),
            ("chu", "处"),
            ("bo", "剥")
        ]
        
        for pinyin, expected in test_cases:
            print(f"\n输入：{pinyin}")
            window.process_input(pinyin)
            if window.engine.is_composing():
                window.engine.commit()
                print(f"提交：{expected}")
        
        print("\n测试完成！")
        
        # 等待用户关闭
        sys.exit(app.exec_())
        
    except ImportError:
        print("✗ pyvirtualdisplay 未安装")
        print("提示：pip3 install pyvirtualdisplay")
        
        # 降级：直接运行但不显示 GUI
        print("\n降级模式：直接运行引擎测试")
        
        from engine.input_engine import create_engine, EventType
        
        engine = create_engine(max_candidates=6)
        
        def on_commit(data):
            print(f"✓ 提交：{data.get('text', '')}")
        
        def on_candidates(data):
            print(f"📋 候选词 ({len(data.get('candidates', []))})")
            for i, c in enumerate(data.get('candidates', [])[:3], 1):
                print(f"  {i}. {c.get('word', c)} ({c.get('pinyin', '')})")
        
        engine.on_event(EventType.CANDIDATE_COMMIT, on_commit)
        engine.on_event(EventType.CANDIDATE_SHOWN, on_candidates)
        
        # 测试用例
        test_cases = [
            ("nihao", "你好"),
            ("zhongguo", "中国"),
            ("python", "Python"),
            ("bu", "不"),
            ("chu", "处"),
            ("bo", "剥")
        ]
        
        for pinyin, expected in test_cases:
            print(f"\n输入：{pinyin}")
            engine.process_input(pinyin)
            if engine.is_composing():
                engine.commit()
                print(f"提交：{expected}")
        
        print("\n✓ 引擎测试完成")
        sys.exit(0)


if __name__ == "__main__":
    main()