# club — Django Project Core

Django project settings, URL routing, middleware, scheduled tasks, and feature flags.

## Key Files

| File | Purpose |
|------|---------|
| `settings.py` | All configuration: DB, cache, apps, email, Telegram |
| `urls.py` | 80+ URL routes for all apps |
| `middleware.py` | Session extraction, `request.me` injection, exception handling |
| `features.py` | Feature flags (`PRIVATE_FEED`, etc.) |
| `context_processors.py` | Inject `settings`, `features`, `me` into all templates |
| `tasks.py` | django-q2 task wrapper functions (14 tasks) |
| `management/commands/setup_schedules.py` | Idempotent Schedule setup |
| `exceptions.py` | `NotFound`, `Forbidden`, `AccessDenied` etc. |

## Scheduled Tasks (`club/tasks.py`)

All tasks call `management.call_command()` internally. Set up via:
```
python manage.py setup_schedules
```

| Task function | Schedule | Command |
|--------------|----------|---------|
| `run_delete_users` | Daily 04:00 | `delete_users` |
| `run_cleanup_oauth_tokens` | Daily 05:00 | `cleanup_oauth_tokens` |
| `run_send_daily_digest` | Daily 08:00 | `send_daily_digest` |
| `run_send_weekly_digest` | Monday 10:00 | `send_weekly_digest` |
| `run_notify_expired_intros` | Daily 12:00 | `notify_expired_intros` |
| `run_send_best_comments` | Daily 19:00 | `send_best_comments` |
| `run_cleanup_post_views` | Daily 01:00 | `cleanup_post_views` |
| `run_rebuild_search_index` | Daily 03:00 | `rebuild_search_index` |
| `run_count_chat_members` | Every 6h | `count_chat_members` |
| `run_replay_stuck_reviews` | Every 30min | `replay_stuck_reviews` |
| `run_replay_pending_moderation` | Every 30min | `replay_pending_moderation` |
| `run_cleanup_gdpr_downloads` | Daily 02:00 | `cleanup_gdpr_downloads` |
| `run_update_hotness` | Every 2h | `update_hotness` |
| `run_promote_old_post` | Daily 11:00 | `promote_old_post` |

## Middleware

`club/middleware.py` runs on every request:
1. Extracts session from cookie → finds `User`
2. Sets `request.me` (User or None)
3. Updates `last_activity_at` (throttled, max once per 5 min)
4. Catches `NotFound`/`Forbidden` → renders 404/403

## Feature Flags (`club/features.py`)

- `PRIVATE_FEED` — hide feed from unauthenticated users; show landing page instead
- Injected into templates via context processor

## Models

`ClubSettings` — key/value store for site-wide configuration (editable in godmode admin). Used for: digest title/intro, feature overrides.
