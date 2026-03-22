import logging
import os
import sys

# IMPORTANT: this should go before any django-related imports (models, apps, settings)
# These lines must be kept together till THE END
import django
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "club.settings")
django.setup()
# THE END

from helpdeskbot import config
from helpdeskbot.handlers.question import update_discussion_message_id, QuestionHandler
from helpdeskbot.handlers.answers import on_reply_message

from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler

log = logging.getLogger(__name__)


async def on_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(
        "🤔 <b>Я бот справочной сообщества.</b>\n\n"
        "Через меня можно задать вопрос и получить ответы от других участников.\n\n\n"
        "Список команд:\n\n"
        "/start - Создание и отправка вопроса\n"
        "/help - Справка",
        parse_mode="HTML"
    )


async def on_telegram_admin_bot_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return None

    message = update.message
    if message.chat.id == int(config.TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_DISCUSSION_ID) \
        and message.forward_from_chat \
        and message.forward_from_chat.id == int(config.TELEGRAM_HELP_DESK_BOT_QUESTION_CHANNEL_ID) \
        and message.forward_from_message_id:
        update_discussion_message_id(update)


def main() -> None:
    if not config.TELEGRAM_HELP_DESK_BOT_TOKEN:
        log.warning("TELEGRAM_HELP_DESK_BOT_TOKEN is not set, helpdeskbot is disabled")
        return

    # Initialize telegram
    application = Application.builder().token(config.TELEGRAM_HELP_DESK_BOT_TOKEN).build()

    # Set handlers
    application.add_handler(CommandHandler("help", on_help_command))
    application.add_handler(QuestionHandler("start"))
    application.add_handler(MessageHandler(filters.REPLY & ~filters.COMMAND, on_reply_message))
    application.add_handler(MessageHandler(filters.User(user_id=config.TELEGRAM_ADMIN_BOT_ID), on_telegram_admin_bot_message))

    # Start the bot
    if settings.DEBUG:
        application.run_polling()
        # ^ polling is useful for development since you don't need to expose webhook endpoints
    else:
        log.info(f"Set webhook: {config.TELEGRAM_HELP_DESK_BOT_WEBHOOK_URL}<token>")
        application.run_webhook(
            listen=config.TELEGRAM_HELP_DESK_BOT_WEBHOOK_HOST,
            port=config.TELEGRAM_HELP_DESK_BOT_WEBHOOK_PORT,
            url_path=f"telegram/helpdeskbot/webhook/{config.TELEGRAM_HELP_DESK_BOT_TOKEN}",
            webhook_url=config.TELEGRAM_HELP_DESK_BOT_WEBHOOK_URL + config.TELEGRAM_HELP_DESK_BOT_TOKEN,
        )


if __name__ == '__main__':
    main()
