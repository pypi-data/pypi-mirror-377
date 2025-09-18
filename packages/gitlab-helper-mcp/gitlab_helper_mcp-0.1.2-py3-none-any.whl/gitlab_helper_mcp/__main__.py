#!/usr/bin/env python3
"""
GitLab MCP Server 包入口点
允许通过 python -m gitlab_helper_mcp 运行
"""

from .server import main

if __name__ == "__main__":
    main()
