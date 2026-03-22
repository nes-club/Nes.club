from asgiref.sync import sync_to_async

from django.conf import settings
from telegram import Update
from telegram.error import Forbidden
from telegram.ext import ContextTypes

from bot.cache import flush_users_cache, cached_telegram_users
from users.models.user import User


async def command_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text or " " not in update.message.text:
        await update.effective_chat.send_message(
            "☝️ Нужно прислать мне секретный код. "
            f"Напиши /auth и код из <a href=\"{settings.APP_HOST}/user/me/edit/bot/\">профиля в сообществе</a> "
            "через пробел. Только не публикуй его в публичных чатах!",
            parse_mode="HTML"
        )
        return None

    secret_code = update.message.text.split(" ", 1)[1].strip()
    user = await sync_to_async(User.objects.filter(secret_hash=secret_code).first)()

    if not user:
        await update.effective_chat.send_message("Пользователь с таким кодом не найден")
        return None

    user.telegram_id = update.effective_user.id
    user.telegram_data = {
        "id": update.effective_user.id,
        "username": update.effective_user.username,
        "first_name": update.effective_user.first_name,
        "last_name": update.effective_user.last_name,
        "language_code": update.effective_user.language_code,
    }
    await sync_to_async(user.save)()

    try:
        await update.effective_chat.send_message(f"Отличный код! Приятно познакомиться, {user.slug}")
    except Forbidden:
        return None

    await update.message.delete()

    if user.moderation_status != User.MODERATION_STATUS_APPROVED:
        await update.effective_chat.send_message(f"Теперь осталось пройти модерацию. Бот заработает сразу после этого")

    # Flush cache so next request repopulates with updated telegram_id
    flush_users_cache()
    await sync_to_async(cached_telegram_users)()

    return None
