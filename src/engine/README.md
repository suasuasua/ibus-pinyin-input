# IBus 中文输入法核心引擎

本项目实现了 IBus 中文输入法的核心引擎功能，包括拼音转换、候选词排序、事件处理和输入逻辑。

## 📁 项目结构

```
src/engine/
├── input_engine.py    # 核心引擎类
├── pinyin_converter.py # 拼音转换器
├── ranker.py          # 候选词排序器
└── events.py          # 事件处理模块

tests/
└── test_engine.py     # 单元测试
```

## 🚀 快速开始

### 安装依赖

```bash
pip install pypinyin
```

### 基本使用

```python
from src.engine.input_engine import create_engine
from src.engine.events import EventType

# 创建引擎
engine = create_engine()

# 监听事件
def on_commit(event):
    print(f"提交：{event.data['text']}")

engine.on_event(EventType.CANDIDATE_COMMIT, on_commit)

# 处理输入
engine.process_input("你好世界")
candidates = engine.get_candidates()
print(f"候选词：{candidates}")

# 提交
result = engine.commit()
print(f"已提交：{result}")
```

## 📚 模块说明

### 1. input_engine.py - 核心引擎

**InputEngine 类** - 核心输入引擎

主要方法：
- `process_input(text)`: 处理输入文本
- `process_char(char)`: 处理单个字符
- `commit(index)`: 提交候选词
- `select_candidate(index)`: 选择候选词
- `delete_char(count)`: 删除字符
- `switch_language(lang)`: 切换语言

**SimpleInputEngine 类** - 简单输入引擎（仅基于词频排序）

### 2. pinyin_converter.py - 拼音转换器

**PinyinConverter 类** - 拼音转换和缓存

主要方法：
- `convert(text, tone_type)`: 转换文本为拼音
- `get_pinyin(char)`: 获取字符拼音
- `clear_cache()`: 清除缓存
- `is_common_character(char)`: 检查常用字符

支持的 tone_type：
- `none`: 无声调
- `single`: 单字母声调
- `number`: 数字声调
- `symbol`: 符号声调

### 3. ranker.py - 候选词排序器

**Ranker 类** - 智能排序（基于词频、上下文、用户偏好）

主要方法：
- `rank_candidates(candidates)`: 排序候选词
- `add_to_history(text)`: 添加用户历史
- `get_word_frequency(word)`: 获取词频
- `update_frequency(word, freq)`: 更新词频

**SimpleRanker 类** - 简单排序（仅基于词频）

### 4. events.py - 事件处理模块

**IBusEventEmitter 类** - IBus 事件发射器

主要方法：
- `on(event_type, callback)`: 监听事件
- `emit_char(char)`: 发射字符事件
- `emit_candidates(candidates)`: 发射候选词事件
- `emit_commit(text)`: 发射提交事件
- `emit_language_switch(from_lang, to_lang)`: 发射语言切换事件

**EventHandler 类** - 事件处理器

主要方法：
- `connect(event_type, callback)`: 连接处理器
- `disconnect(event_type, callback)`: 断开处理器
- `filter_event(event, callback)`: 过滤事件
- `emit(event)`: 发射事件

## 🧪 运行测试

```bash
# 运行所有测试
python tests/test_engine.py

# 或运行特定测试
python -m pytest tests/test_engine.py::TestPinyinConverter -v
```

## 📝 注意事项

1. **词频字典**: 默认词频字典是示例数据，实际项目中应从词典文件加载
2. **多音字**: 目前支持常用多音字，完整实现需要集成 pypinyin 库
3. **缓存机制**: 拼音转换器使用缓存提高性能，可通过 `clear_cache()` 清除
4. **上下文匹配**: 基于简单 Jaccard 相似度，实际项目可使用更复杂的算法

## 🔧 扩展建议

1. **集成完整词典**: 替换示例词频字典为真实词典
2. **优化排序算法**: 使用深度学习模型进行排序
3. **用户学习**: 实现用户输入习惯学习
4. **自定义回调**: 支持 IBus 回调函数配置
5. **性能优化**: 使用多线程处理拼音转换

## 📄 License

MIT License
