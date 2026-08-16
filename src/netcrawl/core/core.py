import logging
import platform
import asyncio

from netcrawl.util.utils import ferr
from netcrawl.core.aioscan import aiohtml
from netcrawl.config.visual import renderlogo
from netcrawl.core.params import NetCrawlParams

async def asynl(url: str, context: NetCrawlParams):
    try:
        if platform.system == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy)
        renderlogo()
        path = aiohtml(url, context)
        await path.aiostart()
    except Exception as e:logging.error(ferr(e), exc_info=True)