from typing import Optional, Any

import telegram
from telegram import Update

from helpdeskbot import config


async def send_message(
    chat_id: int,
    text: str,
    reply_to_message_id: int = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
):
    async with telegram.Bot(token=config.TELEGRAM_HELP_DESK_BOT_TOKEN) as bot:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_to_message_id,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )


async def send_reply(
    update: Update,
    text: str,
    parse_mode: str = "HTML",
    reply_markup: Optional[Any] = None,
    disable_web_page_preview: bool = True,
):
    await update.message.reply_text(
        text=text,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
        disable_web_page_preview=disable_web_page_preview,
    )


def get_channel_message_link(message_id: str) -> str:
    channel_link_id = str(config.TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_ID).replace("-100", "")
    return get_chat_message_link(channel_link_id, message_id)


def get_chat_message_link(chat_id: str, message_id: str) -> str:
    return f"https://t.me/c/{chat_id}/{message_id}"
