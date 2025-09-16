#!/bin/bash

set -e

echo "🚀 开始上传版本0.1.2到正式PyPI..."

# 使用环境变量中的token上传
if [ -n "$PYPI_TOKEN" ]; then
    echo "📤 使用token上传到正式PyPI..."
    uv run twine upload --username __token__ --password "$PYPI_TOKEN" dist/*
    echo "✅ 已发布到PyPI: https://pypi.org/project/tencent-cloud-search-mcp/"
else
    echo "❌ 请设置PYPI_TOKEN环境变量"
    echo "💡 或者手动运行: uv run twine upload dist/*"
    exit 1
fi