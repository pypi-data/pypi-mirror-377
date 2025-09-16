#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MCP服务器主模块"""

import asyncio
import json
import sys
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, Tool, TextContent

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.wsa.v20250508 import wsa_client, models

from .config import Config


class TencentCloudSearchServer:
    """腾讯云搜索MCP服务器"""

    def __init__(self):
        self.server = Server("tencent-cloud-search")
        self.client = None
        self.config = Config()
        self._setup_client()
        self._setup_handlers()

    def _setup_client(self):
        """初始化腾讯云客户端"""
        try:
            self.config.validate()
            secret_id, secret_key = self.config.get_credentials()

            cred = credential.Credential(secret_id, secret_key)
            httpProfile = HttpProfile()
            httpProfile.endpoint = self.config.endpoint

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            self.client = wsa_client.WsaClient(cred, "", clientProfile)

        except Exception as e:
            print(f"警告: 腾讯云客户端初始化失败: {e}", file=sys.stderr)
            print("服务器将继续运行，但搜索功能将无法使用", file=sys.stderr)
            self.client = None

    def _setup_handlers(self):
        """设置MCP服务器处理器"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """列出可用工具"""
            return [
                Tool(
                    name="tencent_search",
                    description="使用腾讯云联网搜索API进行搜索",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询关键词"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量限制 (默认10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """调用工具"""
            if name == "tencent_search":
                return await self._handle_search(arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"未知工具: {name}")],
                    isError=True
                )

    async def _handle_search(self, arguments: Dict[str, Any]) -> CallToolResult:
        """处理搜索请求"""
        try:
            # 检查客户端是否初始化
            if self.client is None:
                return CallToolResult(
                    content=[TextContent(type="text", text="腾讯云客户端未正确初始化，请检查API凭据配置")],
                    isError=True
                )

            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)

            if not query.strip():
                return CallToolResult(
                    content=[TextContent(type="text", text="搜索查询不能为空")],
                    isError=True
                )

            # 创建搜索请求
            req = models.SearchProRequest()
            params = {
                "Query": query,
                "Limit": limit
            }
            req.from_json_string(json.dumps(params))

            # 发送搜索请求
            resp = self.client.SearchPro(req)

            # 解析响应
            if hasattr(resp, 'to_json_string'):
                response_data = json.loads(resp.to_json_string())
            else:
                response_data = {"result": str(resp)}

            # 格式化搜索结果
            formatted_result = self._format_search_results(response_data)

            return CallToolResult(
                content=[TextContent(type="text", text=formatted_result)],
                isError=False
            )

        except TencentCloudSDKException as e:
            error_msg = f"腾讯云API错误: {e}"
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )
        except Exception as e:
            error_msg = f"搜索失败: {e}"
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )

    def _format_search_results(self, response_data: Dict[str, Any]) -> str:
        """格式化搜索结果"""
        try:
            # 尝试从不同的字段获取结果
            pages = response_data.get("Pages", [])
            if pages:
                # Pages是一个JSON字符串列表，需要解析
                results = []
                for page_str in pages:
                    try:
                        page_data = json.loads(page_str)
                        results.append(page_data)
                    except json.JSONDecodeError:
                        continue
            else:
                results = response_data.get("Results", [])

            if not results:
                return "未找到搜索结果"

            formatted_output = f"找到 {len(results)} 个搜索结果:\n\n"

            for i, result in enumerate(results, 1):
                title = result.get("title", result.get("Title", "无标题"))
                url = result.get("url", result.get("Url", ""))
                snippet = result.get("content", result.get("passage", result.get("Snippet", "无描述")))

                formatted_output += f"{i}. **{title}**\n"
                if url:
                    formatted_output += f"   链接: {url}\n"
                formatted_output += f"   描述: {snippet[:200]}...\n\n"

            return formatted_output

        except Exception as e:
            return f"搜索结果解析失败: {e}"

    async def run(self):
        """运行MCP服务器"""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            print(f"❌ MCP服务器运行失败: {e}", file=sys.stderr)
            print("💡 这个工具需要在MCP客户端环境中运行", file=sys.stderr)
            print("ℹ️  请在支持MCP的应用中配置此服务器", file=sys.stderr)
            return False


def main():
    """主函数"""
    print("🔍 腾讯云搜索MCP服务器")
    print("=" * 40)
    print("⚠️  注意：这是一个MCP服务器工具")
    print("💡 它需要在支持MCP协议的应用中使用")
    print("ℹ️  如：Claude Desktop、Continue.dev等")
    print("=" * 40)

    try:
        server = TencentCloudSearchServer()
        result = asyncio.run(server.run())
        if result is False:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()