#!/bin/bash
# IBus 候选词面板启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "IBus 候选词面板"
echo "=========================================="
echo ""
echo "项目目录：$PROJECT_DIR"
echo ""
echo "请选择操作："
echo "1. 运行候选词面板"
echo "2. 运行单元测试"
echo "3. 查看帮助"
echo ""
echo "输入选项 [1-3]: "
read -r choice

case $choice in
    1)
        echo "启动候选词面板..."
        cd "$PROJECT_DIR"
        python3 -m src.ui.main
        ;;
    2)
        echo "运行单元测试..."
        cd "$PROJECT_DIR"
        python3 -m tests.test_ui
        ;;
    3)
        echo "帮助信息："
        echo "=========================================="
        echo "IBus 候选词面板启动脚本"
        echo ""
        echo "使用方式："
        echo "  ./run.sh 1  - 运行候选词面板"
        echo "  ./run.sh 2  - 运行单元测试"
        echo "  ./run.sh 3  - 查看帮助"
        echo ""
        echo "快捷键说明："
        echo "  Tab/Enter - 选择当前候选词"
        echo "  数字键 1-9 - 选择候选词"
        echo "  ↑/↓ 或方向键 - 移动光标"
        echo "  PageUp/PageDown - 滚动列表"
        echo "  w - 切换窗口模式"
        echo "  Escape/q - 最小化窗口"
        echo "  r - 刷新候选词"
        echo "=========================================="
        ;;
    *)
        echo "无效选项，请输入 1-3"
        exit 1
        ;;
esac
