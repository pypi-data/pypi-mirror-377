# Puppy MCP Server

Puppy MCP Server 是一个基于 FastMCP 框架构建的服务器应用程序，用于提供各种工具和服务。

## 功能特性

- 提供 MCP (Multi-Client Protocol) 服务
- 集成 GEO 产品信息查询功能
- 支持多环境配置（测试、预发布、生产环境）
- 可通过环境变量进行配置

## 安装说明

### 环境要求

- Python 3.11 或更高版本

### 安装步骤

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install .
   ```
   或者如果你使用 poetry：
   ```bash
   poetry install
   ```

## 使用方法

### 启动服务

```bash
puppy-mcp-server
```

### 环境配置

可以通过以下环境变量进行配置：

- `ACTIVE_ENV`: 设置运行环境，可选值为 `test`（默认）、`pre`、`prod`
- `BACKSTAGE_AUTH_TOKEN`: 设置后台认证令牌

例如在 Linux/Mac 系统中：
```bash
export ACTIVE_ENV=prod
export BACKSTAGE_AUTH_TOKEN=your_token_here
puppy-mcp-server
```

在 Windows 系统中：
```cmd
set ACTIVE_ENV=prod
set BACKSTAGE_AUTH_TOKEN=your_token_here
puppy-mcp-server
```

## 提供的工具

### hello_world
测试服务是否正常运行的简单工具。

### get_products
获取 GEO 产品列表。
参数：
- `biz_enable`: 商务合同是否可用
- `supplier_enable`: 供应商合同是否可用

## 项目结构

```
puppy-mcp/
├── puppy_mcp_server/
│   └── main.py          # 主程序文件
├── pyproject.toml       # 项目配置文件
└── README.md            # 项目说明文件
```

## 许可证

本项目采用 MIT 许可证。