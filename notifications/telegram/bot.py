import asyncio
import logging

import telegram
from django.conf import settings

log = logging.getLogger(__name__)


async def _run_bot_action(coro):
    async with telegram.Bot(token=settings.TELEGRAM_TOKEN) as bot:
        return await coro(bot)


def run_bot_action(coro_factory):
    """Run a one-shot async bot action from synchronous Django code."""
    return asyncio.run(_run_bot_action(coro_factory))
