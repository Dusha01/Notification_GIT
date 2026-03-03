from abc import ABC, abstractmethod
from typing import List, Optional

from src.modules.github.domain.entities.branch import Branch
from src.modules.github.domain.entities.commit import Commit
from src.modules.github.domain.entities.pull_request import PullRequest


class GitHubRepository(ABC):

    @abstractmethod
    async def get_branches(self) -> List[Branch]:
        ...


    @abstractmethod
    async def get_branch_commits(
        self,
        branch: str,
        since: Optional[str] = None,
        per_page: int = 10,
    ) -> List[Commit]:
        ...


    @abstractmethod
    async def get_pull_requests(self) -> List[PullRequest]:
        ...


    @abstractmethod
    async def get_pull_request_commits(self, pr_number: int) -> List[Commit]:
        ...


    @abstractmethod
    async def close(self) -> None:
        ...
