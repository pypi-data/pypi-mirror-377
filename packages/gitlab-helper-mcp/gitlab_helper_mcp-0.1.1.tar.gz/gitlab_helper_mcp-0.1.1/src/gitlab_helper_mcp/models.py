from pydantic import BaseModel


class MergeRequestChange(BaseModel):
    a_mode: str
    b_mode: str
    deleted_file: bool
    diff: str
    old_path: str
    new_path: str
    new_file: bool
    renamed_file: bool


class MergeRequest(BaseModel):
    id: int
    iid: int
    project_id: int
    title: str
    description: str
    source_branch: str
    target_branch: str
    merge_status: str
    state: str
    web_url: str
    work_in_progress: bool
    changes: list[MergeRequestChange] | None = None
