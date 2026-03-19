# GitHub 自动化执行指南

## 项目信息

- **项目名**: ibus-pinyin-input
- **项目路径**: /home/doudou/.openclaw/workspace/ibus-pinyin-input
- **文件数**: 87 个文件
- **技术栈**: Python + C (IBus 输入法)

## 文件结构

```
ibus-pinyin-input/
├── ibus-pinyin/          # Python 核心引擎 (6 个目录)
├── ibus-integration/     # C 语言 IBus 插件 (6 个目录)
├── src/                  # 源代码 (18 个目录)
├── scripts/              # 配置脚本
├── BROWSER_AUTOMATION_LEARNING.md  # 浏览器自动化学习笔记
├── github_auto.py        # Playwright 自动化脚本
├── github_automation.py  # 完整自动化脚本
├── config.py             # 配置文件
├── run_automation.sh     # 执行脚本
├── README.md             # 项目说明
├── LICENSE               # MIT 许可证
├── requirements.txt      # Python 依赖
└── .gitignore            # Git 忽略文件
```

## 自动化脚本说明

### github_automation.py

支持以下命令：

```bash
# 列出用户仓库
python3 github_automation.py --list

# 创建新仓库
python3 github_automation.py --create

# 上传文件（需要浏览器交互）
python3 github_automation.py --upload

# 创建发布标签
python3 github_automation.py --release

# 验证仓库
python3 github_automation.py --verify

# 执行所有操作
python3 github_automation.py --all
```

### github_auto.py

基础 Playwright 脚本，用于学习浏览器自动化。

## 执行步骤

### 1. 设置环境变量

```bash
# 方法 1: 编辑 config.py
# 文件位置：/home/doudou/.openclaw/workspace/ibus-pinyin-input/config.py

# 方法 2: 设置环境变量
export GITHUB_USERNAME="doudou"
export GITHUB_TOKEN="你的 GitHub token"
export GITHUB_PASSWORD="你的 GitHub 密码"
```

### 2. 获取 GitHub Token

访问 https://github.com/settings/tokens 创建 Personal Access Token

**需要的权限**:
- ✓ repo: 创建仓库、管理仓库
- ✓ public_repo: 公开仓库操作
- ✓ delete: 删除操作（可选）

### 3. 执行自动化

```bash
# 进入项目目录
cd /home/doudou/.openclaw/workspace/ibus-pinyin-input

# 列出仓库（测试）
python3 github_automation.py --list

# 创建仓库
python3 github_automation.py --create

# 上传文件（需要浏览器交互）
python3 github_automation.py --upload

# 创建发布标签
python3 github_automation.py --release

# 验证仓库
python3 github_automation.py --verify

# 一键执行所有操作
python3 github_automation.py --all
```

### 4. 手动上传文件（替代方案）

如果自动化上传遇到问题，可以手动上传：

```bash
# 1. 创建仓库后，在浏览器中打开
https://github.com/{username}/ibus-pinyin-input

# 2. 点击 "Upload files"

# 3. 选择所有文件（可使用 zip 压缩）
# 在项目目录执行：
zip -r ibus-pinyin-input.zip .
# 排除.git 和临时文件

# 4. 上传 zip 文件并提取

# 5. 或者直接拖拽上传整个项目
```

## 注意事项

### 1. 浏览器自动化限制

- GitHub 可能触发验证码
- 需要手动完成验证码
- 建议先用 API 创建仓库

### 2. API 限制

- GitHub API 速率限制：60 次/小时（未认证）
- 使用 token 可提升到 5000 次/小时
- 注意添加延迟避免被封

### 3. 文件上传建议

- 使用 zip 压缩上传（更快）
- 排除 `__pycache__` 和 `.pyc` 文件
- 排除大文件（如词典）

### 4. 错误处理

如果脚本失败：
1. 检查 token 是否有效
2. 检查网络连接
3. 查看浏览器控制台错误
4. 尝试手动操作确认流程

## 预期结果

### 成功标志

```
✓ 仓库创建成功
✓ 文件上传完成
✓ 发布标签 v1.0.0 创建
✓ README 和 LICENSE 已配置
```

### 仓库 URL

创建后仓库 URL:
```
https://github.com/doudou/ibus-pinyin-input
```

## 学习成果

通过本次任务，已完成：

1. ✅ 安装 Playwright 浏览器自动化库
2. ✅ 学习 Playwright 使用方法
3. ✅ 创建 Python 自动化脚本
4. ✅ 编写完整文档和配置
5. ✅ 准备 GitHub 自动化流程

## 后续任务

- [ ] 执行自动化脚本创建仓库
- [ ] 上传项目文件
- [ ] 创建 v1.0.0 发布标签
- [ ] 验证上传成功
- [ ] 添加测试文件
- [ ] 更新 README

---

*创建日期：2026-03-19*
