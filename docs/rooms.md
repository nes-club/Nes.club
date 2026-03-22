# rooms — Channel Directory

Organize posts by topic channels. Each room can be linked to an external Telegram group, creating a Telegram channel directory.

## Models

| Model | Purpose |
|-------|---------|
| `Room` | Named channel with optional Telegram group link |
| `RoomSubscription` | Users following a room |

## Key Room Fields

| Field | Purpose |
|-------|---------|
| `slug` | URL identifier |
| `chat_id`, `chat_url`, `chat_name` | Telegram group integration |
| `members_count` | Cached member count (updated by `count_chat_members` task) |
| `send_new_posts_to_chat` | Auto-forward new posts to Telegram group |
| `send_new_comments_to_chat` | Auto-forward comments |
| `network_group` | Groups rooms in sidebar (via `misc/NetworkGroup`) |
| `is_open_for_posting` | If False, only moderators can post |
| `is_visible` | Soft delete flag |

## Telegram Integration

`rooms/helpers.py` uses `asyncio.run()` + python-telegram-bot v20 to:
- Kick/ban users from room chat (`ban_chat_member`)
- Forward posts/comments to chat

`count_chat_members` management command (scheduled every 6h) updates `Room.members_count` via `bot.get_chat_member_count(chat_id)`.

## Views

- `GET /rooms/` — room directory listing
- `GET /rooms/<slug>/` — room feed (posts filtered by room)
- `POST /rooms/<slug>/join/` — toggle subscription
- `GET /rooms/<slug>/chat/` — redirect to Telegram group (auth-gated)
