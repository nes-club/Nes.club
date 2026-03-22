# bot — Main Telegram Bot

Primary Telegram bot for authentication, commenting, voting, moderation callbacks, and fun commands.

## Version

python-telegram-bot **20.7** (async, Application builder pattern). Fully migrated from v12.

## Startup

```python
# bot/main.py
application = Application.builder().token(settings.TELEGRAM_TOKEN).build()
# Development: application.run_polling()
# Production: application.run_webhook(...)
```

## Handler Modules

| File | Commands / Triggers |
|------|---------------------|
| `handlers/auth.py` | `/auth` — link Telegram account to club profile |
| `handlers/comments.py` | Reply to bot messages → create comment on post |
| `handlers/upvotes.py` | `+` / `++` in reply → upvote post or comment |
| `handlers/moderation.py` | Inline keyboard callbacks for approve/reject (admin only) |
| `handlers/top.py` | `/top` — trending posts |
| `handlers/whois.py` | `/whois @user` or forward a message → user profile info |
| `handlers/fun.py` | `/random`, `/horo` (horoscope) |
| `handlers/posts.py` | Subscribe/unsubscribe from post notifications |

## Key Patterns

- All handler functions are `async def`
- Admin chat filtering: moderation callbacks only work in the club admin chat
- Reply-to-message workflow: replying to a bot notification creates a comment in the club
- Horoscope is deterministic (hash of Telegram ID + current date)

## Configuration (`bot/config.py`)

- `CLUB_CHAT_ID` — admin moderation chat
- `TELEGRAM_CLUB_CHANNEL_URL` — public channel
- Welcome message template
- Regex patterns for upvote detection

## Sync Context Usage

When Django views need to send a Telegram message synchronously, use the bridge in `notifications/telegram/bot.py`:
```python
run_bot_action(lambda bot: bot.send_message(chat_id=..., text=...))
```
Do **not** call `asyncio.run()` directly in views — use the wrapper.

## Container

Runs as a separate Docker service (`bot`). Shares the same PostgreSQL database as the web container.
