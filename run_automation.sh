#!/bin/bash
# GitHub 自动化执行脚本

echo "=========================================="
echo "GitHub 自动化脚本 - 执行流程"
echo "=========================================="
echo ""

cd /home/doudou/.openclaw/workspace/ibus-pinyin-input

# 1. 检查 Playwright 安装
echo "1. 检查 Playwright 安装..."
python -c "from playwright.sync_api import sync_playwright; print('✓ Playwright 已安装')"

# 2. 检查浏览器
echo ""
echo "2. 检查 Chromium 浏览器..."
playwright --version

# 3. 显示项目文件
echo ""
echo "3. 项目文件统计..."
echo "总文件数:"
find . -type f ! -path "*/.git/*" | wc -l

echo ""
echo "=========================================="
echo "准备执行自动化任务"
echo "=========================================="
echo ""
echo "需要设置环境变量："
echo "  export GITHUB_TOKEN='你的 token'"
echo "  export GITHUB_USERNAME='doudou'"
echo ""
echo "或者编辑 config.py 文件"
echo ""
echo "执行选项："
echo "  python github_automation.py --list      # 列出仓库"
echo "  python github_automation.py --create    # 创建仓库"
echo "  python github_automation.py --upload    # 上传文件"
echo "  python github_automation.py --release   # 创建发布"
echo "  python github_automation.py --all       # 执行所有操作"
echo ""
echo "=========================================="
