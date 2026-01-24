import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Set
from aiogram import Bot

from config import Settings
from src.github.github_services.github_services import (
    get_branches,
    get_branch_commits,
    get_pull_requests,
    get_pull_request_commits,
    close_session,
    format_commit_notification,
    format_merge_notification
)
from src.notification.notification_services.notification_services import send_notification


logger = logging.getLogger(__name__)


class Tracker:
    def __init__(self):
        self.last_commit_shas: Dict[str, Set[str]] = {}
        self.last_pr_state: Dict[int, Dict] = {}
        self.last_check_time = datetime.now(timezone.utc)
        self.is_tracking = False
        self.task = None

    async def initialize(self):
        """Инициализация отслеживания - получаем текущие состояния всех веток и PR"""
        try:
            branches = await get_branches()
            if branches:
                for branch in branches:
                    branch_name = branch['name']
                    commits = await get_branch_commits(branch_name, per_page=20)
                    if commits:
                        self.last_commit_shas[branch_name] = {commit['sha'] for commit in commits}
                        logger.info(f"📝 Tracking branch '{branch_name}': {len(commits)} commits")
            
            prs = await get_pull_requests()
            for pr in prs:
                pr_number = pr['number']
                self.last_pr_state[pr_number] = {
                    'merged': pr.get('merged', False),
                    'title': pr['title'],
                    'updated_at': pr.get('updated_at')
                }
                
            logger.info(f"📊 Initialized tracking for {len(self.last_commit_shas)} branches and {len(self.last_pr_state)} PRs")
            
        except Exception as e:
            logger.error(f"Error initializing tracking: {e}")


    async def check_new_branches(self, bot: Bot) -> bool:
        """Проверяет и добавляет новые ветки для отслеживания"""
        changes_detected = False
        
        try:
            current_branches = await get_branches()
            if not current_branches:
                return False
            
            current_branch_names = {branch['name'] for branch in current_branches}
            tracked_branch_names = set(self.last_commit_shas.keys())
            
            new_branches = current_branch_names - tracked_branch_names
            
            for branch_name in new_branches:
                if branch_name not in self.last_commit_shas:
                    commits = await get_branch_commits(branch_name, per_page=20)
                    if commits:
                        self.last_commit_shas[branch_name] = {commit['sha'] for commit in commits}
                        logger.info(f"🆕 New branch detected: '{branch_name}' with {len(commits)} commits")
                        
                        if len(commits) > 0:
                            latest_commit = commits[0]
                            notification = self.format_new_branch_notification(latest_commit, branch_name)
                            await send_notification(bot, notification)
                            changes_detected = True
        
        except Exception as e:
            logger.error(f"Error checking new branches: {e}")
            
        return changes_detected


    async def check_commits(self, bot: Bot) -> bool:
        """Проверяет новые коммиты во всех ветках"""
        changes_detected = False
        
        try:
            await self.check_new_branches(bot)
            
            for branch_name in list(self.last_commit_shas.keys()):
                try:
                    commits = await get_branch_commits(branch_name, per_page=20)
                    if not commits:
                        continue
                    
                    current_shas = {commit['sha'] for commit in commits}
                    known_shas = self.last_commit_shas[branch_name]
                    new_shas = current_shas - known_shas
                    
                    if new_shas:
                        logger.info(f"📬 Found {len(new_shas)} new commits in branch '{branch_name}'")
                        
                        for commit in reversed(commits):  # reversed чтобы получить старые коммиты первыми
                            if commit['sha'] in new_shas:
                                notification = format_commit_notification(commit, branch_name)
                                await send_notification(bot, notification)
                                changes_detected = True
                                await asyncio.sleep(0.5)  # Небольшая задержка между уведомлениями
                        
                        self.last_commit_shas[branch_name] = current_shas
                
                except Exception as e:
                    logger.error(f"Error checking commits in branch '{branch_name}': {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error checking commits: {e}")
        
        return changes_detected


    async def check_merges(self, bot: Bot) -> bool:
        """Проверяет мерджи PR"""
        prs = await get_pull_requests()
        changes_detected = False
        
        current_prs = {}
        for pr in prs:
            pr_number = pr['number']
            pr_merged = pr.get('merged', False)
            
            current_prs[pr_number] = {
                'merged': pr_merged,
                'title': pr['title'],
                'updated_at': pr.get('updated_at')
            }
            
            if pr_number not in self.last_pr_state:
                continue
            
            old_state = self.last_pr_state[pr_number]
            
            if not old_state['merged'] and pr_merged:
                # Получаем коммиты PR
                pr_commits = await get_pull_request_commits(pr_number)
                if pr_commits:
                    # Добавляем SHA коммитов в отслеживаемые для base ветки, чтобы не дублировать уведомления
                    base_branch = pr['base']['ref']
                    if base_branch in self.last_commit_shas:
                        pr_commit_shas = {commit['sha'] for commit in pr_commits}
                        self.last_commit_shas[base_branch].update(pr_commit_shas)
                        logger.info(f"Added {len(pr_commits)} PR commits to tracking for branch '{base_branch}'")
                
                notification = format_merge_notification(pr, pr_commits)
                await send_notification(bot, notification)
                changes_detected = True
        
        self.last_pr_state = current_prs
        return changes_detected


    def format_new_branch_notification(self, commit: Dict, branch_name: str) -> str:
        """Форматирует уведомление о новой ветке"""
        commit_data = commit['commit']
        author = commit_data['author']['name']
        message = commit_data['message']
        sha_short = commit['sha'][:7]
        url = commit['html_url']
        
        return f"""
🌿 <b>Создана новая ветка: {branch_name}</b>

📦 <b>Последний коммит:</b>
👤 <b>Автор:</b> {author}
🔖 <b>Хеш:</b> <code>{sha_short}</code>

📝 <b>Сообщение:</b>
{message[:200]}{'...' if len(message) > 200 else ''}

🔗 <a href='{url}'>Посмотреть коммит</a>
"""

    async def check_updates(self, bot: Bot):
        """Основная функция проверки обновлений"""
        try:
            logger.info("🔍 Checking for updates...")
            
            commit_changes = await self.check_commits(bot)
            merge_changes = await self.check_merges(bot)
            
            if commit_changes or merge_changes:
                logger.info("✅ Changes detected and notifications sent")
            else:
                logger.info("✅ No changes detected")
                
        except Exception as e:
            logger.error(f"❌ Error in update check: {e}")

    async def start_periodic_check(self, bot: Bot):
        """Запускает периодическую проверку"""
        self.is_tracking = True
        await self.initialize()
        
        while self.is_tracking:
            try:
                await self.check_updates(bot)
                await asyncio.sleep(Settings.CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic checker error: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        """Останавливает отслеживание"""
        self.is_tracking = False
        if self.task:
            self.task.cancel()
        await close_session()


tracker = Tracker()


async def start_tracking(bot: Bot):
    """Запускает отслеживание"""
    tracker.task = asyncio.create_task(tracker.start_periodic_check(bot))


async def stop_tracking():
    """Останавливает отслеживание"""
    await tracker.stop()