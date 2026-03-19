#!/usr/bin/env python3
"""
完整的 Playwright + GitHub API 自动化脚本
用于自动创建仓库、上传代码、创建标签
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
from typing import Optional

# 第三方库
try:
    from playwright.sync_api import sync_playwright, Page, BrowserContext
except ImportError:
    print("请安装 playwright: pip install playwright")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    sys.exit(1)

# 配置
PROJECT_PATH = "/home/doudou/.openclaw/workspace/ibus-pinyin-input"
REPO_NAME = "ibus-pinyin-input"
OWNER = os.getenv("GITHUB_USERNAME", "doudou")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_BASE = "https://api.github.com"


def print_section(title: str):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)


def print_info(msg: str):
    """打印信息"""
    print(f"  [ℹ] {msg}")


def print_success(msg: str):
    """打印成功信息"""
    print(f"  [✓] {msg}")


def print_error(msg: str):
    """打印错误信息"""
    print(f"  [✗] {msg}")
    sys.exit(1)


def get_headers() -> dict:
    """获取 GitHub API 请求头"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Automation-Script"
    }
    
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    return headers


def list_user_repos() -> list:
    """列出用户仓库"""
    print_section("列出用户仓库")
    
    url = f"{GITHUB_API_BASE}/user/repos"
    headers = get_headers()
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
        
        print(f"找到 {len(repos)} 个仓库")
        for repo in repos[:5]:  # 只显示前 5 个
            print(f"  - {repo['name']}")
        
        return repos
    except Exception as e:
        print_error(f"获取仓库列表失败：{e}")


def create_repository() -> Optional[str]:
    """创建新仓库"""
    print_section(f"创建仓库：{REPO_NAME}")
    
    url = f"{GITHUB_API_BASE}/user/repos"
    headers = get_headers()
    
    data = {
        "name": REPO_NAME,
        "description": "ibus-pinyin-input 输入法项目",
        "private": False,
        "gitignore_template": "Python",
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        repo_info = response.json()
        repo_url = f"{repo_info['html_url']}"
        
        print_success(f"仓库创建成功！")
        print_info(f"  URL: {repo_url}")
        print_info(f"  克隆 URL: {repo_info['clone_url']}")
        
        return repo_url
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print_info(f"仓库已存在，跳过创建")
            return None
        print_error(f"创建仓库失败：{e}")
    except Exception as e:
        print_error(f"创建仓库时出错：{e}")


def get_repository_url(repo_name: str) -> str:
    """获取仓库 URL"""
    url = f"{GITHUB_API_BASE}/users/{OWNER}/repos/{repo_name}"
    headers = get_headers()
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['html_url']
    except Exception as e:
        print_error(f"获取仓库 URL 失败：{e}")
    return ""


def upload_file_via_browser(repo_url: str):
    """通过浏览器上传文件（需要手动确认）"""
    print_section("通过浏览器上传文件")
    
    # 启动浏览器
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=os.path.expanduser("~/.config/google-chrome"),
            headless=False
        )
        
        page = context.pages[0]
        page.goto(repo_url)
        
        # 等待页面加载
        page.wait_for_load_state("networkidle")
        
        # 检查登录状态
        if page.locator("text='Sign in'").count() > 0:
            print_info("需要登录，请在浏览器中登录 GitHub")
            # 这里可以添加自动登录逻辑
            print_info("按任意键继续...")
            input()
        
        # 点击上传按钮
        upload_btn = page.locator("text='Upload files'")
        
        if upload_btn.count() > 0:
            print_info("点击上传按钮")
            upload_btn.click()
            
            # 等待上传页面
            page.wait_for_load_state("networkidle")
            
            print_info(f"上传文件到：{repo_url}")
            print_info(f"项目路径：{PROJECT_PATH}")
            print_info("请在浏览器中：")
            print_info("  1. 点击上传按钮")
            print_info("  2. 选择所有文件")
            print_info("  3. 填写提交信息")
            print_info("  4. 点击 Commit changes")
            print_info("按 Ctrl+C 停止脚本")
            
            # 保持浏览器打开
            time.sleep(300)
        else:
            print_info("未找到上传按钮")
        
        context.close()


def create_release(repo_url: str):
    """创建发布标签"""
    print_section("创建 v1.0.0 发布标签")
    
    # 提取仓库名
    repo_parts = repo_url.split("/")
    if len(repo_parts) < 2:
        print_error("无法从 URL 提取仓库信息")
    
    owner = repo_parts[-2]
    repo_name = repo_parts[-1]
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}/releases/new"
    headers = get_headers()
    
    # 检查仓库是否存在
    try:
        repo_url_check = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}"
        response = requests.get(repo_url_check, headers=headers)
        if response.status_code == 404:
            print_info("仓库不存在，无法创建发布")
            return
        response.raise_for_status()
    except Exception as e:
        print_error(f"检查仓库失败：{e}")
    
    data = {
        "tag_name": "v1.0.0",
        "name": "v1.0.0 初始发布",
        "body": "Initial release of ibus-pinyin-input\n\n## Features\n- Basic pinyin input support\n- Dictionary management\n- Configurable settings",
        "target_commitish": "master",
        "draft": False,
        "prerelease": False
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        release = response.json()
        print_success(f"发布创建成功！")
        print_info(f"  URL: {release['html_url']}")
        print_info(f"  Tag: {release['tag_name']}")
        
    except Exception as e:
        print_error(f"创建发布失败：{e}")


def verify_repository(repo_url: str):
    """验证仓库"""
    print_section("验证仓库")
    
    try:
        response = requests.get(repo_url, headers=get_headers())
        response.raise_for_status()
        
        repo_info = response.json()
        print_success("仓库验证通过！")
        print_info(f"  名称：{repo_info['name']}")
        print_info(f"  描述：{repo_info['description']}")
        print_info(f"  私有：{repo_info['private']}")
        print_info(f"  更新：{repo_info['updated_at']}")
        
        # 检查标签
        tags_url = f"{GITHUB_API_BASE}/repos/{repo_info['owner']['login']}/{repo_info['name']}/tags"
        tags_response = requests.get(tags_url, headers=get_headers())
        tags = tags_response.json()
        
        print_info(f"  标签：{len(tags)} 个")
        for tag in tags:
            print_info(f"    - {tag['name']}")
        
    except Exception as e:
        print_error(f"验证失败：{e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GitHub 自动化管理脚本")
    parser.add_argument("--create", action="store_true", help="创建仓库")
    parser.add_argument("--upload", action="store_true", help="上传文件")
    parser.add_argument("--release", action="store_true", help="创建发布")
    parser.add_argument("--list", action="store_true", help="列出仓库")
    parser.add_argument("--verify", action="store_true", help="验证仓库")
    parser.add_argument("--all", action="store_true", help="执行所有操作")
    
    args = parser.parse_args()
    
    if args.all:
        args.create = True
        args.upload = True
        args.release = True
        args.verify = True
    
    print("="*60)
    print("GitHub 自动化脚本 - ibus-pinyin-input")
    print(f"Owner: {OWNER}")
    print(f"Token: {'存在' if GITHUB_TOKEN else '未设置'}")
    print(f"项目路径：{PROJECT_PATH}")
    print("="*60)
    
    # 1. 列出仓库
    if args.list:
        list_user_repos()
    
    # 2. 创建仓库
    if args.create:
        repo_url = create_repository()
        if repo_url:
            # 验证创建
            verify_repository(repo_url)
    
    # 3. 上传文件
    if args.upload:
        if not args.create:
            repo_url = get_repository_url(REPO_NAME)
            if not repo_url:
                print_error("请先创建仓库")
        upload_file_via_browser(repo_url)
    
    # 4. 创建发布
    if args.release:
        if not args.create:
            repo_url = get_repository_url(REPO_NAME)
            if not repo_url:
                print_error("请先创建仓库")
        create_release(repo_url)
    
    # 5. 验证
    if args.verify:
        if not args.create:
            repo_url = get_repository_url(REPO_NAME)
            if not repo_url:
                print_error("请先创建仓库")
        verify_repository(repo_url)


if __name__ == "__main__":
    main()
