# IBus Pinyin - 中文拼音输入法

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)
[![GTK](https://img.shields.io/badge/GTK-3.x-orange.svg)](https://gtk.org)
[![IBus](https://img.shields.io/badge/IBus-1.5-blue.svg)](https://ibus.sourceforge.io)

一款基于 IBus 框架的现代中文拼音输入法，遵循 GNOME 项目规范，支持高性能输入体验。

## 📋 项目简介

IBus Pinyin 是一个开源的中文拼音输入法引擎，采用 Python 3.10+ 和 GTK3 构建，提供流畅的中文输入体验。项目严格遵循 IBus 官方框架和 GNOME 项目规范，支持拼音、混合模式等多种输入方式。

### 核心特性

- ✅ **高性能拼音引擎** - 优化的拼音转换算法
- ✅ **智能候选词** - 上下文感知和频率预测
- ✅ **GTK3 界面** - 现代化候选词窗口
- ✅ **IBus 标准兼容** - 与 GNOME、KDE、Deepin 等桌面环境完美集成
- ✅ **可配置性强** - 支持多种主题、快捷键和输入模式
- ✅ **模块化设计** - 易于扩展和定制

## 🚀 快速开始

### 安装依赖

```bash
# Ubuntu/Debian
sudo apt-get install python3-gi python3-gi-cairo gir1.2-ibus-1.0 gir1.2-gtk-3.0

# Fedora
sudo dnf install python3-gobject gtk3 ibus-devel

# Arch Linux
sudo pacman -S ibus gtk3 python-gobject
```

### 构建项目

```bash
# 克隆仓库
git clone https://github.com/youruser/ibus-pinyin.git
cd ibus-pinyin

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt

# 编译 IBus 引擎
make
```

### 配置 IBus

```bash
# 启用输入法
ibus-daemon -drx

# 设置输入法（GNOME 设置 -> 区域与语言 -> 输入源）
# 或命令行：
ibus engine add ibus-pinyin
ibus engine set ibus-pinyin
```

## 📖 使用指南

### 基础用法

1. 切换输入法：`Super + Space` 或 `Alt + Shift`
2. 输入拼音：键入拼音（如 "nihao"）
3. 选择候选词：数字键 `1-9` 或上下箭头
4. 直接输入：按 `Space` 键确认

### 高级功能

- **智能学习** - 自动学习常用词汇
- **云同步** - 同步个人词库（需配置）
- **主题切换** - 支持 GTK3 主题
- **快捷键自定义** - 在配置文件中设置

## 🏗️ 项目结构

```
ibus-pinyin/
├── src/
│   ├── engine/           # 核心引擎模块
│   │   ├── engine.py     # IBus 引擎主类
│   │   ├── candidate.py  # 候选词管理
│   │   ├── input_method.py  # 输入方法接口
│   │   └── context.py    # 上下文处理
│   ├── plugin/           # 插件系统
│   │   ├── dictionary.py # 字典插件
│   │   ├── cloud.py      # 云端同步
│   │   └── learning.py   # 学习插件
│   ├── util/             # 工具模块
│   │   ├── pinyin.py     # 拼音转换
│   │   ├── freq.py       # 频率统计
│   │   └── theme.py      # 主题处理
│   └── config/           # 配置管理
│       ├── settings.py   # 配置加载
│       └── schema.py     # 配置模式
├── docs/                 # 文档
│   ├── ARCHITECTURE.md  # 架构设计
│   ├── API.md           # API 接口
│   └── CONFIG.md        # 配置说明
├── tests/                # 测试套件
│   ├── unit/            # 单元测试
│   └── integration/     # 集成测试
├── scripts/              # 脚本工具
├── requirements.txt      # Python 依赖
├── Makefile              # 构建脚本
└── README.md             # 项目说明
```

## 📦 安装方式

### 从源码安装

```bash
pip install -e .
```

### 系统包（开发中）

计划发布到官方软件仓库。

## 🤝 贡献

欢迎贡献代码！请先阅读 [贡献指南](CONTRIBUTING.md)。

### 开发环境

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest tests/

# 代码风格
flake8 src/
black src/
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 🌐 社区

- [GitHub Issues](https://github.com/youruser/ibus-pinyin/issues)
- [Discussions](https://github.com/youruser/ibus-pinyin/discussions)
- [中文文档](docs/)

## 🙏 致谢

- [IBus 项目](https://ibus.sourceforge.io)
- [Fcitx 项目](https://github.com/fcitx/fcitx5)
- [GNOME 团队](https://wiki.gnome.org/Projects/IBus)

---

**开发状态**: Alpha - 欢迎测试和反馈！
