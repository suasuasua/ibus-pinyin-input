#!/usr/bin/env python3
"""
Playwright 浏览器自动化脚本 - GitHub 仓库管理
用于自动登录 GitHub、创建仓库、上传代码、创建标签
"""

import os
import sys
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, BrowserContext

# 配置
GITHUB_URL = "https://github.com"
USERNAME = os.getenv("GITHUB_USERNAME", "doudou")
TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = "ibus-pinyin-input"

# 项目文件路径
PROJECT_PATH = "/home/doudou/.openclaw/workspace/ibus-pinyin-input"


def print_step(step):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤：{step}")
    print('='*60)


def check_github_login(page: Page):
    """检查是否已登录 GitHub"""
    print_step("检查 GitHub 登录状态")
    
    # 导航到 GitHub
    page.goto(GITHUB_URL)
    
    # 等待页面加载
    page.wait_for_load_state("networkidle")
    
    # 检查是否有登录提示
    if page.locator("text='Sign in'").count() > 0:
        print("未检测到登录状态，需要登录...")
        return False
    
    # 检查用户名
    user_name = page.locator("text='@'").first.inner_text()
    print(f"当前用户：{user_name}")
    
    if "doudou" in user_name.lower():
        print("✓ 已登录 GitHub")
        return True
    else:
        print("⚠ 登录状态不确定，建议重新登录")
        return False


def auto_login(context: BrowserContext):
    """自动登录 GitHub"""
    print_step("登录 GitHub")
    
    page = context.new_page()
    page.goto(GITHUB_URL)
    
    # 等待登录页面加载
    page.wait_for_selector("input[name='login']")
    
    # 输入用户名
    page.fill("input[name='login']", USERNAME)
    page.press("input[name='login']", "Enter")
    
    # 等待密码输入
    page.wait_for_selector("input[name='password']")
    
    print("请输入 GitHub 密码，然后按 Enter 键...")
    page.fill("input[name='password']", os.getenv("GITHUB_PASSWORD", ""))
    page.press("input[name='password']", "Enter")
    
    # 等待登录完成
    page.wait_for_load_state("networkidle")
    
    # 验证登录
    if check_github_login(page):
        return page
    else:
        print("登录失败，请检查凭据")
        return None


def create_repository(page: Page):
    """创建新仓库"""
    print_step("创建新仓库")
    
    # 导航到创建仓库页面
    page.goto("https://github.com/new")
    
    # 填写仓库信息
    print("填写仓库信息...")
    
    page.fill("input[name='name']", REPO_NAME)
    page.fill("input[name='description']", "ibus-pinyin-input 输入法项目")
    
    # 选择私有仓库
    page.select_option("select[name='visibility']", "private")
    
    # 点击创建按钮
    page.click("button:has-text('Create repository')")
    
    # 等待页面加载
    page.wait_for_load_state("networkidle")
    
    print(f"✓ 仓库创建成功：https://github.com/{USERNAME}/{REPO_NAME}")
    
    # 返回仓库首页
    page.goto(f"https://github.com/{USERNAME}/{REPO_NAME}")
    return page


def upload_files_via_web(page: Page):
    """通过网页上传文件（需要手动确认）"""
    print_step("上传文件到仓库")
    
    # 在网页上点击上传按钮
    upload_button = page.locator("text='Upload files'")
    
    if upload_button.count() > 0:
        print("找到上传按钮，但网页上传需要手动确认...")
        print("请在浏览器中点击上传按钮，选择以下文件：")
        print(f"路径：{PROJECT_PATH}")
        print("然后按 Ctrl+C 停止脚本")
    else:
        print("未找到上传按钮")


def create_release(page: Page):
    """创建发布标签"""
    print_step("创建 v1.0.0 发布标签")
    
    # 导航到发布页面
    page.goto(f"https://github.com/{USERNAME}/{REPO_NAME}/releases/new")
    
    # 填写发布信息
    page.fill("input[name='tag_name']", "v1.0.0")
    page.fill("input[name='title']", "v1.0.0 初始发布")
    page.fill("textarea[name='body']", "Initial release of ibus-pinyin-input")
    
    # 选择目标分支
    page.select_option("select[name='target']", "master")
    
    # 点击创建按钮
    page.click("button:has-text('Publish release')")
    
    # 等待页面加载
    page.wait_for_load_state("networkidle")
    
    print(f"✓ 发布创建成功：https://github.com/{USERNAME}/{REPO_NAME}/releases/tag/v1.0.0")


def main():
    """主函数"""
    print("="*60)
    print("Playwright GitHub 自动化脚本")
    print(f"项目路径：{PROJECT_PATH}")
    print(f"仓库名称：{REPO_NAME}")
    print("="*60)
    
    # 检查项目文件
    if not os.path.exists(PROJECT_PATH):
        print(f"错误：项目路径不存在：{PROJECT_PATH}")
        return
    
    files = os.listdir(PROJECT_PATH)
    print(f"项目文件：{len(files)} 个")
    
    # 启动浏览器
    print_step("启动浏览器")
    
    with sync_playwright() as p:
        # 启动浏览器
        context = p.chromium.launch_persistent_context(
            user_data_dir=os.path.expanduser("~/.config/google-chrome"),
            headless=False,  # 非无头模式，方便查看
        )
        
        page = context.pages[0]
        
        # 检查登录状态
        if not check_github_login(page):
            # 需要登录
            page = auto_login(context)
            if not page:
                print("登录失败，终止脚本")
                context.close()
                return
        
        # 创建仓库
        page = create_repository(page)
        
        # 上传文件（需要手动确认）
        upload_files_via_web(page)
        
        # 创建发布
        create_release(page)
        
        # 保持浏览器打开
        print("\n✓ 所有步骤完成！")
        print("请在浏览器中确认文件上传成功")
        print("按 Ctrl+C 停止脚本")
        
        context.close()


if __name__ == "__main__":
    main()
