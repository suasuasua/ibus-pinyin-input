# IBus Pinyin - 架构设计文档

## 📚 目录

- [1. 系统概述](#1-系统概述)
- [2. 架构设计原则](#2-架构设计原则)
- [3. 目录结构](#3-目录结构)
- [4. 核心模块](#4-核心模块)
- [5. 数据流](#5-数据流)
- [6. 配置系统](#6-配置系统)
- [7. 插件系统](#7-插件系统)
- [8. 扩展性](#8-扩展性)

## 1. 系统概述

### 1.1 系统目标

构建一个高性能、可扩展的中文拼音输入法引擎，严格遵循 IBus 框架和 GNOME 项目规范。

### 1.2 技术栈

- **核心框架**: IBus 1.5+
- **GUI**: GTK3 3.20+
- **语言**: Python 3.10+
- **构建系统**: meson/ninja
- **打包工具**: python-gobject

### 1.3 设计原则

1. **模块化**: 每个功能独立模块，易于维护和扩展
2. **可配置**: 所有行为可通过配置文件控制
3. **高性能**: 优化的拼音转换和候选词管理
4. **兼容性**: 遵循 IBus 官方 API 和 GNOME 规范
5. **可扩展**: 支持插件系统，便于添加新功能

## 2. 架构设计原则

### 2.1 分层架构

```
┌─────────────────────────────────────────┐
│         用户界面层 (GTK3)                │
│  ┌─────────────────────────────────┐    │
│  │  候选词窗口 / 状态指示器          │    │
│  └─────────────────────────────────┘    │
├─────────────────────────────────────────┤
│         业务逻辑层                       │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │  拼音引擎   │  │  候选词管理      │   │
│  │  (Engine)   │  │  (Candidate)     │   │
│  └─────────────┘  └─────────────────┘   │
├─────────────────────────────────────────┤
│         数据访问层                       │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │  字典访问   │  │  频率统计       │   │
│  │  (Dict)     │  │  (Frequency)     │   │
│  └─────────────┘  └─────────────────┘   │
├─────────────────────────────────────────┤
│         基础设施层                       │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │  IBus API   │  │  配置管理       │   │
│  │  (Adapter)  │  │  (Config)        │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
```

### 2.2 依赖关系

- 上层依赖下层，不反向依赖
- 业务逻辑层不直接依赖 IBus API
- 数据访问层封装所有外部接口

## 3. 目录结构

```
ibus-pinyin/
├── src/
│   ├── engine/              # 核心引擎模块
│   │   ├── __init__.py
│   │   ├── engine.py        # IBus 引擎主类 (EngineAdapter)
│   │   ├── candidate.py     # 候选词管理 (CandidateManager)
│   │   ├── input_method.py  # 输入方法接口 (InputMethod)
│   │   ├── context.py       # 上下文处理 (ContextManager)
│   │   └── key_event.py     # 键盘事件处理
│   │
│   ├── plugin/              # 插件系统
│   │   ├── __init__.py
│   │   ├── base.py          # 插件基类 (PluginBase)
│   │   ├── loader.py        # 插件加载器
│   │   ├── dictionary.py    # 字典插件 (DictionaryPlugin)
│   │   ├── cloud.py         # 云端同步 (CloudSyncPlugin)
│   │   └── learning.py      # 学习插件 (LearningPlugin)
│   │
│   ├── util/                # 工具模块
│   │   ├── __init__.py
│   │   ├── pinyin.py        # 拼音转换工具
│   │   ├── frequency.py     # 频率统计工具
│   │   ├── theme.py         # 主题处理
│   │   ├── cache.py         # 缓存管理
│   │   └── logger.py        # 日志工具
│   │
│   ├── config/              # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py      # 配置加载/保存
│   │   ├── schema.py        # 配置模式定义
│   │   └── default.py       # 默认配置
│   │
│   └── gui/                 # GUI 组件 (可选)
│       ├── __init__.py
│       ├── candidate_window.py  # 候选词窗口
│       └── status_bar.py      # 状态栏
│
├── docs/                    # 文档
│   ├── ARCHITECTURE.md     # 本文件
│   ├── API.md              # API 接口文档
│   └── CONFIG.md           # 配置说明
│
├── tests/                   # 测试
│   ├── unit/               # 单元测试
│   │   ├── test_engine.py
│   │   ├── test_pinyin.py
│   │   └── test_config.py
│   └── integration/        # 集成测试
│       └── test_full_flow.py
│
├── scripts/                 # 脚本
│   ├── install.py          # 安装脚本
│   └── uninstall.py        # 卸载脚本
│
├── requirements.txt         # Python 依赖
├── setup.py                 # 安装配置
├── Makefile                 # 构建脚本
├── meson.build              # Meson 构建文件
└── LICENSE
```

## 4. 核心模块

### 4.1 Engine (引擎主类)

**位置**: `src/engine/engine.py`

**职责**: 
- 实现 IBus 引擎接口
- 管理输入状态
- 协调各模块工作

**关键类**:
```python
class Engine(IBusEngine):
    """IBus 引擎适配器"""
    
    def __init__(self):
        self.candidate_manager = CandidateManager()
        self.context_manager = ContextManager()
        self.plugin_manager = PluginManager()
        self.settings = Settings()
    
    # IBus API 实现
    def commit_text(self, text):
        pass
    
    def preedit_text(self, text, pos):
        pass
    
    def select_candidate(self, index):
        pass
    
    # 内部方法
    def _process_key_event(self, event):
        pass
    
    def _update_candidate_window(self):
        pass
```

### 4.2 CandidateManager (候选词管理)

**位置**: `src/engine/candidate.py`

**职责**:
- 管理候选词列表
- 处理候选词选择
- 优化候选词排序

**关键类**:
```python
class CandidateManager:
    """候选词管理器"""
    
    def __init__(self):
        self.candidates = []  # 候选词列表
        self.selected_index = 0  # 选中索引
        self.context = {}  # 上下文信息
    
    # 核心方法
    def add_candidate(self, text, freq=1.0):
        pass
    
    def clear_candidates(self):
        pass
    
    def select(self, index):
        pass
    
    def get_sorted_candidates(self, context):
        """根据上下文和频率排序"""
        pass
    
    def optimize_ordering(self, history):
        """基于历史优化排序"""
        pass
```

### 4.3 PinyinConverter (拼音转换器)

**位置**: `src/util/pinyin.py`

**职责**:
- 拼音到汉字的转换
- 多音字处理
- 模糊匹配

**关键类**:
```python
class PinyinConverter:
    """拼音转换器"""
    
    def __init__(self):
        self.dict_engine = DictionaryEngine()
        self.freq_engine = FrequencyEngine()
    
    def convert(self, pinyin):
        """转换拼音到候选词列表"""
        pass
    
    def convert_with_context(self, pinyin, context):
        """基于上下文转换"""
        pass
    
    def handle_polyphone(self, pinyin, history):
        """处理多音字"""
        pass
    
    def fuzzy_match(self, pinyin, threshold=0.8):
        """模糊匹配"""
        pass
```

### 4.4 DictionaryEngine (字典引擎)

**位置**: `src/plugin/dictionary.py`

**职责**:
- 加载字典文件
- 提供拼音到汉字的映射
- 支持多种字典格式

**关键类**:
```python
class DictionaryEngine:
    """字典引擎"""
    
    def __init__(self):
        self.dict_files = []
        self.index = None
    
    def load_dict(self, path):
        """加载字典文件"""
        pass
    
    def lookup(self, pinyin):
        """查找拼音对应的汉字"""
        pass
    
    def get_candidates(self, pinyin, limit=10):
        """获取候选词"""
        pass
    
    def update(self, pinyin, candidates, freq):
        """更新字典"""
        pass
```

## 5. 数据流

### 5.1 输入流程

```
用户输入 → 键盘事件 → KeyEventListener
    ↓
ContextManager (记录上下文)
    ↓
PinyinConverter (转换拼音)
    ↓
DictionaryEngine (查询字典)
    ↓
CandidateManager (生成候选词)
    ↓
Engine (更新 UI)
    ↓
候选词窗口显示
```

### 5.2 选择流程

```
用户按下数字键 → Engine.select_candidate(index)
    ↓
CandidateManager.select(index)
    ↓
Engine.commit_text(text)
    ↓
IBus API 提交文本
    ↓
ContextManager (记录历史)
    ↓
LearningPlugin (可选：学习)
```

### 5.3 配置加载流程

```
Engine 初始化 → Settings.load()
    ↓
读取默认配置 (default.py)
    ↓
读取用户配置 (~/.config/ibus-pinyin/settings.ini)
    ↓
读取系统配置 (/etc/ibus-pinyin/settings.ini)
    ↓
合并配置 → Engine 使用
```

## 6. 配置系统

### 6.1 配置层级

1. **默认配置**: `src/config/default.py`
2. **用户配置**: `~/.config/ibus-pinyin/settings.ini`
3. **系统配置**: `/etc/ibus-pinyin/settings.ini`

### 6.2 配置格式

```ini
[general]
language = zh_CN
input_mode = pinyin
candidate_count = 6
candidate_style = popup

[pinyin]
enable_polyphone = true
enable_fuzzy = true
fuzzy_threshold = 0.8

[candidate]
max_candidates = 10
sort_mode = frequency
optimize = true

[learning]
enable = true
auto_learn = true
max_history = 1000

[theme]
theme = default
color_scheme = dark
font = Noto Sans CJK SC 12
```

### 6.3 配置管理

```python
class Settings:
    """配置管理器"""
    
    def __init__(self):
        self.config = {}
        self.default_config = {}
    
    def load(self):
        """加载所有配置"""
        self._load_default()
        self._load_user()
        self._load_system()
        self._merge()
    
    def get(self, key, default=None):
        """获取配置值"""
        pass
    
    def set(self, key, value):
        """设置配置值"""
        pass
    
    def save(self):
        """保存配置"""
        pass
```

## 7. 插件系统

### 7.1 插件架构

```python
class PluginBase(Plugin):
    """插件基类"""
    
    def __init__(self, name, version, author):
        self.name = name
        self.version = version
        self.author = author
        self.enabled = False
    
    def initialize(self, engine):
        """初始化插件"""
        pass
    
    def shutdown(self):
        """关闭插件"""
        pass
    
    def on_key_event(self, event):
        """键盘事件回调"""
        pass
    
    def on_commit(self, text):
        """提交文本回调"""
        pass
    
    def get_priority(self):
        """插件优先级"""
        return 0
```

### 7.2 插件加载器

```python
class PluginLoader:
    """插件加载器"""
    
    def __init__(self, engine):
        self.engine = engine
        self.plugins = []
    
    def scan(self):
        """扫描插件"""
        pass
    
    def load(self, plugin_path):
        """加载插件"""
        pass
    
    def enable(self, plugin_name):
        """启用插件"""
        pass
    
    def disable(self, plugin_name):
        """禁用插件"""
        pass
    
    def unload(self, plugin_name):
        """卸载插件"""
        pass
```

### 7.3 示例插件

**字典插件** (`src/plugin/dictionary.py`):
```python
class DictionaryPlugin(PluginBase):
    """字典插件"""
    
    def initialize(self, engine):
        self.dict_engine = DictionaryEngine()
        self.dict_engine.load_default_dicts()
    
    def on_key_event(self, event):
        if event.type == KEY_PRESS:
            self.dict_engine.process_key(event.key)
```

## 8. 扩展性

### 8.1 扩展点

1. **自定义拼音规则**: 通过配置或插件
2. **自定义候选词排序**: 实现 `CandidateManager`
3. **自定义主题**: 通过 GTK3 样式
4. **自定义插件**: 实现 `PluginBase`

### 8.2 未来扩展

- **云端同步**: 词库同步
- **AI 辅助**: 智能预测
- **多语言**: 支持日文、韩文等
- **语音输入**: 语音转文字
- **手势输入**: 手势切换

### 8.3 性能优化

1. **缓存**: 拼音转换结果缓存
2. **索引**: 字典索引优化
3. **多线程**: 重型计算异步化
4. **懒加载**: 按需加载资源

---

**版本**: 1.0.0  
**最后更新**: 2026-03-17
