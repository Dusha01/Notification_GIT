import asyncio
import logging
from typing import Dict, Optional, Set

from aiogram import Bot

from src.core.config import settings
from src.core.dependencies import get_github_service, get_notification_sender
from src.i18n import t
from src.modules.bot.domain.services.notification_sender import NotificationSender
from src.modules.github.application.use_cases.github_service import GitHubService
from src.modules.github.domain.entities.commit import Commit
from src.modules.github.domain.entities.pull_request import PullRequest

logger = logging.getLogger(__name__)


class TrackRepositoryUseCase:

    def __init__(
        self,
        github_service: GitHubService,
        notification_sender: NotificationSender,
    ):
        self._github = github_service
        self._notifier = notification_sender
        self._last_commit_shas: Dict[str, Set[str]] = {}
        self._last_pr_state: Dict[int, dict] = {}
        self._is_tracking = False
        self._task = None

    async def initialize(self) -> None:
        try:
            branches = await self._github.get_branches()
            if branches:
                for branch in branches:
                    commits = await self._github.get_branch_commits(
                        branch.name, per_page=20
                    )
                    if commits:
                        self._last_commit_shas[branch.name] = {
                            c.sha for c in commits
                        }
                        logger.info(
                            f"📝 Tracking branch '{branch.name}': {len(commits)} commits"
                        )

            prs = await self._github.get_pull_requests()
            for pr in prs:
                self._last_pr_state[pr.number] = {
                    "merged": pr.merged,
                    "title": pr.title,
                    "updated_at": pr.updated_at,
                }

            logger.info(
                f"📊 Initialized tracking for {len(self._last_commit_shas)} branches "
                f"and {len(self._last_pr_state)} PRs"
            )
        except Exception as e:
            logger.error(f"Error initializing tracking: {e}")


    async def _check_new_branches(self) -> bool:
        changes_detected = False
        try:
            current_branches = await self._github.get_branches()
            if not current_branches:
                return False

            current_names = {b.name for b in current_branches}
            tracked_names = set(self._last_commit_shas.keys())
            new_branches = current_names - tracked_names

            for branch_name in new_branches:
                commits = await self._github.get_branch_commits(
                    branch_name, per_page=20
                )
                if not commits:
                    continue

                self._last_commit_shas[branch_name] = {c.sha for c in commits}

                merge_pr = await self._find_merge_pr_for_branch(branch_name)
                if merge_pr:
                    logger.info(
                        f"🔀 Merge detected into new branch '{branch_name}' (PR #{merge_pr.number})"
                    )
                    pr_commits = await self._github.get_pull_request_commits(
                        merge_pr.number
                    )
                    if pr_commits:
                        pr_shas = {c.sha for c in pr_commits}
                        if merge_pr.merge_commit_sha:
                            pr_shas.add(merge_pr.merge_commit_sha)
                        self._last_commit_shas[branch_name].update(pr_shas)
                    self._last_pr_state[merge_pr.number] = {
                        "merged": True,
                        "title": merge_pr.title,
                        "updated_at": merge_pr.updated_at,
                    }
                    notification = GitHubService.format_merge_notification(merge_pr)
                    await self._notifier.send(notification)
                else:
                    logger.info(
                        f"🆕 New branch detected: '{branch_name}' with {len(commits)} commits"
                    )
                    latest = commits[0]
                    notification = self._format_new_branch_notification(
                        latest, branch_name
                    )
                    await self._notifier.send(notification)
                changes_detected = True
        except Exception as e:
            logger.error(f"Error checking new branches: {e}")
        return changes_detected

    async def _find_merge_pr_for_branch(
        self, branch_name: str
    ) -> Optional[PullRequest]:
        """Find a merged PR where base_branch == branch_name (most recent)."""
        prs = await self._github.get_pull_requests()
        merged_into_branch = [
            pr for pr in prs
            if pr.merged and pr.base_branch == branch_name
        ]
        if not merged_into_branch:
            return None
        merged_into_branch.sort(
            key=lambda p: p.updated_at or "1970-01-01",
            reverse=True,
        )
        return merged_into_branch[0]


    async def _check_commits(self) -> bool:
        changes_detected = False
        try:
            await self._check_new_branches()

            for branch_name in list(self._last_commit_shas.keys()):
                try:
                    commits = await self._github.get_branch_commits(
                        branch_name, per_page=20
                    )
                    if not commits:
                        continue

                    current_shas = {c.sha for c in commits}
                    known_shas = self._last_commit_shas[branch_name]
                    new_shas = current_shas - known_shas

                    if new_shas:
                        logger.info(
                            f"📬 Found {len(new_shas)} new commits in branch '{branch_name}'"
                        )
                        new_commits = [
                            c for c in reversed(commits) if c.sha in new_shas
                        ]
                        notification = GitHubService.format_push_notification(
                            new_commits, branch_name
                        )
                        await self._notifier.send(notification)
                        changes_detected = True

                        self._last_commit_shas[branch_name] = current_shas
                except Exception as e:
                    logger.error(f"Error checking commits in branch '{branch_name}': {e}")
        except Exception as e:
            logger.error(f"Error checking commits: {e}")
        return changes_detected


    async def _check_merges(self) -> bool:
        prs = await self._github.get_pull_requests()
        changes_detected = False
        current_prs = {}

        for pr in prs:
            current_prs[pr.number] = {
                "merged": pr.merged,
                "title": pr.title,
                "updated_at": pr.updated_at,
            }

            if pr.number not in self._last_pr_state:
                continue

            old_state = self._last_pr_state[pr.number]
            if not old_state["merged"] and pr.merged:
                pr_commits = await self._github.get_pull_request_commits(pr.number)
                if pr.base_branch in self._last_commit_shas:
                    pr_shas = {c.sha for c in pr_commits} if pr_commits else set()
                    if pr.merge_commit_sha:
                        pr_shas.add(pr.merge_commit_sha)
                    self._last_commit_shas[pr.base_branch].update(pr_shas)
                    logger.info(
                        f"Added {len(pr_shas)} commit SHAs to tracking for branch '{pr.base_branch}'"
                    )

                notification = GitHubService.format_merge_notification(pr)
                await self._notifier.send(notification)
                changes_detected = True

        self._last_pr_state = current_prs
        return changes_detected


    def _format_new_branch_notification(self, commit: Commit, branch_name: str) -> str:
        message = commit.message[:200] + (
            "..." if len(commit.message) > 200 else ""
        )
        return t(
            "NEW_BRANCH_NOTIFICATION",
            branch_name=branch_name,
            author=commit.author.name,
            sha_short=commit.sha_short,
            message=message,
            url=commit.html_url,
        )

    async def _check_updates(self) -> None:
        try:
            logger.info("🔍 Checking for updates...")
            merge_changes = await self._check_merges()
            commit_changes = await self._check_commits()
            if commit_changes or merge_changes:
                logger.info("✅ Changes detected and notifications sent")
            else:
                logger.info("✅ No changes detected")
        except Exception as e:
            logger.error(f"❌ Error in update check: {e}")


    async def run(self) -> None:
        self._is_tracking = True
        await self.initialize()

        while self._is_tracking:
            try:
                await self._check_updates()
                await asyncio.sleep(settings.CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic checker error: {e}")
                await asyncio.sleep(60)


    async def stop(self) -> None:
        self._is_tracking = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self._github.close()


_tracker: TrackRepositoryUseCase | None = None


async def start_tracking(bot: Bot) -> None:
    global _tracker
    github_service = get_github_service()
    notifier = get_notification_sender(bot)
    _tracker = TrackRepositoryUseCase(
        github_service=github_service,
        notification_sender=notifier,
    )
    _tracker._task = asyncio.create_task(_tracker.run())


async def stop_tracking() -> None:
    global _tracker
    if _tracker:
        await _tracker.stop()
        _tracker = None
