# PyPI打包和上传指南

## 准备工作

### 1. 检查项目结构

确保你的项目包含以下文件：
```
tencent_api_search/
├── src/tencent_cloud_search_mcp/
├── pyproject.toml
├── MANIFEST.in
├── README.md
├── LICENSE
└── uv.lock
```

### 2. 安装构建工具

```bash
# 激活虚拟环境
source .venv/bin/activate

# 确保构建工具已安装
uv pip install build twine
```

### 3. 检查项目信息

编辑 `pyproject.toml` 中的项目信息：

```toml
[project]
name = "tencent-cloud-search-mcp"
version = "0.1.0"
description = "腾讯云联网搜索API的MCP服务器"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.10"
```

**重要：** 请将作者信息替换为你的真实信息！

## 打包流程

### 方法1: 使用uv (推荐)

```bash
# 构建分发包
uv build

# 查看生成的文件
ls -la dist/
```

### 方法2: 使用python -m build

```bash
# 构建分发包
python -m build

# 查看生成的文件
ls -la dist/
```

### 方法3: 手动构建

```bash
# 清理旧的构建文件
rm -rf build/ dist/ *.egg-info/

# 构建源码分发包
python setup.py sdist

# 构建wheel包
python setup.py bdist_wheel

# 查看生成的文件
ls -la dist/
```

## 检查包文件

构建完成后，`dist/` 目录应该包含：

```
dist/
├── tencent_cloud_search_mcp-0.1.0-py3-none-any.whl  # wheel包
└── tencent_cloud_search_mcp-0.1.0.tar.gz           # 源码包
```

### 检查包完整性

```bash
# 检查包文件
twine check dist/*
```

## 上传到PyPI

### 1. 注册PyPI账号

如果没有账号，请先注册：
- **PyPI官网**: https://pypi.org/
- **TestPyPI官网**: https://test.pypi.org/

### 2. 配置认证信息

创建 `.pypirc` 文件（推荐）：

```bash
# 创建配置文件
touch ~/.pypirc
```

在 `~/.pypirc` 中添加：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = your-username
password = your-password

[pypi]
repository = https://upload.pypi.org/legacy/
username = your-username
password = your-password
```

### 3. 上传到TestPyPI (测试)

```bash
# 上传到测试PyPI
twine upload --repository testpypi dist/*
```

### 4. 验证测试包

1. 访问 https://test.pypi.org/project/tencent-cloud-search-mcp/
2. 尝试安装测试包：
```bash
pip install --index-url https://test.pypi.org/simple/ tencent-cloud-search-mcp
```

### 5. 上传到正式PyPI

```bash
# 上传到正式PyPI
twine upload dist/*
```

## 使用API Token上传 (推荐)

更安全的方式是使用API Token：

### 1. 生成API Token

1. 登录 PyPI 账号
2. 进入 Account settings
3. 在 "API tokens" 部分创建新token
4. 复制token值

### 2. 使用Token上传

```bash
# 上传到TestPyPI
twine upload --repository testpypi --username __token__ --password your-test-token dist/*

# 上传到正式PyPI
twine upload --username __token__ --password your-prod-token dist/*
```

## 自动化脚本

创建一个发布脚本 `publish.sh`：

```bash
#!/bin/bash

set -e

echo "🚀 开始发布腾讯云搜索MCP服务器..."

# 检查版本
echo "📋 检查项目信息..."
python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    print(f'项目名称: {data[\"project\"][\"name\"]}')
    print(f'版本: {data[\"project\"][\"version\"]}'
    print(f'作者: {data[\"project\"][\"authors\"][0][\"name\"]}')
"

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf build/ dist/ *.egg-info/

# 构建包
echo "📦 构建包..."
python -m build

# 检查包
echo "🔍 检查包..."
twine check dist/*

# 选择发布目标
echo "请选择发布目标:"
echo "1) TestPyPI (测试)"
echo "2) PyPI (正式)"
read -p "请输入选择 (1/2): " choice

case $choice in
    1)
        echo "📤 上传到TestPyPI..."
        twine upload --repository testpypi dist/*
        echo "✅ 已发布到TestPyPI: https://test.pypi.org/project/tencent-cloud-search-mcp/"
        ;;
    2)
        echo "📤 上传到正式PyPI..."
        twine upload dist/*
        echo "✅ 已发布到PyPI: https://pypi.org/project/tencent-cloud-search-mcp/"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo "🎉 发布完成！"
```

给脚本添加执行权限：

```bash
chmod +x publish.sh
```

## 常见问题

### 1. 版本冲突

如果上传时提示版本已存在，请在 `pyproject.toml` 中增加版本号：

```toml
version = "0.1.1"
```

### 2. 文件缺失

如果提示文件缺失，检查 `MANIFEST.in` 文件是否包含所有必要文件：

```ini
include README.md
include LICENSE
include pyproject.toml
recursive-include src/tencent_cloud_search_mcp *.py
```

### 3. 认证失败

如果认证失败，检查：
- 用户名和密码是否正确
- 是否使用了正确的token
- 网络连接是否正常

### 4. 包名已存在

如果包名已被占用，需要在 `pyproject.toml` 中修改包名：

```toml
name = "your-unique-package-name"
```

## 发布后验证

### 1. 验证包信息

访问PyPI项目页面确认信息正确：
- TestPyPI: https://test.pypi.org/project/tencent-cloud-search-mcp/
- PyPI: https://pypi.org/project/tencent-cloud-search-mcp/

### 2. 测试安装

```bash
# 创建新的虚拟环境测试
python -m venv test_env
source test_env/bin/activate

# 安装包
pip install tencent-cloud-search-mcp

# 测试导入
python -c "from tencent_cloud_search_mcp.server import TencentCloudSearchServer; print('✅ 导入成功')"
```

### 3. 功能测试

```bash
# 设置环境变量
export TENCENTCLOUD_SECRET_ID="your_secret_id"
export TENCENTCLOUD_SECRET_KEY="your_secret_key"

# 测试搜索功能
python -c "
from tencent_cloud_search_mcp.server import TencentCloudSearchServer
import asyncio

async def test():
    server = TencentCloudSearchServer()
    result = await server._handle_search({'query': 'Python', 'limit': 1})
    print(result.content[0].text)

asyncio.run(test())
"
```

## 更新版本

如果要更新版本：

1. 修改 `pyproject.toml` 中的版本号
2. 重新构建和上传
3. 更新 `CHANGELOG.md` (如果有)

```bash
# 更新版本号
sed -i '' 's/version = "0.1.0"/version = "0.1.1"/' pyproject.toml

# 重新构建和上传
./publish.sh
```

现在你可以按照这个指南来打包和上传你的腾讯云搜索MCP服务器了！