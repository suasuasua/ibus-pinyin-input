# 浏览器自动化学习笔记

## 学习日期
2026-03-19

## 学习目标
- 学习 Playwright 浏览器自动化技术
- 创建 Python 脚本自动控制浏览器
- 实现 GitHub 仓库管理自动化

## 技术栈
- **工具**: Playwright (推荐) / Selenium
- **语言**: Python 3.10+
- **浏览器**: Chromium

## 安装步骤

### 1. 安装 Playwright
```bash
pip install playwright
playwright install chromium
```

### 2. 验证安装
```bash
python -c "from playwright.sync_api import sync_playwright; print('✓ Playwright 安装成功')"
```

## 核心概念

### Browser Context
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 启动浏览器上下文
    context = p.chromium.launch_persistent_context(
        user_data_dir=os.path.expanduser("~/.config/google-chrome"),
        headless=False  # 非无头模式
    )
    
    page = context.pages[0]
    
    # 关闭浏览器
    context.close()
```

### 导航页面
```python
page.goto("https://github.com")
page.wait_for_load_state("networkidle")
```

### 表单操作
```python
# 填充输入框
page.fill("input[name='login']", "username")
page.press("input[name='login']", "Enter")

# 点击按钮
page.click("button:has-text('Submit')")

# 选择下拉框
page.select_option("select[name='visibility']", "private")
```

### 等待操作
```python
# 等待元素出现
page.wait_for_selector("button#submit-btn")

# 等待网络空闲
page.wait_for_load_state("networkidle")

# 等待指定时间
page.wait_for_timeout(3000)
```

## GitHub 自动化应用场景

### 1. 检查登录状态
```python
if page.locator("text='Sign in'").count() > 0:
    print("未登录，需要登录")
else:
    print("已登录")
```

### 2. 自动登录
```python
page.goto("https://github.com")
page.wait_for_selector("input[name='login']")
page.fill("input[name='login']", username)
page.press("input[name='login']", "Enter")

page.wait_for_selector("input[name='password']")
page.fill("input[name='password']", password)
page.press("input[name='password']", "Enter")

page.wait_for_load_state("networkidle")
```

### 3. 创建仓库
```python
page.goto("https://github.com/new")
page.fill("input[name='name']", repo_name)
page.fill("input[name='description']", description)
page.select_option("select[name='visibility']", "private")
page.click("button:has-text('Create repository')")
```

### 4. 上传文件
```python
# 点击上传按钮
upload_btn = page.locator("text='Upload files'")
if upload_btn.count() > 0:
    upload_btn.click()
    page.wait_for_load_state("networkidle")
```

### 5. 创建发布标签
```python
page.goto("https://github.com/{username}/{repo}/releases/new")
page.fill("input[name='tag_name']", "v1.0.0")
page.fill("input[name='title']", "v1.0.0 发布")
page.fill("textarea[name='body']", "Release notes")
page.click("button:has-text('Publish release')")
```

## GitHub API 自动化

### 使用 Python requests 库
```python
import requests

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 创建仓库
response = requests.post(
    "https://api.github.com/user/repos",
    json={"name": "repo-name", "description": "Description"}
)

# 获取仓库列表
response = requests.get("https://api.github.com/user/repos")

# 创建发布
response = requests.post(
    "https://api.github.com/repos/{owner}/{repo}/releases/new",
    json={
        "tag_name": "v1.0.0",
        "name": "v1.0.0",
        "target_commitish": "master"
    }
)
```

## 项目实践

### 自动化脚本创建
- ✅ `github_auto.py` - 基础 Playwright 脚本
- ✅ `github_automation.py` - 完整自动化脚本（支持 CLI）

### 支持的命令
```bash
# 列出仓库
python github_automation.py --list

# 创建仓库
python github_automation.py --create

# 上传文件
python github_automation.py --upload

# 创建发布
python github_automation.py --release

# 验证仓库
python github_automation.py --verify

# 执行所有操作
python github_automation.py --all
```

## 注意事项

### 1. 浏览器上下文
- 使用 `persistent_context` 可以保持登录状态
- 注意清理临时配置文件
- 避免敏感信息泄露

### 2. 验证码处理
- GitHub 可能触发验证码
- Playwright 无法自动处理验证码
- 需要手动完成或通过 API 绕过

### 3. 速率限制
- GitHub API 有速率限制（60 次/小时）
- 使用 token 可以绕过部分限制
- 注意添加延迟避免被封

### 4. 错误处理
```python
try:
    # 操作代码
except Exception as e:
    print(f"错误：{e}")
    # 重试逻辑
```

## 学习收获

1. **Playwright 优势**
   - API 简洁易用
   - 支持多浏览器
   - 自动等待机制
   - 无头模式支持

2. **Selenium 对比**
   - Selenium 更成熟，生态更丰富
   - Playwright 性能更好，API 更现代
   - 推荐新项目使用 Playwright

3. **最佳实践**
   - 使用 API 代替浏览器自动化（更可靠）
   - 添加完善的错误处理
   - 记录日志便于调试
   - 使用环境变量管理敏感信息

## 下一步

- [ ] 学习 Playwright 高级功能（截图、录制、轨迹）
- [ ] 实现浏览器自动登录 GitHub（处理验证码）
- [ ] 学习 Selenium 作为备选方案
- [ ] 实现文件上传自动化（通过 API）
- [ ] 添加测试用例

## 参考资料

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright Python 教程](https://playwright.dev/python/docs/intro)
- [GitHub API 文档](https://docs.github.com/en/rest)
- [Requests 文档](https://docs.python-requests.org/)

---
*学习记录完成*
