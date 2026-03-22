import asyncio
import logging

import telegram
from django.conf import settings

from rooms.models import Room
from users.models.user import User

log = logging.getLogger(__name__)


async def _ban_user_in_all_chats(user: User, is_permanent: bool):
    async with telegram.Bot(token=settings.TELEGRAM_TOKEN) as bot:
        for room in Room.objects.filter(chat_id__isnull=False):
            try:
                await bot.ban_chat_member(room.chat_id, user.telegram_id)
                log.info(f"User {user.slug} banned in chat {room.slug}")
                if not is_permanent:
                    # ban + immediate unban = kick (removes user without preventing rejoin)
                    await bot.unban_chat_member(room.chat_id, user.telegram_id)
            except telegram.error.TelegramError as ex:
                log.warning(f"Failed to ban user {user.slug} in chat {room.slug}: {ex}")


async def _unban_user_in_all_chats(user: User):
    async with telegram.Bot(token=settings.TELEGRAM_TOKEN) as bot:
        for room in Room.objects.filter(chat_id__isnull=False):
            try:
                await bot.unban_chat_member(room.chat_id, user.telegram_id)
                log.info(f"User {user.slug} unbanned in chat {room.slug}")
            except telegram.error.TelegramError as ex:
                log.warning(f"Can't unban user {user.slug} in chat {room.slug}: {ex}")


def ban_user_in_all_chats(user: User, is_permanent=True):
    if not user.telegram_id:
        log.warning(f"User {user.slug} has no telegram_id, can't ban")
        return
    asyncio.run(_ban_user_in_all_chats(user, is_permanent))


def unban_user_in_all_chats(user: User):
    if not user.telegram_id:
        log.warning(f"User {user.slug} has no telegram_id, can't unban")
        return
    asyncio.run(_unban_user_in_all_chats(user))
