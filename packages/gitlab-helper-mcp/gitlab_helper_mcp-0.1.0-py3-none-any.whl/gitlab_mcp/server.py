from typing import Literal

import gitlab
from gitlab.v4.objects.merge_requests import ProjectMergeRequest
from mcp.server.fastmcp import FastMCP

from gitlab_mcp.config import config
from gitlab_mcp.models import MergeRequest, MergeRequestChange

# Create an MCP server
mcp = FastMCP("gitlab")


def get_gitlab_instance():
    return gitlab.Gitlab(config.gitlab_url, private_token=config.gitlab_user_access_token)


def _get_merge_request(project_id_or_path: int | str, merge_request_id: int | str) -> MergeRequest:
    gl = get_gitlab_instance()
    project = gl.projects.get(project_id_or_path)
    merge_request = project.mergerequests.get(merge_request_id)
    changes = merge_request.changes()
    mr_obj = MergeRequest(**merge_request.__dict__["_attrs"])
    mr_obj.changes = [MergeRequestChange(**change) for change in changes["changes"]]
    return mr_obj


def _get_merge_request_list(
    project_id_or_path: int | str,
    state: Literal["opened", "closed", "merged", "all"],
    page: int = 1,
    per_page: int = 5,
) -> list[MergeRequest]:
    gl = get_gitlab_instance()
    project = gl.projects.get(project_id_or_path)
    merge_requests: list[ProjectMergeRequest] = project.mergerequests.list(
        state=state, page=page, per_page=per_page
    )
    mr_obj_list = []
    for mr in merge_requests:
        mr_obj = MergeRequest(**mr.__dict__["_attrs"])
        mr_obj_list.append(mr_obj)
    return mr_obj_list


@mcp.tool()
def create_merge_request(
    project_id_or_path: int | str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str,
) -> str:
    """
    创建合并请求

    Args:
        project_id_or_path: 项目ID或全路径（group/project）
        source_branch: 源分支
        target_branch: 目标分支
        title: 合并请求标题
        description: 合并请求描述

    Returns:
        str: 合并请求的 URL
    """
    gl = get_gitlab_instance()
    project = gl.projects.get(project_id_or_path)

    # 3. 创建合并请求
    mr = project.mergerequests.create(
        {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
            # 'labels': ['bug', 'urgent']  # 可选
        }
    )
    return mr.web_url


@mcp.tool()
def get_merge_request_list(
    project_id_or_path: int | str,
    state: Literal["opened", "closed", "merged", "all"],
    page: int = 1,
    per_page: int = 5,
) -> list[str]:
    """
    获取项目的合并请求列表

    Args:
        project_id_or_path: 项目ID或全路径（group/project）
        state: 合并请求状态，可选值：opened（打开）、closed（关闭）、merged（已合并）、all（全部）
        page: 页码，默认为1
        per_page: 每页数量，默认为5

    Returns:
        list[dict]: 合并请求列表，每个元素包含以下字段：
            - id (int): 全局唯一ID
            - iid (int): 项目内唯一ID
            - project_id (int): 项目ID
            - title (str): 合并请求标题
            - description (str): 合并请求描述
            - source_branch (str): 源分支
            - target_branch (str): 目标分支
            - merge_status (str): 合并状态
            - state (str): 请求状态
            - web_url (str): Web访问地址
            - work_in_progress (bool): 是否为草稿状态
            - changes (None): 此接口不包含变更信息
    """
    merge_request_list = _get_merge_request_list(project_id_or_path, state, page, per_page)
    return [mr.model_dump() for mr in merge_request_list]


@mcp.tool()
def get_merge_request(project_id_or_path: int | str, merge_request_id: int | str) -> str:
    """
    获取指定合并请求的详细信息，包括代码变更

    Args:
        project_id_or_path: 项目ID或全路径（group/project）
        merge_request_id: 合并请求ID（可以是全局ID或项目内IID）

    Returns:
        dict: 合并请求详细信息，包含以下字段：
            - id (int): 全局唯一ID
            - iid (int): 项目内唯一ID
            - project_id (int): 项目ID
            - title (str): 合并请求标题
            - description (str): 合并请求描述
            - source_branch (str): 源分支
            - target_branch (str): 目标分支
            - merge_status (str): 合并状态
            - state (str): 请求状态
            - web_url (str): Web访问地址
            - work_in_progress (bool): 是否为草稿状态
            - changes (list[dict]): 代码变更列表，每个变更包含：
                - a_mode (str): 源文件模式
                - b_mode (str): 目标文件模式
                - deleted_file (bool): 是否为删除文件
                - diff (str): 差异内容
                - old_path (str): 原文件路径
                - new_path (str): 新文件路径
                - new_file (bool): 是否为新建文件
                - renamed_file (bool): 是否为重命名文件
    """
    merge_request = _get_merge_request(project_id_or_path, merge_request_id)
    return merge_request.model_dump()


def main():
    print("Hello from gitlab-helper-mcp!")

    # 验证必需的环境变量
    try:
        config.ensure_required_config()
        print("✓ 环境变量配置验证通过")
    except ValueError as e:
        print(f"❌ {e}")
        print("\n请设置以下环境变量：")
        print("export GITLAB_URL=your_gitlab_url")
        print("export GITLAB_USER_ACCESS_TOKEN=your_gitlab_user_access_token")
        return

    mcp.run()


if __name__ == "__main__":
    main()
