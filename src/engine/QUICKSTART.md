# IBus 中文输入法核心引擎 - 快速启动指南

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /home/doudou/.openclaw/workspace/src/engine
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 运行所有测试
python tests/test_engine.py

# 或运行特定模块测试
python -m pytest tests/test_engine.py::TestPinyinConverter -v
```

### 3. 基本使用示例

#### 示例 1: 基本输入

```python
from src.engine.input_engine import create_engine
from src.engine.events import EventType

# 创建引擎
engine = create_engine()

# 监听提交事件
def on_commit(event):
    print(f"提交文本：{event.data['text']}")

engine.on_event(EventType.CANDIDATE_COMMIT, on_commit)

# 输入文本
engine.process_input("你好世界")
candidates = engine.get_candidates()
print(f"候选词：{candidates}")

# 提交
result = engine.commit()
print(f"已提交：{result}")
```

#### 示例 2: 监听候选词

```python
from src.engine.events import CandidateEvent

def on_candidates(event):
    if event.type_ == "shown":
        print(f"候选词列表：{event.candidates}")
        print(f"选中索引：{event.index}")

engine.on_event(EventType.CANDIDATE_SHOWN, on_candidates)
```

#### 示例 3: 切换语言

```python
# 切换到英语模式
engine.switch_language("en")

# 验证状态
print(f"是否组字：{engine.is_composing()}")
```

#### 示例 4: 删除字符

```python
# 删除最后一个字符
engine.delete_char(count=1, method="backspace")

# 删除最后两个字符
engine.delete_char(count=2, method="backspace")
```

## 📖 常用 API

### InputEngine 主要方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `process_input(text)` | 处理输入文本 | text: str |
| `process_char(char)` | 处理单个字符 | char: str |
| `commit(index=-1)` | 提交候选词 | index: int, -1 表示全部 |
| `select_candidate(index)` | 选择候选词 | index: int |
| `delete_char(count, method)` | 删除字符 | count: int, method: str |
| `switch_language(lang)` | 切换语言 | lang: str |
| `get_candidates()` | 获取候选词列表 | - |
| `get_selected_candidate()` | 获取选中候选词 | - |
| `get_context()` | 获取上下文 | - |
| `is_composing()` | 检查组字状态 | - |

### PinyinConverter 主要方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `convert(text, tone_type)` | 转换文本为拼音 | text: str, tone_type: str |
| `get_pinyin(char)` | 获取字符拼音 | char: str |
| `clear_cache()` | 清除缓存 | - |
| `clear_specific_cache(char)` | 清除指定字符缓存 | char: str |
| `is_common_character(char)` | 检查常用字符 | char: str |

### Ranker 主要方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `rank_candidates(candidates)` | 排序候选词 | candidates: List[CandidateWord] |
| `add_to_history(text)` | 添加用户历史 | text: str |
| `get_word_frequency(word)` | 获取词频 | word: str |
| `update_frequency(word, freq)` | 更新词频 | word: str, freq: float |
| `clear_history()` | 清除历史 | - |

## 🎯 事件类型

```python
from src.engine.events import EventType

# 输入事件
EventType.INPUT_CHAR      # 字符输入
EventType.INPUT_TEXT      # 文本输入
EventType.INPUT_DELETE    # 删除字符

# 候选词事件
EventType.CANDIDATE_SHOWN     # 显示候选词
EventType.CANDIDATE_SELECTED  # 选择候选词
EventType.CANDIDATE_COMMIT    # 提交候选词

# 键盘事件
EventType.KEY_PRESS   # 按键按下
EventType.KEY_RELEASE # 按键释放

# 语言切换事件
EventType.LANG_SWITCH   # 切换语言
EventType.LANG_CHANGED  # 语言改变

# 引擎事件
EventType.ENGINE_STARTED   # 引擎启动
EventType.ENGINE_STOPPED   # 引擎停止
EventType.ENGINE_ERROR     # 引擎错误
```

## 🔧 高级用法

### 自定义事件过滤

```python
from src.engine.events import EventHandler, Event

def filter_allow_composing(event: Event) -> bool:
    """只允许组字状态下的事件"""
    if hasattr(event, 'data'):
        return event.data.get('allow_composing', True)
    return True

# 添加过滤器
event_handler.add_filter(EventType.INPUT_CHAR, filter_allow_composing)
```

### 自定义排序策略

```python
from src.engine.ranker import Ranker

# 创建自定义排序器
ranker = Ranker(
    word_freq={'你好': 100, '世界': 80},
    user_history=['你好', '世界'],
    context_window=10,
    max_candidates=6
)

# 添加词频
ranker.update_frequency('编程', 150)
```

### 性能优化 - 使用缓存

```python
from src.engine.pinyin_converter import create_converter

# 创建转换器（自动使用缓存）
converter = create_converter(max_cache_size=10000)

# 缓存会自动管理
pinyin = converter.get_pinyin('中')  # 从缓存获取
```

## 🐛 调试技巧

### 查看当前状态

```python
engine = create_engine()
engine.process_input("测试")

# 查看状态
print(f"当前输入：{engine.get_current_input()}")
print(f"候选词：{engine.get_candidates()}")
print(f"选中索引：{engine.input_state.selected_index}")
print(f"上下文：{engine.get_context()}")
print(f"是否组字：{engine.is_composing()}")
```

### 调试事件流

```python
def debug_event(event):
    print(f"\n事件类型：{event.type}")
    print(f"事件数据：{event.data}")
    print(f"时间戳：{event.timestamp}")

engine.on_event(EventType.INPUT_CHAR, debug_event)
engine.on_event(EventType.CANDIDATE_SHOWN, debug_event)
engine.on_event(EventType.CANDIDATE_COMMIT, debug_event)
```

## 📊 性能基准

```bash
# 运行性能测试
python -m pytest tests/test_engine.py::TestPerformance -v
```

## 📚 更多资源

- 完整文档：`src/engine/README.md`
- 项目总结：`PROJECT_SUMMARY.md`
- 单元测试：`tests/test_engine.py`

---

**提示**: 对于生产环境，请替换示例词典数据为真实汉语词典。
