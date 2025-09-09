import aiohttp
import logging
from typing import Optional, List, Dict, Any

from config import Settings
from src.github.cosnt.const import COMMIT_NOTIFICATION, MERGE_NOTIFICATION

logger = logging.getLogger(__name__)

session: Optional[aiohttp.ClientSession] = None


async def create_session():
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()


async def close_session():
    global session
    if session and not session.closed:
        await session.close()


async def github_api_request(endpoint: str) -> Optional[Any]:
    await create_session()
    url = f"https://api.github.com/repos/{Settings.GITHUB_REPO}/{endpoint}"
    
    headers = {
        'User-Agent': 'GitHub-Notification-Bot',
        'Accept': 'application/vnd.github.v3+json'
    }
    if Settings.GITHUB_TOKEN:
        headers['Authorization'] = f"token {Settings.GITHUB_TOKEN}"
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.warning(f"GitHub API: {response.status} for {endpoint}")
                return None
    except Exception as e:
        logger.error(f"Request error for {endpoint}: {e}")
        return None


async def get_latest_commit() -> Optional[Dict]:
    data = await github_api_request("commits?per_page=1")
    return data[0] if data and len(data) > 0 else None


async def get_pull_requests() -> List[Dict]:
    data = await github_api_request("pulls?state=all&per_page=10")
    return data if data else []


def format_commit_notification(commit: Dict) -> str:
    commit_data = commit['commit']
    author = commit_data['author']['name']
    message = commit_data['message']
    sha_short = commit['sha'][:7]
    url = commit['html_url']
    
    return COMMIT_NOTIFICATION.format(
        repo=Settings.GITHUB_REPO,
        author=author,
        sha_short=sha_short,
        message=f"{message[:200]}{'...' if len(message) > 200 else ''}",
        url=url
    )


def format_merge_notification(pr: Dict) -> str:
    return MERGE_NOTIFICATION.format(
        repo=Settings.GITHUB_REPO,
        title=pr['title'],
        author=pr['user']['login'],
        number=pr['number'],
        url=pr['html_url']
    )