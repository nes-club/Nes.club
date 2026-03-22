import re

from django.conf import settings

WELCOME_MESSAGE = """✖️ <b>Я — твой личный бот для сообщества выпускников РЭШ</b>\n
Через меня можно отвечать на комменты и посты — просто напиши ответ реплаем на сообщение и я перепостю его в сообщество.
Так можно общаться в комментах даже не открывая сайт.\n
Еще в меня встроен глупый AI, который умеет искать и подсказывать всякое по сообществу.\n
Ну и я знаю всякие команды:
/top - Топ событий в сообществе
/random - Почитать случайный пост (неплохо убивает время)
/whois - Узнать профиль по телеграму
/horo - Гороскоп сообщества
/auth - Привязать бота к аккаунту в сообществе
/help - Справка"""

ANONYMOUS_MESSAGE = f"""Привет! Мы пока не знакомы. Привяжи меня к аккаунту командой /auth с
<a href=\"{settings.APP_HOST}/user/me/edit/bot/\">кодом из профиля</a> через пробел"""

BOT_MENTION_RE = re.compile(rf"@{settings.TELEGRAM_BOT_URL.rsplit("/", 1).pop()}\b", re.IGNORECASE)

MIN_COMMENT_LEN = 40
SKIP_COMMANDS = ("/skip", "/Skip", "#skip", "#ignore")
COMMENT_EMOJI_RE = re.compile(r"^💬.*")
POST_EMOJI_RE = re.compile(r"^[📝🔗❓💡🏢🤜🤛🗺🗄🔥🏗🙋‍♀️].*")
COMMENT_URL_RE = re.compile(r"https?://[^/]+/[a-zA-Z]+/.+?/#comment-([a-fA-F0-9-]+)")
POST_URL_RE = re.compile(r"https?://[^/]+/[a-zA-Z]+/(.+?)/")
