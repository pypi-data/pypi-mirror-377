#!/bin/bash

set -e

echo "🚀 开始发布腾讯云搜索MCP服务器..."

# 检查版本
echo "📋 检查项目信息..."
python3 -c "
import sys
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print('警告: 无法解析pyproject.toml')
        sys.exit(0)

with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    project = data['project']
    print('项目名称:', project['name'])
    print('版本:', project['version'])
    print('作者:', project['authors'][0]['name'])
"

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf build/ dist/ *.egg-info/

# 构建包
echo "📦 构建包..."
uv run python -m build

# 检查包
echo "🔍 检查包..."
uv run twine check dist/*

# 选择发布目标
echo ""
echo "请选择发布目标:"
echo "1) TestPyPI (测试)"
echo "2) PyPI (正式)"
echo "3) 只构建不上传"
read -p "请输入选择 (1/2/3): " choice

case $choice in
    1)
        echo "📤 上传到TestPyPI..."
        uv run twine upload --repository testpypi dist/*
        echo "✅ 已发布到TestPyPI: https://test.pypi.org/project/tencent-cloud-search-mcp/"
        ;;
    2)
        echo "⚠️  确认要发布到正式PyPI吗？这将使包对所有人可见。"
        read -p "确认继续? (y/N): " confirm
        if [[ $confirm == [yY] ]]; then
            echo "📤 上传到正式PyPI..."
            uv run twine upload dist/*
            echo "✅ 已发布到PyPI: https://pypi.org/project/tencent-cloud-search-mcp/"
        else
            echo "❌ 取消发布"
        fi
        ;;
    3)
        echo "✅ 构建完成，包文件位于 dist/ 目录"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo "🎉 发布完成！"