# bot — Main Telegram Bot

Primary Telegram bot for authentication, commenting, voting, moderation callbacks, and fun commands.

## Version

python-telegram-bot **20.7** (async, Application builder pattern).

## Startup

```python
# bot/main.py
application = Application.builder().token(settings.TELEGRAM_TOKEN).build()
# Development (DEBUG=true): application.run_polling()
# Production (DEBUG=false): application.run_webhook(...)
```

## Handler Modules

| File | Commands / Triggers |
|------|---------------------|
| `handlers/auth.py` | `/start <code>`, `/auth <code>` — link Telegram account to club profile |
| `handlers/comments.py` | Reply to bot messages → create comment on post |
| `handlers/upvotes.py` | `+` / `++` in reply → upvote post or comment |
| `handlers/moderation.py` | Inline keyboard callbacks for approve/reject (admin only) |
| `handlers/top.py` | `/top` — trending posts |
| `handlers/whois.py` | `/whois @user` or forward a message → user profile info |
| `handlers/fun.py` | `/random`, `/horo` (horoscope) |
| `handlers/posts.py` | Subscribe/unsubscribe from post notifications |

## Key Patterns

- All handler functions are `async def`
- **All Django ORM calls must be wrapped with `sync_to_async`** — the bot runs in an async webhook context and Django ORM is synchronous. Pattern: `await sync_to_async(Model.objects.filter(...).first)()`
- For multi-step DB operations, wrap in an inner sync function: `await sync_to_async(lambda: ...)()` or `await sync_to_async(_inner_func)()`
- Admin chat filtering: moderation callbacks only work in the club admin chat
- Reply-to-message workflow: replying to a bot notification creates a comment in the club

## Configuration

**Required env vars:**
```
TELEGRAM_TOKEN=<токен от @BotFather>
TELEGRAM_BOT_URL=https://t.me/<username_бота>   # для кнопки «Привязать бота» в профиле
TELEGRAM_ADMIN_CHAT_ID=<ID чата модераторов>
```

**Webhook (production only):**
```
TELEGRAM_BOT_WEBHOOK_HOST_URL=https://<bot-service>.railway.app
```
Without this, falls back to `APP_HOST` — Telegram would send webhooks to the wrong service.

In development (`DEBUG=true`) the bot uses polling — no webhook vars needed.

## Привязка бота к профилю

1. Пользователь нажимает «Привязать бота» в `/user/me/edit/bot/`
2. Открывается `https://t.me/<bot>?start=<secret_hash>`
3. Telegram отправляет боту `/start <secret_hash>`
4. Бот находит пользователя по `secret_hash` и сохраняет `telegram_id`

## Container

Runs as a separate Docker/Railway service (`bot`). Shares the same PostgreSQL database as the web container.

## Sync Context Usage

When Django views need to send a Telegram message synchronously, use the bridge in `notifications/telegram/bot.py`:
```python
run_bot_action(lambda bot: bot.send_message(chat_id=..., text=...))
```
Do **not** call `asyncio.run()` directly in views — use the wrapper.
