# IBus Input Engine - 使用说明

## 快速开始

### 安装

```bash
# 克隆项目
cd /path/to/ibus-integration

# 运行安装脚本
./scripts/install.sh

# 或使用参数安装
./scripts/install.sh --prefix /opt/myapp

# 清理构建
./scripts/install.sh --clean
```

### 配置

```bash
# 设置默认输入法
./scripts/configure.sh --default

# 配置引擎属性
./scripts/configure.sh --properties

# 查看当前配置
./scripts/configure.sh --status
```

### 卸载

```bash
# 卸载引擎
./scripts/uninstall.sh

# 仅清理构建
./scripts/uninstall.sh --clean
```

## 功能说明

### 引擎特性

- **多语言支持**：支持中文、英文、日文、韩文等多种语言
- **可配置属性**：
  - InputMode - 输入模式
  - CursorStyle - 光标样式
  - ShowPreedit - 预编辑显示
  - SoundEnabled - 输入音效

### 按键快捷键

| 快捷键 | 功能 |
|--------|------|
| Super+Shift | 切换到下一个输入法 |
| Super+Shift+Ctrl | 切换到上一个输入法 |

### 引擎属性配置

```bash
# 设置输入模式
gsettings set org.freedesktop.ibus.engine.my-input-engine InputMode "Normal"

# 设置光标样式
gsettings set org.freedesktop.ibus.engine.my-input-engine CursorStyle "Blinking"

# 设置预编辑显示
gsettings set org.freedesktop.ibus.engine.my-input-engine ShowPreedit "Auto"

# 设置音效
gsettings set org.freedesktop.ibus.engine.my-input-engine SoundEnabled "Enabled"
```

## 测试

### 运行测试套件

```bash
./tests/test-input-engine.sh

# 详细输出
./tests/test-input-engine.sh --verbose
```

### 手动测试

```bash
# 1. 检查引擎是否安装
ls /usr/share/ibus/engines/my-input-engine.xml

# 2. 检查 IBus 守护进程
pgrep ibus-daemon

# 3. 重启 IBus
sudo ibus-daemon --replace

# 4. 设置引擎为默认
gsettings set org.freedesktop.ibus.settings.inputmethod default-input-method "my-input-engine"

# 5. 启用引擎
gsettings set org.freedesktop.ibus.settings.inputmethod enabled-engines "['my-input-engine']"

# 6. 查看当前设置
gsettings get org.freedesktop.ibus.settings.inputmethod default-input-method
gsettings get org.freedesktop.ibus.settings.inputmethod enabled-engines
```

## 故障排除

### 问题 1: 引擎无法加载

**症状**：IBus 无法识别引擎

**解决方法**：
```bash
# 检查配置文件
ls /usr/share/ibus/engines/my-input-engine.xml

# 验证 XML 语法
xmllint --noout /usr/share/ibus/engines/my-input-engine.xml

# 检查权限
ls -la /usr/share/ibus/engines/my-input-engine.xml

# 重启 IBus
sudo ibus-daemon --replace
```

### 问题 2: 按键事件未响应

**症状**：按下按键后无反应

**解决方法**：
```bash
# 检查引擎是否启用
gsettings get org.freedesktop.ibus.settings.inputmethod enabled-engines

# 检查焦点
ibus-daemon --debug

# 查看日志
journalctl -f -t ibus
```

### 问题 3: 候选词不显示

**症状**：输入后候选词表不显示

**解决方法**：
```bash
# 检查能力设置
gsettings get org.freedesktop.ibus.engine.my-input-engine client-capabilities

# 启用查找表支持
gsettings set org.freedesktop.ibus.engine.my-input-engine LookupTable "Enabled"

# 重启 IBus
sudo ibus-daemon --replace
```

## 开发指南

### 创建新引擎

```bash
# 查看示例代码
cat src/my-input-engine.c

# 参考引擎描述
cat src/my-input-engine-desc.c

# 查看配置文件
cat src/my-input-engine.xml
```

### 引擎 API

```c
// 创建引擎
IBusEngine *engine = my_input_engine_new("my-input-engine", "/my/path", connection);

// 处理按键
static gboolean
process_key_event (IBusEngine *engine,
                   guint keyval,
                   guint keycode,
                   guint state)
{
    // 处理按键逻辑
    return TRUE;
}

// 更新预编辑文本
static void
update_preedit (IBusEngine *engine)
{
    IBusText *text = ibus_text_new_from_string("预编辑文本");
    ibus_engine_update_preedit_text(engine, text, 0, TRUE);
    g_object_unref(text);
}

// 提交文本
static void
commit_text (IBusEngine *engine)
{
    IBusText *text = ibus_text_new_from_string("提交文本");
    ibus_engine_commit_text(engine, text);
    g_object_unref(text);
}
```

### 引擎描述

```xml
<?xml version="1.0" encoding="UTF-8"?>
<engine>
    <name>my-input-engine</name>
    <description>My Input Engine</description>
    <author>Developer</author>
    <license>LGPL</license>
    <lang>en</lang>
    <lang>zh_CN</lang>
    <capability>Focus</capability>
    <capability>PreeditText</capability>
    <capability>LookupTable</capability>
</engine>
```

## 系统要求

- **操作系统**：Linux (支持 X11 和 Wayland)
- **依赖包**：
  - libibus-1.0-dev
  - glib2.0-dev
  - gcc
  - make
- **桌面环境**：GNOME, KDE, XFCE, 或其他 IBus 支持的桌面

## 版本历史

### v1.0.0 (2026-03-19)

- 初始版本发布
- 实现基本按键处理
- 实现候选词生成
- 支持多语言配置
- 提供完整的安装/卸载/配置脚本

## 许可证

本软件按照 LGPL v2.1 或更高版本许可分发。

## 支持

如有问题，请通过以下方式联系我们：

- **邮件**：support@example.com
- **文档**：查看 docs 目录
- **测试**：运行 tests/test-input-engine.sh

## 致谢

- IBus 开发团队
- 所有贡献者
