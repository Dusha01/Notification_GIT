import logging
from typing import Any, Dict, List, Optional

import aiohttp

from src.core.config import settings
from src.modules.github.domain.entities.branch import Branch
from src.modules.github.domain.entities.commit import Commit, CommitAuthor
from src.modules.github.domain.entities.pull_request import PullRequest
from src.modules.github.domain.repositories.github_repository import GitHubRepository

logger = logging.getLogger(__name__)


class GitHubApiAdapter(GitHubRepository):

    def __init__(self, repo: str, token: Optional[str] = None):
        self._repo = repo
        self._token = token
        self._session: Optional[aiohttp.ClientSession] = None


    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session


    async def _request(self, endpoint: str) -> Optional[Any]:
        await self._ensure_session()
        url = f"https://api.github.com/repos/{self._repo}/{endpoint}"

        headers = {
            "User-Agent": "GitHub-Notification-Bot",
            "Accept": "application/vnd.github.v3+json",
        }
        if self._token:
            headers["Authorization"] = f"token {self._token}"

        try:
            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                logger.warning(f"GitHub API: {response.status} for {endpoint}")
                return None
        except Exception as e:
            logger.error(f"Request error for {endpoint}: {e}")
            return None


    @staticmethod
    def _commit_from_dict(data: Dict) -> Commit:
        commit_data = data["commit"]
        author_data = commit_data["author"]
        return Commit(
            sha=data["sha"],
            message=commit_data["message"],
            author=CommitAuthor(
                name=author_data["name"],
                email=author_data.get("email", ""),
            ),
            html_url=data["html_url"],
        )


    async def get_branches(self) -> List[Branch]:
        """Get all branches."""
        data = await self._request("branches?per_page=50")
        if not data:
            return []
        return [Branch(name=b["name"]) for b in data]


    async def get_branch_commits(
        self,
        branch: str,
        since: Optional[str] = None,
        per_page: int = 10,
    ) -> List[Commit]:
        """Get commits for a branch."""
        endpoint = f"commits?sha={branch}&per_page={per_page}"
        if since:
            endpoint += f"&since={since}"

        data = await self._request(endpoint)
        if not data:
            return []

        commits = [self._commit_from_dict(c) for c in data]
        for c in commits:
            c.branch = branch
        return commits


    async def get_pull_requests(self) -> List[PullRequest]:
        data = await self._request("pulls?state=all&per_page=10")
        if not data:
            return []

        return [
            PullRequest(
                number=pr["number"],
                title=pr["title"],
                author_login=pr["user"]["login"],
                html_url=pr["html_url"],
                merged=pr.get("merged", False),
                base_branch=pr["base"]["ref"],
                updated_at=pr.get("updated_at"),
            )
            for pr in data
        ]


    async def get_pull_request_commits(self, pr_number: int) -> List[Commit]:
        data = await self._request(f"pulls/{pr_number}/commits")
        if not data:
            return []
        return [self._commit_from_dict(c) for c in data]


    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
