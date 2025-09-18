# GitLab MCP Server

一个用于 [GitLab](https://gitlab.com/) 集成的 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器。

## 功能特性

- 🚀 基于 FastMCP 构建的高性能 MCP 服务器
- 🔧 支持创建 GitLab 合并请求（Merge Request）
- 🔐 安全的环境变量配置管理
- 🛠 支持多种安装和运行方式

## 环境要求

- Python 3.12+
- 有效的 GitLab 访问权限（GitLab URL 和用户访问令牌）

## 安装

### 方法一：使用 uvx（推荐）

```bash
# 临时运行
uvx gitlab-helper-mcp

# 或永久安装
uv tool install gitlab-helper-mcp
```

### 方法二：使用 pip

```bash
pip install gitlab-helper-mcp
```

### 方法三：开发安装

```bash
git clone <repository-url>
cd gitlab-helper-mcp
uv sync
uv run python main.py
```

## 配置

在运行之前，需要设置以下环境变量：

```bash
export GITLAB_URL=https://gitlab.example.com
export GITLAB_USER_ACCESS_TOKEN=your_gitlab_access_token_here
```

或者创建 `.env` 文件：

```env
GITLAB_URL=https://gitlab.example.com
GITLAB_USER_ACCESS_TOKEN=your_gitlab_access_token_here
```

### 获取 GitLab 访问凭据

1. 登录你的 GitLab 实例
2. 进入 **User Settings** > **Access Tokens**
3. 创建一个新的个人访问令牌，选择以下权限：
   - `api` - 完整的 API 访问权限
   - `read_user` - 读取用户信息
   - `read_repository` - 读取仓库
   - `write_repository` - 写入仓库（用于创建 MR）
4. 复制生成的访问令牌

## 使用方法

### 作为独立服务器运行

```bash
# 使用 uvx
uvx gitlab-helper-mcp

# 或使用已安装的命令
gitlab-helper-mcp

# 或使用 Python 模块
python -m gitlab_helper_mcp

# 或直接运行
uv run python main.py
```

### 在 Claude Desktop 中使用

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "gitlab-helper": {
      "command": "uvx",
      "args": ["gitlab-helper-mcp"],
      "env": {
        "GITLAB_URL": "https://gitlab.example.com",
        "GITLAB_USER_ACCESS_TOKEN": "your_gitlab_access_token_here"
      }
    }
  }
}
```

## 可用工具

### `create_merge_request`

创建 GitLab 合并请求（Merge Request）。

**参数：**
- `project_name` (string): 项目名称，格式为 `group/project`
- `source_branch` (string): 源分支名称
- `target_branch` (string): 目标分支名称
- `title` (string): 合并请求标题
- `description` (string): 合并请求描述

**返回：**
- 合并请求的 Web URL

**示例使用：**
```python
# 创建一个新的合并请求
create_merge_request(
    project_name="mygroup/myproject",
    source_branch="feature/new-feature",
    target_branch="main",
    title="Add new feature",
    description="This MR adds a new feature to improve user experience."
)
```

## 开发

### 环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd gitlab-helper-mcp

# 创建虚拟环境并安装依赖
uv venv
uv sync

# 运行开发服务器
uv run python main.py
```

### 代码质量检查

```bash
# 运行 linter
ruff check

# 格式化代码
ruff format
```

### 构建和发布

```bash
# 构建包
uv build

# 发布到 PyPI（需要配置 PyPI 凭据）
twine upload dist/*
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如有问题，请在 [GitHub Issues](https://github.com/philoveritas/gitlab-helper-mcp/issues) 中提出。