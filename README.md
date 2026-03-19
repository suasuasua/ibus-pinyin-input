# ibus-pinyin-input

基于 IBus 的拼音输入法项目，包含 Python 核心引擎、C 语言 IBus 插件和混合引擎。

## 项目结构

```
ibus-pinyin-input/
├── ibus-pinyin/           # Python 核心引擎
│   ├── src/
│   │   ├── data/          # 词库数据
│   │   ├── util/          # 工具模块
│   │   └── ...
│   └── README.md
├── ibus-integration/      # C 语言 IBus 插件
│   ├── src/
│   │   ├── my-input-engine.c
│   │   └── ...
│   ├── docs/              # IBus API 文档
│   ├── scripts/           # 安装/卸载脚本
│   └── README.md
├── src/                   # 源代码
│   ├── config/            # 配置管理
│   ├── engine/            # 引擎核心
│   ├── ui/                # 用户界面
│   └── data/              # 数据管理
├── scripts/               # 配置脚本
├── docs/                  # 文档
├── tests/                 # 测试文件
├── requirements.txt       # Python 依赖
├── README.md              # 项目说明
└── LICENSE                # 许可证
```

## 功能特性

- **Python 核心引擎**：基于 Python 的拼音输入法核心，支持智能词库管理
- **C 语言 IBus 插件**：与 IBus 框架深度集成的 C 语言插件
- **混合引擎**：结合 Python 和 C 的优势，提供高性能输入体验
- **智能词库**：支持自定义词库和动态词库更新
- **配置管理**：灵活的配置系统，支持导出/导入配置

## 安装说明

### 系统要求

- Ubuntu 18.04+ / Debian 10+
- IBus 框架 >= 1.5
- Python 3.8+
- GCC >= 7.0

### 安装步骤

```bash
# 1. 安装依赖
sudo apt-get update
sudo apt-get install -y ibus libibus-1.0-dev python3-dev gcc

# 2. 克隆仓库
git clone https://github.com/doudou/ibus-pinyin-input.git
cd ibus-pinyin-input

# 3. 安装 Python 依赖
pip3 install -r requirements.txt

# 4. 编译 IBus 插件
cd ibus-integration
chmod +x scripts/configure.sh
./scripts/configure.sh

# 5. 安装
chmod +x scripts/install.sh
./scripts/install.sh
```

### 配置

```bash
# 配置 IBus 使用本输入法
ibus-config --show-module | grep -i pinyin
# 选择 ibus-pinyin-input 并启动
ibus-daemon -rf
```

## 测试

```bash
# 运行测试套件
cd ibus-integration
./scripts/test.sh

# 运行 Python 测试
cd ibus-pinyin
python3 -m pytest tests/

# 运行集成测试
python3 ibus_test_complete.py
```

## 开发

### Python 核心引擎

```bash
cd ibus-pinyin
python3 -m pytest tests/
```

### C 语言插件

```bash
cd ibus-integration
make clean
make
sudo make install
```

## 文档

- [架构文档](docs/ARCHITECTURE.md)
- [IBus API 参考](ibus-integration/docs/IBUS-API-REFERENCE.txt)
- [用户手册](ibus-integration/docs/README-USER.md)

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- GitHub: https://github.com/doudou/ibus-pinyin-input
- Email: 475317506@qq.com

---

**版本**: v1.0.0  
**作者**: doudou  
**创建日期**: 2026-03-19