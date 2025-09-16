#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试MCP服务器初始化"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from tencent_cloud_search_mcp.server import TencentCloudSearchServer

    print("开始测试MCP服务器初始化...")

    # 测试没有环境变量的情况
    print("\n1. 测试没有环境变量的情况:")
    if 'TENCENTCLOUD_SECRET_ID' in os.environ:
        del os.environ['TENCENTCLOUD_SECRET_ID']
    if 'TENCENTCLOUD_SECRET_KEY' in os.environ:
        del os.environ['TENCENTCLOUD_SECRET_KEY']

    try:
        server = TencentCloudSearchServer()
        print("✅ 服务器初始化成功")
    except Exception as e:
        print("❌ 服务器初始化失败:", e)
        import traceback
        traceback.print_exc()

    # 测试有环境变量的情况
    print("\n2. 测试有环境变量的情况:")
    os.environ['TENCENTCLOUD_SECRET_ID'] = 'test_id'
    os.environ['TENCENTCLOUD_SECRET_KEY'] = 'test_key'

    try:
        server = TencentCloudSearchServer()
        print("✅ 服务器初始化成功")
    except Exception as e:
        print("❌ 服务器初始化失败:", e)
        import traceback
        traceback.print_exc()

except Exception as e:
    print("❌ 导入失败:", e)
    import traceback
    traceback.print_exc()