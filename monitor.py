import aiohttp
import asyncio
import time
from database import update_status, get_urls

async def check_website(session, url_id, url):
    start = time.time()
    try:
        async with session.get(url, timeout=10) as response:
            status = 'UP' if response.status == 200 else 'DOWN'
    except:
        status = 'DOWN'
    response_time = (time.time() - start) * 1000
    update_status(url_id, status, response_time)
    return status, response_time

async def monitor_all():
    urls = get_urls()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url_id, url, status, monitoring in urls:
            if monitoring:
                tasks.append(check_website(session, url_id, url))
        await asyncio.gather(*tasks)
