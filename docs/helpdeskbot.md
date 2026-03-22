# helpdeskbot — Support Telegram Bot

Separate Telegram bot for user support Q&A with a moderation queue.

## Purpose

Members send questions to the bot. Questions are forwarded to a private moderator channel. Moderators reply in the channel, and replies are forwarded back to the user.

## Architecture

Separate bot with its own token (`settings.HELPDESK_BOT_TOKEN`), running in its own Docker container. Connects to the same PostgreSQL database.

## Flow

```
User sends /start to @helpdeskbot
  → Bot asks for question
  → Question forwarded to moderator channel
  → Moderator replies in channel thread
  → Reply forwarded back to user as DM
```

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Bot startup (polling or webhook) |
| `handlers/question.py` | Question submission flow |
| `handlers/answers.py` | Reply handling and forwarding |
| `room.py` | Channel/room configuration |
| `config.py` | Bot token, channel IDs |

## Configuration

- `HELPDESK_BOT_TOKEN` — separate from main bot token
- `HELPDESK_CHANNEL_ID` — Telegram channel where questions are posted

## Container

Runs as `helpdeskbot` service in Docker Compose.
