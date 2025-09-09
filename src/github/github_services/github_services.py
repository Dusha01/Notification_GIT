import aiohttp
import logging
from typing import Optional, List, Dict, Any

from config import Settings



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