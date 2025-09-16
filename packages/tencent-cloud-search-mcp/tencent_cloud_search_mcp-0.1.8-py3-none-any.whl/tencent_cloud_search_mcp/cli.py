#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""命令行接口模块"""

import argparse
import sys
from .server import main


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="腾讯云联网搜索MCP服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 直接运行MCP服务器
  tencent-search-mcp

  # 通过Python模块运行
  python -m tencent_cloud_search_mcp.server

  # 使用环境变量配置
  export TENCENTCLOUD_SECRET_ID=your_secret_id
  export TENCENTCLOUD_SECRET_KEY=your_secret_key
  tencent-search-mcp
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    return parser


def main_cli():
    """命令行主函数"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        main()
    except KeyboardInterrupt:
        print("\n服务器已停止", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"服务器运行错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main_cli()