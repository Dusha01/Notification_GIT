import logging
import asyncio
from aiogram import Bot, Dispatcher

from config import Settings
from src.common import register_common_handlers
from src.github.github_services.github_services import get_latest_commit, get_pull_requests, close_session
from src.notification.notification_services.notification_services import send_notification



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


bot = Bot(token=Settings.BOT_TOKEN)
dp = Dispatcher()


last_commit_sha = None
last_pr_state = {}



async def check_commits():
    global last_commit_sha
    
    commit = await get_latest_commit()
    if not commit:
        return False
    
    current_sha = commit['sha']
    
    if last_commit_sha is None:
        last_commit_sha = current_sha
        logger.info(f"Initial commit set: {current_sha[:7]}")
        return False
    
    if last_commit_sha != current_sha:
        commit_data = commit['commit']
        author = commit_data['author']['name']
        message = commit_data['message']
        sha_short = current_sha[:7]
        url = commit['html_url']
        
        notification = (
            f"📦 <b>Новый коммит в {Settings.GITHUB_REPO}</b>\n\n"
            f"👤 <b>Автор:</b> {author}\n"
            f"🔖 <b>Хеш:</b> <code>{sha_short}</code>\n\n"
            f"📝 <b>Сообщение:</b>\n{message[:200]}{'...' if len(message) > 200 else ''}\n\n"
            f"🔗 <a href='{url}'>Посмотреть коммит</a>"
        )
        
        await send_notification(bot, notification)
        last_commit_sha = current_sha
        return True
    
    return False



async def check_merges():
    global last_pr_state
    
    prs = await get_pull_requests()
    changes_detected = False
    
    current_prs = {}
    for pr in prs:
        pr_number = pr['number']
        pr_merged = pr.get('merged', False)
        pr_title = pr['title']
        pr_user = pr['user']['login']
        pr_url = pr['html_url']
        
        current_prs[pr_number] = {
            'merged': pr_merged,
            'title': pr_title
        }
        
        if pr_number not in last_pr_state:
            pass
        else:
            old_state = last_pr_state[pr_number]
            if not old_state['merged'] and pr_merged:
                notification = (
                    f"🎉 <b>Pull Request мерджнут: {Settings.GITHUB_REPO}</b>\n\n"
                    f"📋 <b>Заголовок:</b> {pr_title}\n"
                    f"👤 <b>Автор:</b> {pr_user}\n"
                    f"🔢 <b>Номер:</b> #{pr_number}\n\n"
                    f"🔗 <a href='{pr_url}'>Посмотреть PR</a>"
                )
                
                await send_notification(bot, notification)
                changes_detected = True
    
    last_pr_state = current_prs
    return changes_detected



async def check_updates():
    try:
        logger.info("🔍 Checking for updates...")
        
        commit_changes = await check_commits()
        merge_changes = await check_merges()
        
        if commit_changes or merge_changes:
            logger.info("✅ Changes detected and notifications sent")
        else:
            logger.info("✅ No changes detected")
            
    except Exception as e:
        logger.error(f"❌ Error in update check: {e}")



async def periodic_checker():
    while True:
        try:
            await check_updates()
            await asyncio.sleep(Settings.CHECK_INTERVAL)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Periodic checker error: {e}")
            await asyncio.sleep(60)



async def on_startup():
    logger.info("🚀 Bot starting up...")
    logger.info(f"📁 Tracking repository: {Settings.GITHUB_REPO}")
    logger.info(f"👥 Notification recipients: {Settings.CHAT_IDS}")
    
    await check_updates()
    asyncio.create_task(periodic_checker())



async def on_shutdown():
    logger.info("🛑 Bot shutting down...")
    await close_session()



async def main():
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