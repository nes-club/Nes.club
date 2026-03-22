# notifications — Email & Telegram

Email digests, transactional emails, Telegram notifications, SES webhook handling.

## Email Digests

### Weekly Digest
- Management command: `send_weekly_digest`
- Scheduled: Mondays (via django-q2 Schedule)
- Content: top posts, hot comments, upcoming events, community stats
- Saves result as `Post(type=weekly_digest)` for the homepage
- Sends email to: `is_email_verified=True`, `membership_expires_at >= now()-14d`, not unsubscribed
- Sends Telegram DM to users with `telegram_id` linked
- Sends channel announcement (production only)

### Daily Digest
- Management command: `send_daily_digest`
- Scheduled: every weekday
- Aggregates weekend posts on Tuesday

## Transactional Emails

| Module | Emails |
|--------|--------|
| `email/users.py` | Auth OTP codes, welcome emails |
| `email/badges.py` | Badge received notifications |
| `email/achievements.py` | Achievement unlocked |
| `email/invites.py` | Invite email to new users |

## Telegram Notifications

- `telegram/posts.py` — new post notifications to subscribers and rooms
- `telegram/common.py` — `send_telegram_message()`, `render_html_message()`, Chat/CLUB_CHANNEL helpers
- `telegram/common.py` — shared helpers for all Telegram notifications

## Email Unsubscribe & Bounce Handling

- `GET /notifications/unsubscribe/<user_id>/<secret_code>/` — one-click unsubscribe
- `POST /notifications/webhooks/ses/` — SES bounce/complaint processing
  - Stores `WebhookEvent` and sets `is_email_unsubscribed = True` on complaints

## Models

| Model | Purpose |
|-------|---------|
| `WebhookEvent` | Stores SES bounce/complaint events |

## Digest User Preferences

Controlled by `user.email_digest_type`:
- `nope` — no emails
- `daily` — daily digest
- `weekly` — weekly digest (default)
