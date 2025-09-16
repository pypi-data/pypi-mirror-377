# 腾讯云联网搜索MCP服务器

这是一个基于Model Context Protocol (MCP)的腾讯云联网搜索API服务器，可以让你在各种支持MCP的应用中使用腾讯云的搜索功能。

## 功能特性

- 🚀 基于MCP协议，支持多种MCP客户端
- 🔍 使用腾讯云联网搜索API进行网络搜索
- 📝 格式化的搜索结果展示
- 🛡️ 完善的错误处理和参数验证

## 安装

### 使用uv安装（推荐）

```bash
uv install tencent-cloud-search-mcp
```

### 使用pip安装

```bash
pip install tencent-cloud-search-mcp
```

## 配置

在使用前，需要设置腾讯云API凭据：

```bash
export TENCENTCLOUD_SECRET_ID="your_secret_id"
export TENCENTCLOUD_SECRET_KEY="your_secret_key"
```

## 使用方法

### 作为MCP服务器使用

1. 在支持MCP的应用中配置此服务器
2. 使用工具名称 `tencent_search` 进行搜索

### 命令行运行

```bash
tencent-search-mcp
```

### 作为Python模块运行

```bash
python -m tencent_cloud_search_mcp.server
```

## API参考

### 可用工具

#### tencent_search

使用腾讯云联网搜索API进行搜索

**参数：**
- `query` (string, 必需): 搜索查询关键词
- `limit` (integer, 可选): 返回结果数量限制，默认10

**返回格式化的搜索结果，包含标题、链接和描述。**

## 故障排除

### 常见问题

1. **认证失败**
   - 检查 `TENCENTCLOUD_SECRET_ID` 和 `TENCENTCLOUD_SECRET_KEY` 环境变量是否正确设置
   - 确认API密钥有足够的权限

2. **网络连接问题**
   - 检查网络连接
   - 确认腾讯云API服务可用

3. **依赖安装失败**
   - 确保使用Python 3.10或更高版本

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 更新日志

### 0.1.0

- 初始版本发布
- 支持腾讯云联网搜索API
- 完整的MCP服务器实现