import logging
import asyncio
from datetime import datetime, timezone
from aiogram import Bot, Dispatcher

from config import Settings
from src.github.github_services.github_services import (
    get_latest_commit, 
    get_branch_commits,
    get_branches,
    get_pull_requests, 
    close_session, 
    format_commit_notification, 
    format_merge_notification
)

from src.notification.notification_services.notification_services import send_notification
from src.common import register_common_handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



last_commits = {}
last_pr_state = {}
last_check_time = datetime.now(timezone.utc)


async def check_commits(bot: Bot):
    global last_commits, last_check_time
    
    changes_detected = False
    current_time = datetime.now(timezone.utc)
    
    try:
        # Получаем список всех веток
        branches = await get_branches()
        if not branches:
            return False
        
        for branch in branches:
            branch_name = branch['name']
            
            # Получаем самый последний коммит в ветке
            latest_commit = await get_latest_commit(branch_name)
            if not latest_commit:
                continue
                
            commit_sha = latest_commit['sha']
            
            # Если это первая проверка для ветки - просто запоминаем коммит
            if branch_name not in last_commits:
                last_commits[branch_name] = commit_sha
                continue
            
            # Если коммит изменился - отправляем уведомление
            if last_commits[branch_name] != commit_sha:
                notification = format_commit_notification(latest_commit, branch_name)
                await send_notification(bot, notification)
                changes_detected = True
                
                # Обновляем последний известный коммит для ветки
                last_commits[branch_name] = commit_sha
    
    except Exception as e:
        logger.error(f"Error checking commits: {e}")
    
    # Обновляем время последней проверки
    last_check_time = current_time
    return changes_detected


async def check_merges(bot: Bot):
    global last_pr_state
    
    prs = await get_pull_requests()
    changes_detected = False
    
    current_prs = {}
    for pr in prs:
        pr_number = pr['number']
        pr_merged = pr.get('merged', False)
        pr_updated_at = pr.get('updated_at')
        
        current_prs[pr_number] = {
            'merged': pr_merged,
            'title': pr['title'],
            'updated_at': pr_updated_at
        }
        
        # Если PR новый - пропускаем (ждем следующего обновления)
        if pr_number not in last_pr_state:
            continue
        
        old_state = last_pr_state[pr_number]
        
        # Проверяем, был ли PR мерджнут с момента последней проверки
        if not old_state['merged'] and pr_merged:
            notification = format_merge_notification(pr)
            await send_notification(bot, notification)
            changes_detected = True
    
    last_pr_state = current_prs
    return changes_detected


async def check_updates(bot: Bot):
    try:
        logger.info("🔍 Checking for updates...")
        
        commit_changes = await check_commits(bot)
        merge_changes = await check_merges(bot)
        
        if commit_changes or merge_changes:
            logger.info("✅ Changes detected and notifications sent")
        else:
            logger.info("✅ No changes detected")
            
    except Exception as e:
        logger.error(f"❌ Error in update check: {e}")


async def periodic_checker(bot: Bot):
    while True:
        try:
            await check_updates(bot)
            await asyncio.sleep(Settings.CHECK_INTERVAL)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Periodic checker error: {e}")
            await asyncio.sleep(60)


async def on_startup(bot: Bot):
    logger.info("🚀 Bot starting up...")
    logger.info(f"📁 Tracking repository: {Settings.GITHUB_REPO}")
    logger.info(f"👥 Notification recipients: {len(Settings.CHAT_IDS)} users")
    
    # Инициализируем отслеживание - получаем текущие состояния
    await initialize_tracking()
    
    # Запускаем периодическую проверку
    asyncio.create_task(periodic_checker(bot))


async def initialize_tracking():
    """Инициализация отслеживания - получаем текущие состояния всех веток и PR"""
    global last_commits, last_pr_state
    
    try:
        # Инициализируем последние коммиты для всех веток
        branches = await get_branches()
        if branches:
            for branch in branches:
                branch_name = branch['name']
                latest_commit = await get_latest_commit(branch_name)
                if latest_commit:
                    last_commits[branch_name] = latest_commit['sha']
                    logger.info(f"📝 Tracking branch '{branch_name}': {latest_commit['sha'][:7]}")
        
        # Инициализируем состояние PR
        prs = await get_pull_requests()
        for pr in prs:
            pr_number = pr['number']
            last_pr_state[pr_number] = {
                'merged': pr.get('merged', False),
                'title': pr['title'],
                'updated_at': pr.get('updated_at')
            }
            
        logger.info(f"📊 Initialized tracking for {len(last_commits)} branches and {len(last_pr_state)} PRs")
        
    except Exception as e:
        logger.error(f"Error initializing tracking: {e}")


async def on_shutdown(bot: Bot):
    logger.info("🛑 Bot shutting down...")
    await close_session()


async def main():
    bot = Bot(token=Settings.BOT_TOKEN)
    dp = Dispatcher()
    
    register_common_handlers(dp)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())