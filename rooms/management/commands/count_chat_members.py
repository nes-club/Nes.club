import asyncio
import logging

import telegram
from django.conf import settings
from django.core.management import BaseCommand

from rooms.models import Room

log = logging.getLogger(__name__)


async def _count_all_chat_members():
    async with telegram.Bot(token=settings.TELEGRAM_TOKEN) as bot:
        for room in Room.objects.filter(chat_id__isnull=False):
            try:
                member_count = await bot.get_chat_member_count(room.chat_id)
                room.chat_member_count = member_count
                room.save()
                log.info(f"Updated member count for chat {room.slug}: {member_count} members")
            except telegram.error.TelegramError as ex:
                log.warning(f"Failed to get member count for chat {room.slug}: {ex}")


class Command(BaseCommand):
    help = "Count members in every telegram chat and save to database"

    def handle(self, *args, **options):
        if not settings.TELEGRAM_TOKEN:
            self.stdout.write("No telegram token. Skipping")
            return
        asyncio.run(_count_all_chat_members())
        self.stdout.write("Done 🥙")
