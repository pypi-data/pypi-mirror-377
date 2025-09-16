#!/bin/bash

set -e

echo "🚀 开始上传版本0.1.2到TestPyPI..."

# 使用环境变量中的token上传
if [ -n "$TEST_PYPI_TOKEN" ]; then
    echo "📤 使用token上传到TestPyPI..."
    uv run twine upload --repository testpypi --username __token__ --password "$TEST_PYPI_TOKEN" dist/*
    echo "✅ 已发布到TestPyPI: https://test.pypi.org/project/tencent-cloud-search-mcp/"
else
    echo "❌ 请设置TEST_PYPI_TOKEN环境变量"
    echo "💡 或者手动运行: uv run twine upload --repository testpypi dist/*"
    exit 1
fi