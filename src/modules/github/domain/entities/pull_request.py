from dataclasses import dataclass
from typing import Optional


@dataclass
class PullRequest:

    number: int
    title: str
    author_login: str
    html_url: str
    merged: bool
    base_branch: str
    head_branch: str
    merge_commit_sha: Optional[str] = None
    updated_at: Optional[str] = None
