#!/usr/bin/env python3
"""
配置文件 - 管理API endpoints和其他配置信息
"""

import os


class Config:
    """配置类"""

    def __init__(self):
        # GitLab 配置
        self.gitlab_url = os.getenv("GITLAB_URL", "")
        self.gitlab_user_access_token = os.getenv("GITLAB_USER_ACCESS_TOKEN", "")

    def validate_config(self) -> list:
        """验证配置是否完整"""
        errors = []

        if not self.gitlab_url:
            errors.append("GITLAB_URL 环境变量是必需的")

        if not self.gitlab_user_access_token:
            errors.append("GITLAB_USER_ACCESS_TOKEN 环境变量是必需的")

        return errors

    def ensure_required_config(self):
        """确保必需的配置存在，否则抛出异常"""
        errors = self.validate_config()
        if errors:
            raise ValueError("配置错误：\n" + "\n".join(f"- {error}" for error in errors))


# 创建全局配置实例
config = Config()
