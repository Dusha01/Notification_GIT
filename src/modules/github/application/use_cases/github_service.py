"""GitHub application service - orchestrates use cases."""

from typing import List, Optional

from src.core.config import settings
from src.modules.github.domain.entities.branch import Branch
from src.modules.github.domain.entities.commit import Commit
from src.modules.github.domain.entities.pull_request import PullRequest
from src.modules.github.domain.constants.templates import (
    COMMIT_NOTIFICATION,
    MERGE_NOTIFICATION,
)
from src.modules.github.domain.repositories.github_repository import GitHubRepository
from src.modules.github.infrastructure.adapters.github_api_adapter import (
    GitHubApiAdapter,
)


class GitHubService:
    """Application service for GitHub operations."""

    def __init__(self, repository: Optional[GitHubRepository] = None):
        self._repo = repository or GitHubApiAdapter(
            repo=settings.GITHUB_REPO,
            token=settings.GITHUB_TOKEN,
        )

    async def get_branches(self) -> List[Branch]:
        """Get all branches."""
        return await self._repo.get_branches()

    async def get_branch_commits(
        self,
        branch: str,
        since: Optional[str] = None,
        per_page: int = 10,
    ) -> List[Commit]:
        """Get commits for a branch."""
        return await self._repo.get_branch_commits(
            branch=branch, since=since, per_page=per_page
        )

    async def get_pull_requests(self) -> List[PullRequest]:
        """Get all pull requests."""
        return await self._repo.get_pull_requests()

    async def get_pull_request_commits(self, pr_number: int) -> List[Commit]:
        """Get commits in a pull request."""
        return await self._repo.get_pull_request_commits(pr_number)

    async def close(self) -> None:
        """Close repository resources."""
        await self._repo.close()

    @staticmethod
    def format_commit_notification(commit: Commit, branch: Optional[str] = None) -> str:
        """Format commit for notification message."""
        message = commit.message[:200] + ("..." if len(commit.message) > 200 else "")
        base_text = COMMIT_NOTIFICATION.format(
            repo=settings.GITHUB_REPO,
            author=commit.author.name,
            sha_short=commit.sha_short,
            message=message,
            url=commit.html_url,
        )
        if branch and branch != "main":
            base_text = base_text.replace(
                "Новый коммит", f"Новый коммит в ветке '{branch}'"
            )
        return base_text

    @staticmethod
    def format_merge_notification(
        pr: PullRequest, commits: Optional[List[Commit]] = None
    ) -> str:
        """Format PR merge for notification message."""
        base_text = MERGE_NOTIFICATION.format(
            repo=settings.GITHUB_REPO,
            title=pr.title,
            author=pr.author_login,
            number=pr.number,
            url=pr.html_url,
        )
        if commits:
            commits_text = "\n\n📝 <b>Коммиты в PR:</b>\n"
            for commit in commits[:5]:
                msg = commit.message.split("\n")[0][:100]
                commits_text += (
                    f"• <code>{commit.sha_short}</code> {msg} ({commit.author.name})\n"
                )
            if len(commits) > 5:
                commits_text += f"... и ещё {len(commits) - 5} коммитов"
            base_text += commits_text
        return base_text
