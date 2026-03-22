import asyncio
import logging
from collections import namedtuple

import telegram
from django.conf import settings
from django.template import loader

from common.regexp import IMAGE_RE

log = logging.getLogger(__name__)

Chat = namedtuple("Chat", ["id"])

ADMIN_CHAT = Chat(id=settings.TELEGRAM_ADMIN_CHAT_ID) if settings.TELEGRAM_ADMIN_CHAT_ID else None
CLUB_CHAT = Chat(id=settings.TELEGRAM_CLUB_CHAT_ID) if settings.TELEGRAM_CLUB_CHAT_ID else None
CLUB_CHANNEL = Chat(id=settings.TELEGRAM_CLUB_CHANNEL_ID) if settings.TELEGRAM_CLUB_CHANNEL_ID else None
CLUB_ONLINE = Chat(id=settings.TELEGRAM_ONLINE_CHANNEL_ID) if settings.TELEGRAM_ONLINE_CHANNEL_ID else None
VIBES_CHAT = Chat(id=settings.TELEGRAM_VIBES_CHAT_ID) if settings.TELEGRAM_VIBES_CHAT_ID else None
PARLIAMENT_CHAT = Chat(id=settings.TELEGRAM_PARLIAMENT_CHAT_ID) if settings.TELEGRAM_PARLIAMENT_CHAT_ID else None

NORMAL_TEXT_LIMIT = 4096
PHOTO_TEXT_LIMIT = 1024


async def _send_telegram_message(chat_id, text, parse_mode, disable_preview, **kwargs):
    async with telegram.Bot(token=settings.TELEGRAM_TOKEN) as bot:
        images_in_message = IMAGE_RE.findall(text)
        if len(images_in_message) == 1 and len(text) < PHOTO_TEXT_LIMIT:
            return await bot.send_photo(
                chat_id=chat_id,
                photo=images_in_message[0],
                caption=text[:PHOTO_TEXT_LIMIT],
                parse_mode=parse_mode,
                **kwargs
            )
        else:
            return await bot.send_message(
                chat_id=chat_id,
                text=text[:NORMAL_TEXT_LIMIT],
                parse_mode=parse_mode,
                disable_web_page_preview=disable_preview,
                **kwargs
            )


async def _send_telegram_image(chat_id, image_url, text, parse_mode, **kwargs):
    async with telegram.Bot(token=settings.TELEGRAM_TOKEN) as bot:
        return await bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption=text[:PHOTO_TEXT_LIMIT],
            parse_mode=parse_mode,
            **kwargs
        )


async def _remove_action_buttons(chat_id, message_id, **kwargs):
    async with telegram.Bot(token=settings.TELEGRAM_TOKEN) as bot:
        return await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
            **kwargs
        )


def send_telegram_message(
    chat: Chat,
    text: str,
    parse_mode: str = "HTML",
    disable_preview: bool = True,
    **kwargs
):
    if not settings.TELEGRAM_TOKEN:
        log.warning("No telegram token. Skipping")
        return

    if not chat:
        log.warning("No chat id. Skipping")
        return

    log.info(f"Telegram: sending message to chat_id {chat.id}, starting with {text[:10]}...")

    try:
        return asyncio.run(_send_telegram_message(chat.id, text, parse_mode, disable_preview, **kwargs))
    except telegram.error.TelegramError as ex:
        log.warning(f"Telegram error: {ex}")


def send_telegram_image(
    chat: Chat,
    image_url: str,
    text: str,
    parse_mode: str = "HTML",
    **kwargs
):
    if not settings.TELEGRAM_TOKEN:
        log.warning("No telegram token. Skipping")
        return

    log.info(f"Telegram: sending the image: {image_url} {text[:20]}")

    try:
        return asyncio.run(_send_telegram_image(chat.id, image_url, text, parse_mode, **kwargs))
    except telegram.error.TelegramError as ex:
        log.warning(f"Telegram error: {ex}")


def remove_action_buttons(chat: Chat, message_id: str, **kwargs):
    try:
        return asyncio.run(_remove_action_buttons(chat.id, message_id, **kwargs))
    except telegram.error.TelegramError:
        log.info("Buttons are already removed. Skipping")
        return None


def render_html_message(template, **data):
    template = loader.get_template(f"messages/{template}")
    return template.render({
        **data,
        "settings": settings
    })
