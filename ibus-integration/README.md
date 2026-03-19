# IBus 框架完整集成项目

## 项目概述

本项目实现了将输入法引擎完整集成到 IBus (Intelligent Input Bus) 框架。IBus 是 Linux/Unix 系统上的开源输入法框架，支持多语言输入。

## 项目结构

```
ibus-integration/
├── src/
│   ├── ibus-input-engine.c      # 核心输入法引擎实现
│   ├── ibus-input-engine.h      # 引擎头文件
│   ├── ibus-input-engine-desc.c # 引擎描述文件
│   ├── ibus-input-engine-desc.h # 描述头文件
│   └── ibus-input-engine.xml    # 引擎配置文件
├── docs/
│   ├── IBUS-INTRODUCTION.txt    # IBus 框架介绍
│   ├── IBUS-API-REFERENCE.txt   # IBus API 参考
│   └── IBUS-PLUGIN-STRUCTURE.txt # 插件结构说明
├── scripts/
│   ├── install.sh               # 安装脚本
│   ├── uninstall.sh             # 卸载脚本
│   └── configure.sh             # 配置脚本
├── tests/
│   └── test-input-engine.sh     # 测试脚本
└── README.md                    # 项目说明
```

## 核心功能

1. **IBus 框架接口对接**
   - 实现 IBusEngine 接口
   - 实现 IBusEngineSimple 接口
   - 支持 GDBus 通信

2. **输入法插件开发**
   - 实现按键事件处理 (process_key_event)
   - 实现焦点管理 (focus_in/focus_out)
   - 实现候选词选择 (candidate_clicked)
   - 实现预编辑文本更新 (update_preedit_text)

3. **事件回调机制**
   - 键盘按键回调
   - 焦点进入/退出回调
   - 候选词点击回调
   - 页面上下翻页回调

4. **配置和安装**
   - 自动生成配置文件
   - 支持 gsettings 配置
   - 提供安装/卸载脚本

## IBus 核心接口说明

### IBusEngine 核心回调函数

| 函数 | 说明 | 参数 |
|------|------|------|
| process_key_event | 处理键盘按键事件 | keyval, keycode, state |
| focus_in | 输入法获得焦点 | 无 |
| focus_out | 输入法失去焦点 | 无 |
| reset | 重置输入法状态 | 无 |
| enable | 启用输入法 | 无 |
| disable | 禁用输入法 | 无 |
| set_cursor_location | 设置光标位置 | x, y, w, h |
| set_capabilities | 设置客户端能力 | caps |
| page_up/page_down | 翻页 | 无 |
| candidate_clicked | 候选词点击 | index, button, state |
| set_surrounding_text | 设置上下文文本 | text, cursor, anchor |
| process_hand_writing_event | 处理手写事件 | coordinates |
| cancel_hand_writing | 取消手写 | n_strokes |
| set_content_type | 设置内容类型 | purpose, hints |

### 主要函数接口

| 函数 | 说明 |
|------|------|
| ibus_engine_commit_text() | 提交文本 |
| ibus_engine_update_preedit_text() | 更新预编辑文本 |
| ibus_engine_update_lookup_table() | 更新候选词表 |
| ibus_engine_show_preedit_text() | 显示预编辑区 |
| ibus_engine_hide_preedit_text() | 隐藏预编辑区 |
| ibus_engine_show_lookup_table() | 显示候选词表 |
| ibus_engine_hide_lookup_table() | 隐藏候选词表 |
| ibus_engine_delete_surrounding_text() | 删除上下文文本 |
| ibus_engine_get_surrounding_text() | 获取上下文文本 |

## 开发步骤

1. **实现 IBusEngineSimple 继承**
   - 使用 G_DEFINE_TYPE_WITH_PRIVATE 宏
   - 实现 class_init 和 instance_init 函数

2. **注册回调函数**
   - engine_class->process_key_event
   - engine_class->focus_in
   - engine_class->focus_out
   - engine_class->reset
   - engine_class->candidate_clicked
   - 其他必要回调

3. **实现引擎逻辑**
   - 按键处理逻辑
   - 候选词管理
   - 输入状态管理

4. **创建引擎描述文件**
   - 引擎名称
   - 引擎图标
   - 支持的语言

5. **编写配置文件**
   - 引擎配置选项
   - 默认设置

## 参考文档

- [IBus 官方文档](https://ibus.github.io/docs/)
- [IBus GitHub](https://github.com/ibus/ibus)
- [IBus 示例代码](https://github.com/ibus/ibus/blob/main/src/ibusenginesimple.c)
