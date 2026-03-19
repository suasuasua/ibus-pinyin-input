# IBus 候选词面板 UI

IBus 中文输入法的候选词面板界面实现，使用 GTK3 + PyGObject。

## 📋 功能特性

- **候选词显示**：支持动态更新候选词列表
- **光标选择**：Tab/Enter 键选择当前候选词
- **数字键选择**：1-9 选择对应候选词
- **方向键导航**：↑/↓ 键移动光标
- **滚动操作**：PageUp/PageDown 滚动列表
- **窗口模式切换**：支持跟随光标或独立窗口
- **响应式设计**：支持不同屏幕尺寸
- **主题支持**：亮色/暗色主题切换
- **快捷键配置**：可自定义快捷键

## 📁 文件结构

```
src/ui/
├── candidate_panel.py    # 候选词面板核心类
├── keyboard_handler.py   # 键盘事件处理器
├── panel_config.py       # 面板配置
├── styles.css            # CSS3 样式表
└── main.py               # 主入口文件

tests/
└── test_ui.py            # 单元测试文件
```

## 🚀 安装依赖

```bash
# 安装 PyGObject
pip install PyGObject

# 或安装 gi
pip install PyGObject[gi]
```

## 💻 使用方法

### 方式一：运行主程序

```bash
cd /home/doudou/.openclaw/workspace
python -m src.ui.main
```

### 方式二：创建 IBus 插件

在 IBus 引擎中集成：

```python
from src.ui.candidate_panel import CandidatePanel
from src.ui.keyboard_handler import KeyboardHandler

# 创建面板
panel = CandidatePanel(parent=your_window)

# 创建键盘处理器
handler = KeyboardHandler(panel)

# 更新候选词
panel.update_candidates(candidates)

# 显示
panel.show()
```

## ⌨️ 快捷键说明

| 快捷键 | 功能 |
|--------|------|
| Tab/Enter | 选择当前候选词 |
| 数字键 1-9 | 选择对应候选词 |
| ↑/↓ 或方向键 | 移动光标 |
| PageUp/PageDown | 滚动列表 |
| w | 切换窗口模式 |
| Escape/q | 最小化窗口 |
| r | 刷新候选词 |

## 🎨 配置选项

在 `panel_config.py` 中配置：

```python
class CandidatePanelConfig:
    # 窗口尺寸
    width: int = 320
    height: int = 280
    
    # 字体大小
    font_size: int = 18
    
    # 候选词数量
    max_candidates: int = 9
    
    # 主题
    theme: str = "light"  # light, dark, system
    
    # 跟随光标
    follow_cursor: bool = True
    
    # 窗口模式
    window_mode: bool = False
```

## 🧪 运行测试

```bash
cd /home/doudou/.openclaw/workspace
python -m tests.test_ui
```

## 📝 样式定制

编辑 `styles.css` 自定义样式：

```css
.candidate {
    font-size: 18px;
    color: #333333;
    padding: 6px 12px;
}

.candidate:selected {
    background-color: #e8f4fd;
    color: #0066cc;
}
```

## 🔧 集成到 IBus

### 1. 创建 IBus 引擎

```python
from ibus_engine import IBusEngine
from src.ui.candidate_panel import CandidatePanel

class MyIBusEngine(IBusEngine):
    def commit(self, text):
        # 处理提交
        pass
    
    def candidate_update(self, candidates, cursor_pos):
        # 更新候选词
        panel = CandidatePanel()
        panel.update_candidates(candidates, cursor_pos)
        panel.show()
```

### 2. 注册引擎

```bash
# 在 IBus 配置中添加
ibus-daemon --replace --user
```

## 📖 技术细节

### 核心组件

- **CandidatePanel**: 候选词面板核心类
  - 窗口管理
  - 候选词渲染
  - 事件处理
  
- **KeyboardHandler**: 键盘事件处理器
  - 按键映射
  - 光标移动
  - 选择逻辑
  
- **PanelConfig**: 面板配置
  - 窗口配置
  - 主题配置
  - 快捷键配置

### 事件流

```
用户输入 → IBus 引擎 → 更新候选词 → 面板渲染 → 键盘事件 → 选择候选词
```

## 🐛 常见问题

### 问题 1：窗口不跟随光标

**原因**：`follow_cursor` 配置为 `False`

**解决**：设置 `follow_cursor = True`

### 问题 2：样式不生效

**原因**：GTK 版本问题

**解决**：升级 GTK 版本到 3.22+

### 问题 3：键盘事件不响应

**原因**：窗口焦点丢失

**解决**：确保窗口保持焦点，使用 `grab_focus()`

## 📄 许可证

MIT License

## 📞 支持

如有问题，请提交 Issue 或联系开发者。
