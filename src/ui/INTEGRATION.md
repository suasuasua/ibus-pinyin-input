# IBus 候选词面板集成指南

## 📌 概述

本指南说明如何将候选词面板集成到 IBus 中文输入法引擎中。

## 🛠️ 前置要求

### 系统依赖

- Python 3.8+
- PyGObject (GTK3)
- IBus 开发库

### 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get install libgtk-3-dev python3-gi python3-gi-cairo

# Fedora
sudo dnf install gtk3-devel python3-gobject

# Arch Linux
sudo pacman -S gtk3 python-gobject
```

## 🔧 集成步骤

### 1. 创建 IBus 引擎

```python
from ibus_engine import IBusEngine
from src.ui.candidate_panel import CandidatePanel
from src.ui.keyboard_handler import KeyboardHandler
from src.ui.panel_config import CandidatePanelConfig

class MyCandidatePanel(IBusEngine):
    """IBus 候选词面板引擎"""
    
    def __init__(self):
        super().__init__()
        self.panel = None
        self.handler = None
        self.config = CandidatePanelConfig()
        
        # 注册输入源
        self.register_input_source()

    def register_input_source(self):
        """注册输入源"""
        # 创建输入源
        input_source = IBusInputSource(
            name="中文输入法",
            engine_type="IBus",
            layout="cn",
            variant="zh-pinyin"
        )
        
        # 添加引擎
        input_source.add_engine(self)
        
        # 设置默认
        IBusEngine.set_default(input_source)

    def setup_panel(self):
        """设置候选词面板"""
        # 创建主窗口
        main_window = Gtk.Window()
        main_window.set_title("候选词")
        main_window.set_default_size(320, 280)
        
        # 创建面板
        self.panel = CandidatePanel(main_window)
        self.handler = KeyboardHandler(self.panel)
        
        # 设置窗口模式
        self.panel.set_window_mode(self.config.window_mode)
        
        # 设置焦点
        self.panel.grab_focus()
        
        # 连接信号
        self.panel.connect('candidate-selected', self._on_candidate_selected)
        self.panel.connect('selection-changed', self._on_selection_changed)
        self.panel.connect('commit', self._on_commit)
        
        # 返回面板
        return self.panel

    def candidate_update(self, candidates, cursor_pos=None):
        """更新候选词"""
        if self.panel:
            self.panel.update_candidates(candidates, cursor_pos)
            self.panel.show()
            
    def _on_candidate_selected(self, panel, candidate):
        """候选词选中"""
        print(f"选中：{candidate}")
        # 发送选中的字
        self.commit(candidate)

    def _on_selection_changed(self, panel, candidate):
        """选择变化"""
        print(f"变化：{candidate}")

    def _on_commit(self, panel, candidate):
        """提交候选词"""
        print(f"提交：{candidate}")
        self.commit(candidate)

    def candidate_show(self):
        """显示候选词面板"""
        if not self.panel:
            self.panel = self.setup_panel()
        self.panel.show()
        
    def candidate_hide(self):
        """隐藏候选词面板"""
        if self.panel:
            self.panel.minimize()

    def candidate_toggle(self):
        """切换候选词面板"""
        if self.panel and self.panel.get_visible():
            self.candidate_hide()
        else:
            self.candidate_show()

    def key_event(self, key_event):
        """处理键盘事件"""
        # 处理切换窗口模式
        if key_event.keyval == Gdk.KEY_w or key_event.keyval == ord('w'):
            self.panel.toggle_window_mode()
            return IBusKeyEventResult.IGNORE

        # 处理最小化
        if key_event.keyval == Gdk.KEY_Escape or key_event.keyval == ord('q'):
            self.candidate_hide()
            return IBusKeyEventResult.IGNORE

        # 其他事件由键盘处理器处理
        return IBusKeyEventResult.PASS

    def destroy(self):
        """清理资源"""
        if self.panel:
            self.panel.destroy()
            self.panel = None
```

### 2. 创建 IBus 配置

```python
# ibus-candidate-panel.conf
[General]
Name=中文输入法
Description=IBus 中文输入法
Author=IBus Team
Version=1.0.0

[Engine]
Name=CandidatePanelEngine
Engine=MyCandidatePanel
ConfigFile=/usr/share/ibus/candidate-panel.conf

[InputSource]
Name=中文输入法
Layout=cn
Variant=zh-pinyin
Order=1
```

### 3. 安装引擎

```bash
# 编译引擎
python3 setup.py build

# 安装引擎
sudo python3 setup.py install

# 重启 IBus
ibus restart
```

## 📝 配置文件示例

```python
# /etc/ibus/candidate-panel.conf
[General]
# 窗口尺寸
Width=320
Height=280

# 字体大小
FontSize=18

# 最大候选词数量
MaxCandidates=9

# 主题
Theme=light

# 跟随光标
FollowCursor=true

# 窗口模式
WindowMode=false

[Keyboard]
# 选择键
SelectKey=Tab

# 上移键
UpKey=Up

# 下移键
DownKey=Down

# 最小化键
MinimizeKey=Escape

# 切换窗口模式键
ToggleWindowKey=w

# 刷新键
RefreshKey=r

[Theme]
# 亮色主题
BgColor=#ffffff
TextColor=#333333
HoverBg=#f0f0f0
SelectedBg=#e8f4fd

# 暗色主题
DarkBg=#2d2d2d
DarkTextColor=#ffffff
DarkHoverBg=#3d3d3d
DarkSelectedBg=#0066cc
```

## 🧪 测试集成

```python
# test_integration.py
from ibus_engine import IBusEngine
from src.ui.candidate_panel import CandidatePanel

# 创建引擎实例
engine = MyCandidatePanel()

# 创建主窗口
main_window = Gtk.Window()
main_window.set_default_size(800, 600)

# 设置面板
engine.setup_panel()

# 更新候选词
candidates = ["测试 1", "测试 2", "测试 3"]
engine.candidate_update(candidates)

# 显示面板
engine.candidate_show()

# 启动主循环
Gtk.main()
```

## 🔍 调试技巧

### 启用调试日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ibus-candidate-panel')
logger.setLevel(logging.DEBUG)
```

### 捕获异常

```python
try:
    engine = MyCandidatePanel()
    engine.run()
except Exception as e:
    import traceback
    traceback.print_exc()
    logger.error(f"错误：{e}")
```

### 检查 GTK 版本

```python
from gi.repository import Gtk
print(f"GTK 版本：{Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}")
```

## ⚙️ 性能优化

### 1. 减少渲染次数

```python
class OptimizedCandidatePanel(CandidatePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_update_time = 0
        self.update_rate = 0.1  # 100ms
        
    def update_candidates(self, candidates, cursor_pos=None):
        current_time = time.time()
        if current_time - self.last_update_time < self.update_rate:
            return
        self.last_update_time = current_time
        super().update_candidates(candidates, cursor_pos)
```

### 2. 使用 CSS 缓存

```python
css_cache = {}

def get_css_provider():
    if 'provider' not in css_cache:
        css_cache['provider'] = Gtk.CssProvider()
    return css_cache['provider']
```

### 3. 预渲染候选词

```python
class PreRenderedCandidatePanel(CandidatePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pre_rendered = []
        
    def update_candidates(self, candidates, cursor_pos=None):
        # 预渲染所有候选词
        self.pre_rendered = self._render_candidates()
        # 只显示当前选中的
        self.show_selected(self.pre_rendered, cursor_pos)
```

## 📊 性能指标

| 操作 | 耗时 (ms) |
|------|-----------|
| 初始化 | 50-100 |
| 渲染 9 个候选词 | 10-20 |
| 更新候选词 | 5-10 |
| 选择候选词 | 1-5 |
| 窗口跟随 | 5-10 |

## 🎯 最佳实践

1. **及时更新候选词**：在用户输入后立即更新
2. **合理设置窗口大小**：根据屏幕尺寸调整
3. **使用暗色主题**：提高可读性
4. **优化键盘事件处理**：减少不必要的处理
5. **缓存渲染结果**：避免重复渲染

## 📞 技术支持

遇到问题？请：
1. 查看日志
2. 检查 GTK 版本
3. 确认 IBus 配置正确
4. 提交 Issue
